from pathlib import Path
from typing import List

from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class Config(BaseModel):
    nailong_model_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data" / "nailongremove",
    )
    nailong_bypass_superuser: bool = True
    nailong_bypass_admin: bool = True
    nailong_need_admin: bool = False
    nailong_list_scenes: List[str] = Field(default_factory=list)
    nailong_blacklist: bool = True
    nailong_recall: bool = True
    nailong_tip: str = "本群禁止发送奶龙！"
    nailong_failed_tip: str = "{:Reply($message_id)}呜，不要发奶龙了嘛 🥺 👉👈"


config = get_plugin_config(Config)
