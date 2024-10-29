from nonebot.utils import run_sync

from ..config import ModelType, config

if config.nailong_model is ModelType.CLASSIFICATION:
    from .classification import check_image as original_check_image

elif config.nailong_model is ModelType.TARGET_DETECTION:
    from .target_detection import check_image as original_check_image

else:
    raise ValueError("Invalid model type")


check_image = run_sync(original_check_image)
