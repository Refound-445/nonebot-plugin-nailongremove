from typing import Awaitable, Callable, NoReturn

from ..config import ModelType, config
from ..frame_source import FrameSource
from .utils.common import CheckResult as CheckResult


def raise_extra_import_error(e: BaseException, group: str) -> NoReturn:
    raise ImportError(
        f"Possibly missing required libraries, "
        f"Please run `pip install nonebot-plugin-nailongremove[{group}]` "
        f"in your project's environment to install.",
    ) from e


check: Callable[[FrameSource], Awaitable[CheckResult]]

if config.nailong_model is ModelType.CLASSIFICATION:
    from .classification import check as check

elif config.nailong_model is ModelType.TARGET_DETECTION:
    try:
        from .target_detection import check as check
    except ImportError as e:
        raise_extra_import_error(e, "model1")

else:
    raise ValueError("Invalid model type")
