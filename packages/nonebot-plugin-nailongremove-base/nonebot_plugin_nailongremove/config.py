from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cookit import StrEnum
from cookit.pyd import field_validator
from nonebot import get_plugin_config
from pydantic import BaseModel, Field

DEFAULT_LABEL = "nailong"


class ModelType(int, Enum):
    CLASSIFICATION = 0
    TARGET_DETECTION = 1
    HF_DETECTION = 2
    HF_YOLO = 3



class Model1Type(StrEnum):
    TINY = auto()
    M = auto()

    @property
    def yolox_size(self) -> Tuple[int, int]:
        return {
            Model1Type.TINY: (416, 416),
            Model1Type.M: (640, 640),
        }[self]


class Config(BaseModel):
    proxy: Optional[str] = None

    nailong_bypass_superuser: bool = False
    nailong_bypass_admin: bool = False
    nailong_need_admin: bool = False
    nailong_list_scenes: List[str] = Field(default_factory=list)
    nailong_blacklist: bool = True
    nailong_user_blacklist: List[str] = Field(default_factory=list)
    nailong_priority: int = 100

    nailong_recall: List[str] = ["nailong"]
    nailong_mute_seconds: Dict[str,int] = {"nailong":0}
    nailong_tip: Dict[str, List[str]] = {
        DEFAULT_LABEL: ["本群禁止发送奶龙！"],
    }
    nailong_failed_tip: Dict[str, List[str]] = {
        DEFAULT_LABEL: ["{:Reply($message_id)}呜，不要发奶龙了嘛 🥺 👉👈"],
    }
    nailong_check_all_frames: bool = False
    nailong_check_rate: float = 0.8

    nailong_model_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data" / "nailongremove",
    )
    nailong_model: ModelType = ModelType.TARGET_DETECTION
    nailong_auto_update_model: bool = True
    nailong_concurrency: int = 1
    nailong_onnx_providers: List[str] = ["CPUExecutionProvider"]

    nailong_model1_type: Model1Type = Model1Type.TINY
    nailong_model1_yolox_size: Optional[Tuple[int, int]] = None
    nailong_model1_score: Dict[str, Optional[float]] = {
        DEFAULT_LABEL: 0.5,
    }
    nailong_model2_online: bool = False
    nailong_check_mode: int = 0
    nailong_similarity_on: bool = False
    nailong_similarity_max_storage: int = 1000
    nailong_hf_token: Optional[str] = None

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
