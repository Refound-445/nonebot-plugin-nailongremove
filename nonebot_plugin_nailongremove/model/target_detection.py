from typing import TYPE_CHECKING

import numpy as np
import onnxruntime

from ..config import config
from ..utils import ensure_model_from_github_release
from .yolox_utils import demo_postprocess, multiclass_nms, preprocess, vis

if TYPE_CHECKING:
    from . import CheckResult

COCO_CLASSES = ("_background_", "nailong", "anime", "human", "emoji", "long", "other")

model_path = ensure_model_from_github_release(
    "nkxingxh",
    "NailongDetection",
    "v2.3",
    "nailong_v2.3_tiny.onnx",
)

session = onnxruntime.InferenceSession(model_path)
input_shape = config.nailong_yolox_size


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
