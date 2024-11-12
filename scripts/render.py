import re
from pathlib import Path
from typing import List, Optional, TypedDict, cast

import bs4
import httpx
import tomllib
from packaging.version import Version

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


def format_markers(m: re.Match[str]) -> Optional[str]:
    g = cast(PkgFilenameReGroups, m.groupdict())
    if (not g["py"].startswith("cp")) or (g["abi"].endswith("m")):
        return None

    markers: List[str] = []
    markers.append(f"python_version == '{g['py'][2]}.{g['py'][3:]}'")

    common_os = {
        "win": "win32",
        "linux": "linux",
    }
    if x := next((x for x in common_os if g["platform"].startswith(f"{x}_")), None):
        markers.extend(
            (
                f"sys_platform == '{common_os[x]}'",
                f"platform_machine == '{g['platform'][len(x) + 1:]}'",
            ),
        )

    return " and ".join(markers)


def get_torch_deps() -> str:
    def get_deps(pkg: str) -> List[str]:
        html = httpx.get(f"{TORCH_INDEX}/{pkg}/").raise_for_status().text
        soup = bs4.BeautifulSoup(html, "lxml")
        tags: "bs4.ResultSet[bs4.Tag]" = soup.find_all("a")
        links = [
            (m, f"{TORCH_BASE}{h}")
            for x in tags
            if (
                isinstance((h := x.get("href")), str)
                and (m := PKG_FILENAME_RE.match(x.text))
            )
        ]
        links.sort(key=lambda x: Version(x[0]["ver"]), reverse=True)
        ver: str = links[1][0]["ver"]
        links = [x for x in links if x[0]["ver"] == ver]
        return [f"{pkg} @ {x} ; {ms}" for m, x in links if (ms := format_markers(m))]

    deps = [
        *get_deps("torch"),
        *get_deps("torchvision"),
    ]
    return "\n    ".join(f'"{x}",' for x in deps).strip(",")


# TORCH = get_torch_deps()


def process(file_path: Path):
    file_path.with_name(file_path.name.replace(".template", "")).write_text(
        (
            file_path.read_text(encoding="u8").replace("%%version%%", VERSION)
            # .replace('"%%torch%%"', TORCH)
        ),
        "u8",
    )


def main():
    for p in PACKAGES_PATH.iterdir():
        for f in (x for x in p.iterdir() if x.name.endswith(SUFFIX)):
            process(f)


if __name__ == "__main__":
    main()
