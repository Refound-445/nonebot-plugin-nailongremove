from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class ModelType(int, Enum):
    CLASSIFICATION = 0
    TARGET_DETECTION = 1


class Config(BaseModel):
    nailong_bypass_superuser: bool = True
    nailong_bypass_admin: bool = True
    nailong_need_admin: bool = False
    nailong_list_scenes: List[str] = Field(default_factory=list)
    nailong_blacklist: bool = True
    nailong_priority: int = 100

    nailong_recall: bool = True
    nailong_mute_seconds: int = 0
    nailong_tip: str = "本群禁止发送奶龙！"
    nailong_failed_tip: str = "{:Reply($message_id)}呜，不要发奶龙了嘛 🥺 👉👈"

    nailong_model_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data" / "nailongremove",
    )
    nailong_model: ModelType = ModelType.CLASSIFICATION
    nailong_auto_update_model: bool = True
    nailong_concurrency: int = 1

    nailong_model1_yolox_size: Tuple[int, int] = (416, 416)
    nailong_model1_type: str = "tiny"

    nailong_github_token: Optional[str] = None


config = get_plugin_config(Config)
