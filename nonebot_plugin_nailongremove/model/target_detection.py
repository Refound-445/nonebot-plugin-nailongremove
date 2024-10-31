from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import onnxruntime
from nonebot import logger
from yarl import URL

from ..config import config
from ..utils import TIME_FORMAT_TEMPLATE, ensure_model, get_github, get_ver_filename
from .yolox_utils import demo_postprocess, multiclass_nms, preprocess, vis

if TYPE_CHECKING:
    from . import CheckResult

COCO_CLASSES = ("_background_", "nailong", "anime", "human", "emoji", "long", "other")


model_filename_sfx = f"_{config.nailong_model1_type}.onnx"


def find_local_model() -> Path:
    local_models = [
        x
        for x in config.nailong_model_dir.iterdir()
        if x.name.endswith(model_filename_sfx)
    ]
    local_models.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    if not local_models:
        raise FileNotFoundError("No local model found")
    p = local_models[0]
    version = (
        vp.read_text("u8")
        if (vp := (p.parent / get_ver_filename(p.name))).exists()
        else "Unknown"
    )
    logger.info(f"Using local cached model: {p.name} (version {version})")
    return p


def get_latest_model() -> Path:
    if not config.nailong_auto_update_model:
        with suppress(FileNotFoundError):
            return find_local_model()

    github = get_github()
    try:
        ret = github.rest.repos.get_latest_release("nkxingxh", "NailongDetection")
        asset = next(
            x for x in ret.parsed_data.assets if x.name.endswith(model_filename_sfx)
        )
        url = URL(asset.browser_download_url)
        version = asset.updated_at.strftime(TIME_FORMAT_TEMPLATE)
        return ensure_model(
            str(url.parent),
            url.name,
            lambda: version,
        )
    except Exception as e:
        logger.warning(f"Failed to get latest model: {type(e).__name__}: {e}")
        logger.opt(exception=e).debug("Stacktrace")
        return find_local_model()


model_path = get_latest_model()

session = onnxruntime.InferenceSession(model_path)
input_shape = config.nailong_model1_yolox_size


def check_image(image: np.ndarray) -> "CheckResult":
    img, ratio = preprocess(image, input_shape)
    ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}
    output = session.run(None, ort_inputs)
    predictions = demo_postprocess(output[0], input_shape)[0]

    boxes = predictions[:, :4]
    scores = predictions[:, 4:5] * predictions[:, 5:]

    boxes_xyxy = np.ones_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.0
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.0
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.0
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.0
    boxes_xyxy /= ratio
    dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.1)
    if dets is not None:
        final_boxes, final_scores, final_cls_inds = (
            dets[:, :4],  # type: ignore
            dets[:, 4],  # type: ignore
            dets[:, 5],  # type: ignore
        )
        for i in range(len(final_scores)):
            if final_cls_inds[i] == 1 and final_scores[i] > 0.5:
                image = vis(
                    image,
                    final_boxes,
                    final_scores,
                    final_cls_inds,
                    conf=0.3,
                    class_names=COCO_CLASSES,
                )
                return True, image
    return False
