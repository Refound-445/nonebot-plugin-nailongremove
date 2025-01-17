import asyncio
from dataclasses import dataclass
from typing import Optional
from typing_extensions import override

import numpy as np

# import torch before onnxruntime
import torch as torch  # isort: skip
import onnxruntime  # isort: skip
import itertools

from cookit import with_semaphore
from nonebot.utils import run_sync

from ..config import config
from ..frame_source import FrameSource, repack_save
from .utils.common import CheckResult, CheckSingleResult, race_check, similarity_process
from .utils.update import GitHubLatestReleaseModelUpdater, ModelInfo, UpdaterGroup
from .utils.yolox import demo_postprocess, multiclass_nms, preprocess, vis

model_filename_sfx = f"_{config.nailong_model1_type.value}.onnx"


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
    providers=config.nailong_onnx_providers,
)
input_shape = config.nailong_model1_yolox_size or config.nailong_model1_type.yolox_size


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
def _check_single(
        frame: np.ndarray,
        is_gif: bool = False,
) -> CheckSingleResult[Optional[Detections]]:
    if is_gif:
        res = similarity_process(frame)
        if res is not None:
            return res
        return CheckSingleResult.not_ok(None)
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
        return CheckSingleResult.not_ok(None)

    final_boxes, final_scores, final_cls_ids = (
        dets[:, :4],  # type: ignore
        dets[:, 4],  # type: ignore
        dets[:, 5],  # type: ignore
    )
    for c, s in zip(final_cls_ids, final_scores):
        label = labels[int(c)]
        expected = config.nailong_model1_score.get(label)
        if (expected is not None) and s >= expected:
            return CheckSingleResult(
                ok=True,
                label=label,
                extra=Detections(final_boxes, final_scores, final_cls_ids),
            )
    return CheckSingleResult.not_ok(None)


async def check_single(
        frame: np.ndarray,
        is_gif: bool = False,
) -> CheckSingleResult[FrameInfo]:
    if is_gif:
        res = await _check_single(frame, True)
        return CheckSingleResult(
            ok=res.ok,
            label=res.label,
            extra=FrameInfo(frame, res.extra),
        )
    res = await _check_single(frame)
    return CheckSingleResult(
        ok=res.ok,
        label=res.label,
        extra=FrameInfo(frame, res.extra),
    )


async def check(source: FrameSource) -> CheckResult:
    label = None
    extra_vars = {}
    if config.nailong_check_all_frames and config.nailong_check_mode == 0:
        if config.nailong_similarity_on:
            tem_source = itertools.tee(source, 1)[0]
            sem = asyncio.Semaphore(config.nailong_concurrency)
            results = await asyncio.gather(
                *(
                    with_semaphore(sem)(check_single)(frame, True)
                    for frame in tem_source
                ),
            )
            ok = True if sum(1 for r in results if r.ok) / len(results) >= config.nailong_check_rate else False
        else:
            ok = False
        if not ok:
            sem = asyncio.Semaphore(config.nailong_concurrency)
            results = await asyncio.gather(
                *(with_semaphore(sem)(check_single)(frame) for frame in source),
            )
            ok = True if sum(1 for r in results if r.ok) / len(results) >= config.nailong_check_rate else False
        if ok:
            all_labels = {r.label for r in results if r.label}
            label = next(
                (x for x in config.nailong_model1_score if x in all_labels),
                None,
            )
            extra_vars["$checked_result"] = await repack_save(
                source,
                (r.extra.vis() for r in results),
            )
    else:
        res = await race_check(check_single, source)
        ok = bool(res)
        if res:
            label = res.label
            extra_vars["$checked_result"] = await repack_save(
                source,
                iter((res.extra.vis(),)),
            )
    return CheckResult(ok, label, extra_vars)
