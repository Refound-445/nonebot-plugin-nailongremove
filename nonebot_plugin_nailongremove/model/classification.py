from typing import TYPE_CHECKING, Any

import cv2
import numpy as np
import torch
from torch import nn
from torchvision import transforms

from ..utils import ensure_model_from_github_repo

if TYPE_CHECKING:
    from . import CheckResult

model_path = ensure_model_from_github_repo(
    "spawner1145",
    "NailongRecognize",
    "main",
    "",
    "nailong.pth",
)

cuda_available = torch.cuda.is_available()
device = torch.device("cuda" if cuda_available else "cpu")
transform = transforms.Compose([transforms.ToTensor()])
model: Any = torch.hub.load("pytorch/vision:v0.10.0", "resnet50", weights=None)
model.fc = nn.Linear(model.fc.in_features, 2)  # 修改最后一层为分类层
model.load_state_dict(
    torch.load(model_path, weights_only=True, map_location=device),
)
model.eval()
if cuda_available:
    model.cuda()


def check_image(image: np.ndarray) -> "CheckResult":
    if image.shape[0] < 224 or image.shape[1] < 224:
        return False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    image = transform(image)
    image = image.unsqueeze(0)  # type: ignore
    with torch.no_grad():
        output = model(image.to(device))  # type: ignore
        _, pred = torch.max(output, 1)
        if pred.item() == 1:
            return True
    return False
