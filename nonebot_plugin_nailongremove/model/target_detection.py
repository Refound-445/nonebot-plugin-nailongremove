from typing import TYPE_CHECKING
from typing_extensions import override

import numpy as np
import onnxruntime

from ..config import config
from .update import GitHubLatestReleaseModelUpdater, ModelInfo
from .yolox_utils import demo_postprocess, multiclass_nms, preprocess, vis

if TYPE_CHECKING:
    from . import CheckResult

model_filename_sfx = f"_{config.nailong_model1_type}.onnx"


class ModelUpdater(GitHubLatestReleaseModelUpdater):
    @override
    def get_info(self) -> ModelInfo[None]:
        info = super().get_info()
        info.filename = f"nailong{model_filename_sfx}"
        return info


model_path = ModelUpdater(
    "nkxingxh",
    "NailongDetection",
    lambda x: x.endswith(model_filename_sfx),
).get()

labels_path = GitHubLatestReleaseModelUpdater(
    "nkxingxh",
    "NailongDetection",
    lambda x: x == "labels.txt",
).get()
labels = labels_path.read_text("u8").splitlines()

session = onnxruntime.InferenceSession(
    model_path,
    providers=(
        [
            "TensorrtExecutionProvider",
            "CUDAExecutionProvider",
            "CPUExecutionProvider",
        ]
        if config.nailong_onnx_try_to_use_gpu
        else ["CPUExecutionProvider"]
    ),
)
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
    if dets is None:
        return False

    final_boxes, final_scores, final_cls_inds = (
        dets[:, :4],  # type: ignore
        dets[:, 4],  # type: ignore
        dets[:, 5],  # type: ignore
    )
    has = any(
        True
        for c, s in zip(final_cls_inds, final_scores)
        if c == 1 and s >= config.nailong_model1_score
    )
    if has:
        image = vis(
            image,
            final_boxes,
            final_scores,
            final_cls_inds,
            conf=0.3,
            class_names=labels,
        )
        return True, image
    return False
