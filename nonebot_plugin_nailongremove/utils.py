import httpx
import torch
from nonebot import logger

from .config import MODEL_BASE_URL, config


def ensure_model(model_filename: str):
    model_version_filename = f"{model_filename}.ver.txt"
    model_path = config.nailong_model_dir / model_filename
    model_version_path = config.nailong_model_dir / model_version_filename

    def download():
        url = f"{MODEL_BASE_URL}/{model_filename}"
        torch.hub.download_url_to_file(url, model_filename, progress=True)

    def get_model_version():
        url = f"{MODEL_BASE_URL}/{model_version_filename}"
        return httpx.get(url).raise_for_status().text.strip()

    try:
        ver = get_model_version()
    except Exception:
        logger.error(f"Failed to get model version of {model_filename}")
        raise

    local_ver = (
        model_version_path.read_text(encoding="u8").strip()
        if model_version_path.exists()
        else None
    )
    if (not model_path.exists()) or (ver != local_ver):
        logger.info(
            f"Updating model {model_filename} "
            f"from version {local_ver or 'Unknown'} to version {ver}",
        )
        if (not model_version_path.exists()) or (
            ver != model_version_path.read_text().strip()
        ):
            download()
            model_version_path.write_text(ver, encoding="u8")

    return model_path
