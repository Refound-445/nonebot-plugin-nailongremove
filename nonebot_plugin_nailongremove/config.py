from pathlib import Path
from typing import List

from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class Config(BaseModel):
    nailong_model_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data" / "nailongremove",
    )
    nailong_list_scenes: List[str] = Field(default_factory=list)
    nailong_blacklist: bool = True


config = get_plugin_config(Config)
