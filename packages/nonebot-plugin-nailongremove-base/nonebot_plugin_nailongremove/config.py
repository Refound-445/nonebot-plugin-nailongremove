from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cookit.pyd import field_validator
from nonebot import get_plugin_config
from pydantic import BaseModel, Field

DEFAULT_LABEL = "nailong"


class ModelType(int, Enum):
    CLASSIFICATION = 0
    TARGET_DETECTION = 1


MODEL1_YOLOX_SIZE_MAP = {
    "tiny": (416, 416),
    "m": (640, 640),
    "m_beta": (640, 640),
}
MODEL1_DEFAULT_TYPE = "tiny"


class Config(BaseModel):
    proxy: Optional[str] = None

    nailong_bypass_superuser: bool = True
    nailong_bypass_admin: bool = True
    nailong_need_admin: bool = False
    nailong_list_scenes: List[str] = Field(default_factory=list)
    nailong_blacklist: bool = True
    nailong_user_blacklist: List[str] = Field(default_factory=list)
    nailong_priority: int = 100

    nailong_recall: bool = True
    nailong_mute_seconds: int = 0
    nailong_tip: Dict[str, str] = {
        DEFAULT_LABEL: "本群禁止发送奶龙！",
    }
    nailong_failed_tip: Dict[str, str] = {
        DEFAULT_LABEL: "{:Reply($message_id)}呜，不要发奶龙了嘛 🥺 👉👈",
    }
    nailong_check_all_frames: bool = False

    nailong_model_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data" / "nailongremove",
    )
    nailong_model: ModelType = ModelType.TARGET_DETECTION
    nailong_auto_update_model: bool = True
    nailong_concurrency: int = 1
    nailong_onnx_providers: List[str] = ["CPUExecutionProvider"]

    nailong_model1_type: str = MODEL1_DEFAULT_TYPE
    nailong_model1_yolox_size: Optional[Tuple[int, int]] = None
    nailong_model1_score: Dict[str, Optional[float]] = {
        DEFAULT_LABEL: 0.5,
    }

    nailong_github_token: Optional[str] = None

    @field_validator(
        "nailong_tip",
        "nailong_failed_tip",
        "nailong_model1_score",
        mode="before",
    )
    def transform_to_dict(cls, v: Any):  # noqa: N805
        return v if isinstance(v, dict) else {DEFAULT_LABEL: v}

    @field_validator(
        "nailong_tip",
        "nailong_failed_tip",
        # "nailong_model1_score",
        mode="after",
    )
    def check_default_label_exists(cls, v: Dict[str, Any]):  # noqa: N805
        if DEFAULT_LABEL not in v:
            raise ValueError(f"Please ensure default label {DEFAULT_LABEL} in dict")
        return v

    @field_validator("nailong_onnx_providers", mode="before")
    def transform_to_list(cls, v: Any):  # noqa: N805
        return v if isinstance(v, list) else [v]

    @field_validator("nailong_onnx_providers", mode="after")
    def validate_provider_available(cls, v: Any):  # noqa: N805
        try:
            from onnxruntime.capi import _pybind_state as c
        except ImportError:
            pass
        else:
            available_providers: List[str] = c.get_available_providers()  # type: ignore
            if any(p not in available_providers for p in v):
                raise ValueError(f"Provider {v} not available in onnxruntime")
        return v


config = get_plugin_config(Config)
