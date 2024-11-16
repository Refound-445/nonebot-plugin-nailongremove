import asyncio
import datetime
import glob
import os
import random
import shutil
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, TypeVar
import itertools
import cv2
import torch
from PIL import Image
from typing_extensions import TypeAlias
import torch.nn.functional as F

import numpy as np

from ...config import config
from ...frame_source import FrameSource

T = TypeVar("T")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class CheckSingleResult(Generic[T]):
    ok: bool
    label: Optional[str]
    extra: T

    @classmethod
    def not_ok(cls, extra: T):
        return cls(ok=False, label=None, extra=extra)


@dataclass
class CheckResult:
    ok: bool
    label: Optional[str]
    extra_vars: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def not_ok(cls):
        return cls(ok=False, label=None, extra_vars={})


FrameChecker: TypeAlias = Callable[[[np.ndarray], bool], Awaitable[CheckSingleResult[T]]]


async def race_check(
        checker: FrameChecker[T],
        frames: FrameSource,
        concurrency: int = config.nailong_concurrency,
) -> Optional[CheckSingleResult[T]]:
    iterator = iter(frames)
    if config.nailong_similarity_on:
        temp_frames = itertools.tee(frames, 1)[0]

    async def worker() -> CheckSingleResult:
        if config.nailong_similarity_on:
            while True:
                try:
                    frame = next(temp_frames)
                except StopIteration:
                    break
                res = await checker(frame, True)
                if res.ok:
                    return res
        while True:
            try:
                frame = next(iterator)
            except StopIteration:
                return CheckSingleResult.not_ok(None)
            res = await checker(frame, False)
            if res.ok:
                return res

    if config.nailong_check_mode == 0:
        tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
        while True:
            if not tasks:
                break
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                if (res := t.result()).ok:
                    for pt in pending:
                        pt.cancel()
                    return res
            tasks = pending
    elif config.nailong_check_mode == 1:
        frame = next(iterator)
        if config.nailong_similarity_on:
            res = await checker(frame, True)
            if res.ok:
                return res
        res = await checker(frame, False)
        if res.ok:
            return res
    elif config.nailong_check_mode == 2:
        records = []
        while True:
            try:
                frame = next(iterator)
                records.append(frame)
            except StopIteration:
                break
        frame = records[random.randint(0, len(records) - 1)]
        if config.nailong_similarity_on:
            res = await checker(frame, True)
            if res.ok:
                return res
        res = await checker(frame, False)
        if res.ok:
            return res
    return None

def similarity_process(image1: np.ndarray, dsize) -> Optional[CheckSingleResult]:
    path = list(glob.glob(os.path.join(config.nailong_model_dir, 'records/*/*.jpg')))
    if len(path) == 0:
        return None
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
    image1 = cv2.resize(image1, dsize, interpolation=cv2.INTER_LINEAR)
    image1_tensor = torch.tensor(image1, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
    image1_tensor = image1_tensor.reshape(1, -1).to(device)
    for i in range(0, len(path), config.nailong_similarity_max_batch_size):
        temp_paths = path[i:(
            i + config.nailong_similarity_max_batch_size if i + config.nailong_similarity_max_batch_size < len(
                path) else len(path))]
        image2s = []
        for image_path in temp_paths:
            image2 = cv2.imread(image_path)
            image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
            image2 = cv2.resize(image2, dsize, interpolation=cv2.INTER_LINEAR)
            image2s.append(image2)
        image2_tensor = torch.tensor(np.array(image2s), dtype=torch.float32).permute(0, 3, 1, 2)
        image2_tensor = image2_tensor.reshape(image2_tensor.shape[0], -1).to(device)
        similarities = F.cosine_similarity(image1_tensor, image2_tensor)
        indices = torch.nonzero(similarities > 0.99)
        index = indices[0].item() if indices.numel() > 0 else None
        if index is not None:
            image_path = path[index]
            label = os.path.split(image_path)[-2].split('\\')[-1]
            return CheckSingleResult(ok=True, label=label, extra=None)
    return None


def process_gif_and_save_jpgs(frames, label, dsize, similarity_threshold=0.85):
    if len(list(glob.glob(
            os.path.join(str(config.nailong_model_dir), 'records/*/*.jpg')))) >= config.nailong_similarity_max_storage:
        zip_filename = shutil.make_archive(os.path.join(str(config.nailong_model_dir), '{}_records'.format(
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))), 'zip',
                                           os.path.join(str(config.nailong_model_dir), 'records'))
        shutil.rmtree(os.path.join(str(config.nailong_model_dir), 'records'))
    else:
        zip_filename = None
    output_dir = os.path.join(str(config.nailong_model_dir), 'records', label)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    frame_count = [i for i in range(len(frames))]
    while len(frame_count) > 0:
        frame_num1 = frame_count[0]
        frame_count.remove(frame_num1)
        frame1 = frames[frame_num1]
        frame_filename = os.path.join(output_dir, "frame{}_{}.jpg".format(frame_num1,
                                                                          datetime.datetime.now().strftime(
                                                                              "%Y-%m-%d_%H-%M-%S")))
        while os.path.exists(frame_filename):
            frame_filename = "exist-" + frame_filename
        cv2.imwrite(frame_filename, frame1)
        # frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        frame1 = cv2.resize(frame1, dsize)
        image1_tensor = torch.tensor(frame1, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        image1_tensor = image1_tensor.reshape(1, -1).to(device)
        max_length = len(list(frame_count))
        indexs = []
        for i in range(0, max_length, config.nailong_similarity_max_batch_size):
            frame2_num = frame_count[i:(
                i + config.nailong_similarity_max_batch_size if i + config.nailong_similarity_max_batch_size < max_length else max_length)]
            frame2 = [frames[i] for i in frame2_num]
            # frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            frame2 = [cv2.resize(t, dsize) for t in frame2]
            image2_tensor = torch.tensor(np.array(frame2), dtype=torch.float32).permute(0, 3, 1, 2)
            image2_tensor = image2_tensor.reshape(image2_tensor.shape[0], -1).to(device)
            similarities = F.cosine_similarity(image1_tensor, image2_tensor)
            indices = torch.nonzero(similarities > similarity_threshold)
            index = indices.squeeze().tolist() if indices.numel() > 0 else None
            if type(index) is int:
                index=[index]
            if index is not None:
                indexs.extend([frame2_num[i] for i in index])
        frame_count = [i for i in frame_count if i not in indexs]
    return zip_filename
