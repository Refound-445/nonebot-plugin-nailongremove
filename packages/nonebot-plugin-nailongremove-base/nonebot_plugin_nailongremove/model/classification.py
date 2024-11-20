from typing import cast

import cv2
import numpy as np
import torch
from nonebot.utils import run_sync
from torch import Tensor, nn
from torchvision import transforms
from torchvision.models import ResNet

from ..config import DEFAULT_LABEL
from ..frame_source import FrameSource
from .utils.common import CheckResult, CheckSingleResult, race_check
from .utils.update import GitHubRepoModelUpdater

model_path = GitHubRepoModelUpdater(
    "spawner1145",
    "NailongRecognize",
    "main",
    "nailong.pth",
).get()

cuda_available = torch.cuda.is_available()
device = torch.device("cuda" if cuda_available else "cpu")
transform = transforms.Compose([transforms.ToTensor()])
model = cast(ResNet, torch.hub.load("pytorch/vision:v0.10.0", "resnet50", weights=None))
model.fc = nn.Linear(model.fc.in_features, 2)  # 修改最后一层为分类层
model.load_state_dict(
    torch.load(model_path, weights_only=True, map_location=device),
)
model.eval()
if cuda_available:
    model.cuda()

SIZE = 224


@run_sync
def check_single(image: np.ndarray) -> CheckSingleResult[None]:
    if image.shape[0] < SIZE or image.shape[1] < SIZE:
        return CheckSingleResult()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (SIZE, SIZE))
    tensor = cast(Tensor, transform(image))
    tensor = tensor.unsqueeze(0)
    with torch.no_grad():
        output: Tensor = model(tensor.to(device))
        _, pred = torch.max(output, 1)
        return CheckSingleResult(
            label=DEFAULT_LABEL if pred.item() == 1 else None,
            extra=None,
        )


async def check(source: FrameSource) -> CheckResult:
    res = await race_check(check_single, source)
    return CheckResult(label=res.label if res else None)
