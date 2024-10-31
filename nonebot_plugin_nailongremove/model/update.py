from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, Optional, TypeVar
from typing_extensions import override

import httpx
from githubkit import GitHub
from nonebot import logger
from tqdm import tqdm

from ..config import config

T = TypeVar("T")

TIME_FORMAT_TEMPLATE = "%Y-%m-%d_%H-%M-%S"


class ProxyGitHub(GitHub):
    @override
    def _get_client_defaults(self):
        return {**super()._get_client_defaults(), "proxy": config.proxy}


def get_github():
    return ProxyGitHub(config.nailong_github_token, auto_retry=False)


def get_ver_filename(filename: str) -> str:
    return f"{filename}.ver.txt"


def get_ver_path(filename: str) -> Path:
    return config.nailong_model_dir / get_ver_filename(filename)


def progress_download(resp: httpx.Response, file_path: Path):
    if not (file_dir := file_path.parent).exists():
        file_dir.mkdir(parents=True)
    prog = tqdm(unit="B", unit_scale=True, unit_divisor=1024)
    with file_path.open("wb") as f, prog:  # fmt: skip
        for b in resp.iter_bytes():
            if (prog.total is None) and (c_len := resp.headers.get("Content-Length")):
                prog.total = int(c_len)
            prog.update(len(b))
            f.write(b)


def httpx_progress_download(file_path: Path, *args, **kwargs):
    with httpx.stream(*args, **kwargs) as resp:
        return progress_download(resp.raise_for_status(), file_path)


def github_progress_download(github: GitHub, file_path: Path, *args, **kwargs):
    with github.get_sync_client() as cli, cli.stream(*args, **kwargs) as resp:
        return progress_download(resp.raise_for_status(), file_path)


@dataclass
class ModelInfo(Generic[T]):
    download_url: str
    filename: str
    version: str
    extra: T


class ModelUpdater(ABC):
    @abstractmethod
    def find_from_local(self) -> Optional[Path]: ...

    @abstractmethod
    def get_info(self) -> ModelInfo: ...

    def check_local_ver(self, info: ModelInfo) -> Optional[str]:
        if (config.nailong_model_dir / info.filename).exists() and (
            ver_path := get_ver_path(info.filename)
        ).exists():
            return ver_path.read_text(encoding="u8").strip()
        return None

    def save_local_ver(self, info: ModelInfo, clear: bool = False):
        p = get_ver_path(info.filename)
        if clear:
            p.unlink(missing_ok=True)
        else:
            p.write_text(info.version, encoding="u8")

    def _download(self, tmp_path: Path, info: ModelInfo):
        httpx_progress_download(
            tmp_path,
            "GET",
            info.download_url,
            proxy=config.proxy,
            follow_redirects=True,
        )

    def download(self, info: ModelInfo):
        tmp_path = config.nailong_model_dir / f"{info.filename}.{info.version}"
        try:
            self._download(tmp_path, info)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise
        else:
            tmp_path.rename(config.nailong_model_dir / info.filename)

    def validate(self, path: Path, info: ModelInfo) -> Any:  # noqa: ARG002
        """please raise Error when validation failed"""
        return

    def validate_with_unlink(self, path: Path, info: ModelInfo) -> Any:
        try:
            return self.validate(path, info)
        except Exception:
            path.unlink(missing_ok=True)
            self.save_local_ver(info, clear=True)
            raise

    def _get(self) -> Path:
        if (not config.nailong_auto_update_model) and (local := self.find_from_local()):
            return local

        try:
            info = self.get_info()
        except Exception as e:
            if not (local := self.find_from_local()):
                raise
            logger.error(
                f"Failed to get model info for {type(self).__name__}, skipping update: "
                f"{type(e).__name__}: {e}",
            )
            logger.debug("Stacktrace")
            return local

        model_path = config.nailong_model_dir / info.filename
        local_ver = self.check_local_ver(info)

        if model_path.exists():
            try:
                self.validate_with_unlink(model_path, info)
            except Exception as e:
                logger.error(
                    f"Validation for model {info.filename} failed, re-downloading: "
                    f"{type(e).__name__}: {e}",
                )

        if (not model_path.exists()) or (local_ver != info.version):
            from_tip = f"from version {local_ver or 'Unknown'} " if local_ver else ""
            logger.info(
                f"Updating model {info.filename} {from_tip}to version {info.version}",
            )
            self.download(info)
            self.save_local_ver(info)
            self.validate_with_unlink(model_path, info)

        return model_path

    def get(self):
        p = self._get()
        logger.info(f"Using model {p.name}")
        return p


class GitHubModelUpdater(ModelUpdater):
    def __init__(self) -> None:
        super().__init__()
        self.github = get_github()


class GitHubDownloadModelUpdater(GitHubModelUpdater):
    @override
    def _download(self, tmp_path: Path, info: ModelInfo):
        github_progress_download(
            self.github,
            tmp_path,
            "GET",
            info.download_url,
            follow_redirects=True,
        )


class GitHubRepoModelUpdater(GitHubModelUpdater):
    def __init__(self, owner: str, repo: str, branch: str, path: str) -> None:
        super().__init__()
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.path = path

        p = self.path.rsplit("/", 1)
        self.folder = p[0] if len(p) > 1 else ""
        self.filename = p[-1]

    def format_download_url(self) -> str:
        folder = f"{self.folder}/" if self.folder else ""
        return (
            f"https://github.com/{self.owner}/{self.repo}"
            f"/raw/refs/heads/{self.branch}/{folder}{self.filename}"
        )

    @override
    def find_from_local(self) -> Optional[Path]:
        if (p := (config.nailong_model_dir / self.filename)).exists():
            return p
        return None

    @override
    def get_info(self) -> ModelInfo[None]:
        ret = self.github.rest.git.get_tree(
            self.owner,
            self.repo,
            f"{self.branch}:{self.folder}",
        )
        it = next(
            x
            for x in ret.parsed_data.tree
            if x.path == self.filename and isinstance(x.sha, str)
        )
        assert it.sha
        return ModelInfo(
            self.format_download_url(),
            self.filename,
            it.sha[:7],
            None,
        )


class GitHubLatestReleaseModelUpdater(GitHubModelUpdater):
    def __init__(
        self,
        owner: str,
        repo: str,
        filename_checker: Optional[Callable[[str], bool]] = None,
    ) -> None:
        super().__init__()
        self.owner = owner
        self.repo = repo
        self.filename_checker = filename_checker or (lambda _: True)

    def format_download_url(self, tag: str, filename: str) -> str:
        return (
            f"https://github.com/{self.owner}/{self.repo}/"
            f"releases/download/{tag}/{filename}"
        )

    @override
    def find_from_local(self) -> Optional[Path]:
        fs = [
            x
            for x in config.nailong_model_dir.iterdir()
            if x.is_file() and self.filename_checker(x.name)
        ]
        if fs:
            fs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return fs[0]
        return None

    @override
    def get_info(self) -> ModelInfo[None]:
        ret = self.github.rest.repos.get_latest_release(self.owner, self.repo)
        asset = next(x for x in ret.parsed_data.assets if self.filename_checker(x.name))
        return ModelInfo(
            self.format_download_url(ret.parsed_data.tag_name, asset.name),
            asset.name,
            asset.updated_at.strftime(TIME_FORMAT_TEMPLATE),
            None,
        )
