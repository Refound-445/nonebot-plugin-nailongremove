from pathlib import Path
from subprocess import run
from typing import Any

ROOT_PATH = Path(__file__).parent.parent.parent
PACKAGES_PATH = ROOT_PATH / "packages"


def system(*args: str, **kwargs: Any):
    kwargs.setdefault("cwd", str(ROOT_PATH))
    r = run(args, **kwargs)  # noqa: S603
    return r.returncode


def system_no_fail(*args: str, **kwargs: Any):
    c = system(*args, **kwargs)
    if c:
        raise RuntimeError(f"command {args} failed with code {c}")
