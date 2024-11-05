import asyncio
from dataclasses import dataclass
from typing import Optional
from typing_extensions import override

import numpy as np
import onnxruntime
from cookit import with_semaphore
from nonebot.utils import run_sync

from ..config import config
from ..frame_source import FrameSource, repack_save
from .common import CheckResult, CheckSingleResult, race_check
from .update import GitHubLatestReleaseModelUpdater, ModelInfo, UpdaterGroup
from .yolox_utils import demo_postprocess, multiclass_nms, preprocess, vis

model_filename_sfx = f"_{config.nailong_model1_type}.onnx"


class ModelUpdater(GitHubLatestReleaseModelUpdater):
    @override
    def get_info(self) -> ModelInfo[None]:
        info = super().get_info()
        info.filename = f"nailong{model_filename_sfx}"
        return info


OWNER = "nkxingxh"
REPO = "NailongDetection"

model_path, labels_path = UpdaterGroup(
    ModelUpdater(
        OWNER,
        REPO,
        lambda x: x.endswith(model_filename_sfx),
    ),
    GitHubLatestReleaseModelUpdater(
        OWNER,
        REPO,
        lambda x: x == "labels.txt",
    ),
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


@dataclass
class Detections:
    boxes: np.ndarray
    scores: np.ndarray
    ids: np.ndarray


@dataclass
class FrameInfo:
    frame: np.ndarray
    detections: Optional[Detections] = None

    def vis(self) -> np.ndarray:
        return (
            vis(
                self.frame,
                self.detections.boxes,
                self.detections.scores,
                self.detections.ids,
                conf=0.3,
                class_names=labels,
            )
            if self.detections
            else self.frame
        )


@run_sync
def _check_single(frame: np.ndarray) -> CheckSingleResult[Optional[Detections]]:
    img, ratio = preprocess(frame, input_shape)
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
        return CheckSingleResult(ok=False, extra=None)

    final_boxes, final_scores, final_cls_ids = (
        dets[:, :4],  # type: ignore
        dets[:, 4],  # type: ignore
        dets[:, 5],  # type: ignore
    )
    has = any(
        True
        for c, s in zip(final_cls_ids, final_scores)
        if labels[int(c)] == "nailong" and s >= config.nailong_model1_score
    )
    if has:
        return CheckSingleResult(
            ok=True,
            extra=Detections(final_boxes, final_scores, final_cls_ids),
        )
    return CheckSingleResult(ok=False, extra=None)


async def check_single(frame: np.ndarray) -> CheckSingleResult[FrameInfo]:
    res = await _check_single(frame)
    return CheckSingleResult(ok=res.ok, extra=FrameInfo(frame, res.extra))


async def check(frames: FrameSource) -> CheckResult:
    extra_vars = {}
    if config.nailong_checked_result_all:
        sem = asyncio.Semaphore(config.nailong_concurrency)
        results = asyncio.gather(
            *(with_semaphore(sem)(check_single)(frame) for frame in frames),
        )
        ok = any(r.ok for r in results)
        if ok:
            extra_vars["$checked_result"] = await repack_save(
                frames,
                (r.extra.vis() for r in results),
            )
    else:
        res = await race_check(check_single, frames)
        ok = bool(res)
        if res:
            extra_vars["$checked_result"] = await repack_save(
                frames,
                iter((res.extra.vis(),)),
            )
    return CheckResult(ok, extra_vars)
