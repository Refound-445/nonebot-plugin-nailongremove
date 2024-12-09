import asyncio
import datetime
import glob
import itertools
import os
import random
import shutil
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, TypeVar
from typing_extensions import TypeAlias

import cv2
import numpy as np
import torch

from ...config import config
from ...frame_source import FrameSource

T = TypeVar("T")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if config.nailong_similarity_on:
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    import json

    import faiss
    import torchvision
    from huggingface_hub import PyTorchModelHubMixin
    from nonebot import logger
    from torch import nn
    from torchvision import transforms
    import sklearn
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.5],
                std=[0.5],
            ),  # Assuming grayscale or single-channel
        ],
    )

    class MyModel(
        nn.Module,
        PyTorchModelHubMixin,
    ):
        def __init__(self):
            super().__init__()
            self.resnet = torchvision.models.resnet18(weights=None)
            self.resnet.fc = nn.Linear(
                self.resnet.fc.in_features,
                5,
            )  # Output dimension is 5

        def forward(self, x):
            return self.resnet(x)

    features_model = MyModel.from_pretrained(
        "refoundd/NailongFeatures",cache_dir=config.nailong_model_dir
    ).to(device)
    index_path = config.nailong_model_dir / "records.index"
    json_path = config.nailong_model_dir / "records.json"
    if os.path.exists(index_path):
        index = faiss.read_index(str(index_path))
    else:
        index = faiss.IndexFlatL2(512)
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            index_cls = json.load(f)
    else:
        index_cls = {}
    if torch.cuda.is_available():
        try:
            res = faiss.StandardGpuResources()  # 创建GPU资源
            index = faiss.index_cpu_to_gpu(res, 0, index)  # 将CPU索引转移到GPU
        except Exception:
            logger.warning(
                "load faiss-gpu failed.Please check your GPU device and install faiss-gpu first.",
            )

    def hook(model, input, output):
        embeddings = input[0]
        vector = embeddings.detach().cpu().numpy().astype(np.float32)
        faiss.normalize_L2(vector)
        global index
        d, i = index.search(vector, 1)
        return 1 - d[0][0], i[0][0], vector

    features_model.resnet.fc.register_forward_hook(hook)
    features_model.eval()


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


FrameChecker: TypeAlias = Callable[
    [[np.ndarray], bool],
    Awaitable[CheckSingleResult[T]],
]


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
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
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


def similarity_process(
    image1: np.ndarray,
    dsize=(224, 224),
    similarity_threshold=1,
) -> Optional[CheckSingleResult]:
    # image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
    image1 = cv2.resize(image1, dsize, interpolation=cv2.INTER_LINEAR)
    image1_tensor = transform(image1).unsqueeze(0).to(device)
    # image1_tensor = (
    #     torch.tensor(image1, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
    # ).to(device)
    distance, indice, _ = features_model(image1_tensor)
    if distance >= similarity_threshold:
        label = index_cls[str(indice)]
        return CheckSingleResult(ok=True, label=label, extra=None)
    return None


def process_gif_and_save_jpgs(frames, label, dsize=(224, 224), similarity_threshold=1):
    if (
        len(
            list(
                glob.glob(str(config.nailong_model_dir / "records/*/*.jpg")),
            ),
        )
        >= config.nailong_similarity_max_storage
        and config.nailong_hf_token is not None
    ):
        zip_filename = shutil.make_archive(
            config.nailong_model_dir
            / "{}_records".format(
                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            ),
            "zip",
            config.nailong_model_dir / "records",
        )
        shutil.rmtree(config.nailong_model_dir / "records")
        from huggingface_hub import HfApi

        api = HfApi()
        commitInfo = api.upload_file(
            path_or_fileobj=zip_filename,
            path_in_repo="new_dataset.zip",
            repo_id="refoundd/NailongClassification",
            repo_type="dataset",
            create_pr=True,
            token=config.nailong_hf_token,
        )
        # os.remove(zip_filename)
    else:
        commitInfo = None
    output_dir = config.nailong_model_dir / "records" / label
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    count = 0
    for frame in frames:
        frame_filename = os.path.join(
            output_dir,
            "frame{}_{}.jpg".format(
                count,
                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            ),
        )
        while os.path.exists(frame_filename):
            frame_filename = "exist-" + frame_filename
        cv2.imwrite(frame_filename, frame)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, dsize, interpolation=cv2.INTER_LINEAR)
        image1_tensor = transform(frame).unsqueeze(0).to(device)
        # image1_tensor = (
        #     torch.tensor(frame, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        # ).to(device)
        d, i, features = features_model(image1_tensor)
        if d >= similarity_threshold:
            index_cls[str(i)] = label
        else:
            index.add(features)
            index_cls[str(index.ntotal - 1)] = label
        count += 1
    faiss.write_index(index, str(index_path))
    with open(json_path, "w") as f:
        json.dump(index_cls, f)
    return commitInfo
