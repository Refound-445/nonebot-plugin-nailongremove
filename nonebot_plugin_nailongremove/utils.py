from typing import Callable
from typing_extensions import TypeAlias

import torch
from githubkit import GitHub
from nonebot import logger

from .config import config

ModelVersionGetter: TypeAlias = Callable[[], str]


def get_github():
    return GitHub(config.nailong_github_token)


def format_github_release_download_base_url(owner: str, name: str, tag: str):
    return f"https://github.com/{owner}/{name}/releases/download/{tag}"


def format_github_repo_download_base_url(
    owner: str,
    name: str,
    branch: str,
    folder: str,
):
    return f"https://github.com/{owner}/{name}/raw/refs/heads/{branch}/{folder}".removesuffix(
        "/",
    )


def make_github_repo_sha_getter(
    owner: str,
    repo: str,
    branch: str,
    folder: str,
    filename: str,
):
    def getter() -> str:
        github = get_github()
        ret = github.rest.git.get_tree(owner, repo, f"{branch}:{folder}")
        return next(
            x.sha[:7]
            for x in ret.parsed_data.tree
            if x.path == filename and isinstance(x.sha, str)
        )

    return getter


def make_github_release_update_time_getter(
    owner: str,
    repo: str,
    tag: str,
    filename: str,
):
    def getter() -> str:
        github = get_github()
        ret = github.rest.repos.get_release_by_tag(owner, repo, tag)
        asset = next(x for x in ret.parsed_data.assets if x.name == filename)
        return asset.updated_at.strftime("%Y-%m-%d_%H-%M-%S")

    return getter


def ensure_model(
    model_base_url: str,
    model_filename: str,
    model_version_getter: ModelVersionGetter,
):
    model_path = config.nailong_model_dir / model_filename
    model_version_path = config.nailong_model_dir / f"{model_filename}.ver.txt"

    model_exists = model_path.exists()
    local_ver = (
        model_version_path.read_text(encoding="u8").strip()
        if model_exists and model_version_path.exists()
        else None
    )

    if model_exists and (not config.nailong_auto_update_model):
        return model_path

    def download():
        if not config.nailong_model_dir.exists():
            config.nailong_model_dir.mkdir(parents=True)
        url = f"{model_base_url}/{model_filename}"
        torch.hub.download_url_to_file(url, str(model_path), progress=True)

    try:
        ver = model_version_getter()
    except Exception as e:
        logger.error(
            f"Failed to get model version of {model_filename}: "
            f"{type(e).__name__}: {e}",
        )
        if model_exists:
            logger.exception("Stacktrace")
        else:
            raise
        ver = None

    if ver is None:
        logger.warning("Skip update.")
    elif local_ver != ver:
        local_ver_display = (
            f" from version {local_ver or 'Unknown'}" if model_exists else ""
        )
        logger.info(
            f"Updating model {model_filename}{local_ver_display} to version {ver}",
        )
        download()
        model_version_path.write_text(ver, encoding="u8")

    return model_path


def ensure_model_from_github_release(owner: str, repo: str, tag: str, filename: str):
    return ensure_model(
        format_github_release_download_base_url(owner, repo, tag),
        filename,
        make_github_release_update_time_getter(owner, repo, tag, filename),
    )


def ensure_model_from_github_repo(
    owner: str,
    repo: str,
    branch: str,
    folder: str,
    filename: str,
):
    return ensure_model(
        format_github_repo_download_base_url(owner, repo, branch, folder),
        filename,
        make_github_repo_sha_getter(owner, repo, branch, folder, filename),
    )
