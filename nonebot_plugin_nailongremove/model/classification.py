from typing import Any

import cv2
import numpy as np
import torch
from torch import nn
from torchvision import transforms

from ..utils import ensure_model

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
transform = transforms.Compose([transforms.ToTensor()])

MODEL_URL_DEFAULT = "https://github.com/spawner1145/NailongRecognize/raw/refs/heads/main/nailong.pth"
model_path = ensure_model("nailong.pth")

model: Any = torch.hub.load("pytorch/vision:v0.10.0", "resnet50", weights=None)
model.fc = nn.Linear(model.fc.in_features, 2)  # 修改最后一层为分类层
model.load_state_dict(
    torch.load(model_path, weights_only=True, map_location=device),
)
model.eval()


def check_image(image: np.ndarray) -> bool:
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
