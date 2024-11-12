import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, List, Optional, TypeVar, Union
from typing_extensions import override

import httpx
from githubkit import GitHub
from nonebot import logger
from tqdm import tqdm

from ...config import config

T = TypeVar("T")

TIME_FORMAT_TEMPLATE = "%Y-%m-%d_%H-%M-%S"


class ProxyGitHub(GitHub):
    @override
    def _get_client_defaults(self):
        return {**super()._get_client_defaults(), "proxy": config.proxy}


def get_github():
    return ProxyGitHub(config.nailong_github_token, auto_retry=False)


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


def create_parent_dir(path: Path, create: bool = True):
    if create and (not (p := path.parent).exists()):
        p.mkdir(parents=True)
    return path


def find_file(
    path: Path,
    checker: Union[Callable[[Path], bool], str, None] = None,
    recursive: bool = False,
    last_modified: bool = True,
) -> Optional[Path]:
    if isinstance(checker, str) and checker:
        if (p := path / checker).exists():
            return p
        if not recursive:
            return None

    checker = (
        (checker if callable(checker) else (lambda x: x.name == checker))
        if checker
        else None
    )

    def iterator(p: Path):
        child_dirs: List[Path] = []
        for x in p.iterdir():
            if x.is_dir() and recursive:
                child_dirs.append(x)
            elif x.is_file() and ((not checker) or checker(x)):
                yield x
        for ch in child_dirs:
            yield from iterator(ch)

    it = iterator(path)
    if last_modified:
        return max(it, key=lambda x: x.stat().st_mtime, default=None)
    return next(it, None)


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

    @property
    def root_dir(self) -> Path:
        return config.nailong_model_dir

    def get_path(self, filename: str, create_parent: bool = True) -> Path:
        return create_parent_dir(self.root_dir / filename, create_parent)

    def get_ver_path(self, filename: str, create_parent: bool = True) -> Path:
        return self.get_path(filename, create_parent).with_name(f"{filename}.ver.txt")

    def get_tmp_path(self, filename: str, create_parent: bool = True) -> Path:
        return self.get_path(f"{filename}-{time.time() * 1000:.0f}.tmp", create_parent)

    def check_local_ver(self, info: ModelInfo) -> Optional[str]:
        if (
            self.get_path(info.filename).exists()
            and (ver_path := self.get_ver_path(info.filename)).exists()
        ):
            return ver_path.read_text(encoding="u8").strip()
        return None

    def save_local_ver(self, info: ModelInfo, clear: bool = False):
        p = self.get_ver_path(info.filename)
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
        tmp_path = self.get_tmp_path(info.filename)
        try:
            self._download(tmp_path, info)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise
        else:
            self.validate_with_unlink(tmp_path, info, clear_ver=False)
            path = self.get_path(info.filename)
            if not (p := path.parent).exists():
                p.mkdir(parents=True)
            if path.exists():
                path.unlink()
            tmp_path.rename(path)

    def validate(self, path: Path, info: ModelInfo) -> Any:  # noqa: ARG002
        """please raise Error when validation failed"""
        return

    def validate_with_unlink(
        self,
        path: Path,
        info: ModelInfo,
        clear_ver: bool = True,
    ) -> Any:
        try:
            return self.validate(path, info)
        except Exception:
            path.unlink(missing_ok=True)
            if clear_ver:
                self.save_local_ver(info, clear=True)
            raise

    def _get(self, force_update: bool = False) -> Path:
        if (
            (not force_update)
            and (not config.nailong_auto_update_model)
            and (local := self.find_from_local())
        ):
            logger.info("Update skipped")
            return local

        try:
            info = self.get_info()
        except Exception as e:
            if force_update or (not (local := self.find_from_local())):
                raise
            logger.error(
                f"Failed to get model info in {type(self).__name__}, skipping update: "
                f"{type(e).__name__}: {e}",
            )
            logger.debug("Stacktrace")
            return local

        model_path = self.get_path(info.filename)
        local_ver = self.check_local_ver(info)

        if model_path.exists():
            try:
                self.validate_with_unlink(model_path, info)
            except Exception as e:
                logger.error(
                    f"Validation for model {info.filename} failed, "
                    f"deleted, re-downloading: "
                    f"{type(e).__name__}: {e}",
                )

        if (not model_path.exists()) or (local_ver != info.version):
            from_tip = f"from version {local_ver or 'Unknown'} " if local_ver else ""
            logger.info(
                f"Updating model {info.filename} {from_tip}to version {info.version}",
            )
            try:
                self.download(info)
            except Exception as e:
                if force_update or (not (local := self.find_from_local())):
                    raise
                logger.error(
                    f"Failed to update model, skipping: {type(e).__name__}: {e}",
                )
                logger.debug("Stacktrace")
                return local
            else:
                self.save_local_ver(info)

        return model_path

    def get(self, force_update: bool = False):
        p = self._get(force_update)
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
        return find_file(self.root_dir, self.filename)

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
        local_filename_checker: Optional[Callable[[str], bool]] = None,
    ) -> None:
        super().__init__()
        self.owner = owner
        self.repo = repo
        self.local_filename_checker = local_filename_checker or (lambda _: True)

    def format_download_url(self, tag: str, filename: str) -> str:
        return (
            f"https://github.com/{self.owner}/{self.repo}/"
            f"releases/download/{tag}/{filename}"
        )

    @override
    def find_from_local(self) -> Optional[Path]:
        return find_file(self.root_dir, lambda p: self.local_filename_checker(p.name))

    @override
    def get_info(self) -> ModelInfo[None]:
        ret = self.github.rest.repos.get_latest_release(self.owner, self.repo)
        tag_name = ret.parsed_data.tag_name
        asset = next(
            x for x in ret.parsed_data.assets if self.local_filename_checker(x.name)
        )
        return ModelInfo(
            self.format_download_url(ret.parsed_data.tag_name, asset.name),
            asset.name,
            f"{tag_name}-{asset.updated_at.strftime(TIME_FORMAT_TEMPLATE)}",
            None,
        )


# 联动更新，还没有实现检查更新失败时使用本地文件的逻辑，因为没想到好的解决办法
class UpdaterGroup:
    def __init__(self, *updaters: ModelUpdater) -> None:
        self.updaters = updaters

    def get(self):
        force_update = config.nailong_auto_update_model
        return tuple(u.get(force_update) for u in self.updaters)
