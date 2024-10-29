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
        torch.hub.download_url_to_file(url, str(model_path), progress=True)

    def get_model_version():
        url = f"{MODEL_BASE_URL}/{model_version_filename}"
        return httpx.get(url, follow_redirects=True).raise_for_status().text.strip()

    try:
        ver = get_model_version()
    except Exception:
        logger.warning(f"Failed to get model version of {model_filename}")
        logger.exception("Stacktrace")
        ver = None

    local_ver = (
        model_version_path.read_text(encoding="u8").strip()
        if model_version_path.exists()
        else None
    )
    model_exists = model_path.exists()

    if model_exists and (ver is None):
        logger.warning("Skip update.")
        return model_path

    if (not model_exists) or local_ver != ver:
        logger.info(
            f"Updating model {model_filename} "
            f"from version {local_ver or 'Unknown'} to version {ver or 'Unknown'}",
        )
        download()
        if ver:
            model_version_path.write_text(ver, encoding="u8")

    return model_path
