import asyncio
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, TypeVar
from typing_extensions import TypeAlias

import numpy as np

from ...config import config
from ...frame_source import FrameSource

T = TypeVar("T")


@dataclass
class CheckSingleResult(Generic[T]):
    label: Optional[str] = None
    extra: T = None  # type: ignore


@dataclass
class CheckResult:
    label: Optional[str] = None
    extra_vars: Dict[str, Any] = field(default_factory=dict)


FrameChecker: TypeAlias = Callable[[np.ndarray], Awaitable[CheckSingleResult[T]]]


async def race_check(
    checker: FrameChecker[T],
    frames: FrameSource,
    concurrency: int = config.nailong_concurrency,
) -> Optional[CheckSingleResult[T]]:
    iterator = iter(frames)

    async def worker() -> Optional[CheckSingleResult[T]]:
        while True:
            try:
                frame = next(iterator)
            except StopIteration:
                return None
            res = await checker(frame)
            if res.label:
                return res

    tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
    while True:
        if not tasks:
            break
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in done:
            if (res := t.result()) and res.label:
                for pt in pending:
                    pt.cancel()
                return res
        tasks = pending

    return None
