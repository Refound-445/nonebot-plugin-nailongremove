from typing import Awaitable, Callable

from ..config import ModelType, config
from ..frame_source import FrameSource
from .utils.common import CheckResult as CheckResult

check: Callable[[FrameSource], Awaitable[CheckResult]]

if config.nailong_model is ModelType.CLASSIFICATION:
    from .classification import check as check

elif config.nailong_model is ModelType.TARGET_DETECTION:
    from .target_detection import check as check

else:
    raise NotImplementedError  # never reach here
