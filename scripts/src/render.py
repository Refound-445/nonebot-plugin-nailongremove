import re
from pathlib import Path
from typing import TypedDict

try:
    import tomllib  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    import tomli as tomllib  # pyright: ignore[reportMissingImports]

from .utils import PACKAGES_PATH

SUFFIX = ".template.toml"
TORCH_BASE = "https://download.pytorch.org"
TORCH_INDEX = f"{TORCH_BASE}/whl/cu124"

PKG_FILENAME_RE = re.compile(
    r"^(?P<name>.+?)-(?P<ver>.+?)-(?P<py>.+?)-(?P<abi>.+?)-(?P<platform>.+?)"
    r"(?P<ext>\..+)$",
)
VERSION_RE = re.compile(
    r"""^(\s*)__version__(\s*)=(\s*)(?P<q>['"])(?P<v>.+?)(?P=q)(\s*);?(\s*)$""",
    re.MULTILINE,
)


class PkgFilenameReGroups(TypedDict):
    name: str
    ver: str
    py: str
    abi: str
    platform: str
    ext: str


def get_version() -> str:
    base_pkg_path = PACKAGES_PATH / "nonebot-plugin-nailongremove-base"
    base_toml_path = base_pkg_path / "pyproject.toml"
    toml_dict = tomllib.loads(base_toml_path.read_text(encoding="u8"))
    version = toml_dict["tool"]["pdm"]["version"]
    if version["source"] != "file":
        raise NotImplementedError
    version_file_path = base_pkg_path / version["path"]
    version_file_raw = version_file_path.read_text(encoding="u8")
    version_match = VERSION_RE.search(version_file_raw)
    if not version_match:
        raise ValueError("Version not found in pyproject.toml")
    return version_match.group("v")


VERSION = get_version()


def process(file_path: Path):
    file_path.with_name(file_path.name.replace(".template", "")).write_text(
        file_path.read_text(encoding="u8").replace("%%version%%", VERSION),
        "u8",
    )


def main():
    for p in PACKAGES_PATH.iterdir():
        for f in (x for x in p.iterdir() if x.name.endswith(SUFFIX)):
            process(f)


if __name__ == "__main__":
    main()
