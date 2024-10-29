import torch

from .config import MODEL_BASE_URL, config


def ensure_model(model_filename: str):
    model_path = config.nailong_model_dir / model_filename
    if not model_path.exists():
        url = f"{MODEL_BASE_URL}/{model_filename}"
        torch.hub.download_url_to_file(url, model_filename, progress=True)
    return model_path
