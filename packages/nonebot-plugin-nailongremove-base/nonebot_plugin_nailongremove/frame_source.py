from abc import ABC, abstractmethod
from io import BytesIO
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterator,
    Tuple,
    Type,
    TypeVar,
    cast, Optional,
)

import httpx
from typing_extensions import Self, TypeAlias, override

import cv2
import numpy as np
from nonebot import logger
from nonebot.drivers import Request
from nonebot.matcher import current_bot, current_event, current_matcher
from nonebot_plugin_alconna.builtins.uniseg.market_face import MarketFace
from nonebot_plugin_alconna.uniseg import Image, Segment, UniMessage
# from nonebot_plugin_alconna.uniseg.tools import image_fetch
from PIL import Image as Img, ImageSequence

T = TypeVar("T")


class FrameSource(ABC, Generic[T]):
    def __init__(self, data: T) -> None:
        super().__init__()
        self.data = data

    @abstractmethod
    def __iter__(self) -> Iterator[np.ndarray]: ...


class PilImageFrameSource(FrameSource[Img.Image]):
    def __init__(self, data: Img.Image) -> None:
        super().__init__(data)

    @classmethod
    def from_raw(cls, raw: bytes) -> Self:
        return cls(Img.open(BytesIO(raw)))

    @override
    def __iter__(self) -> Iterator[np.ndarray]:
        for frame in ImageSequence.Iterator(self.data):
            image_array = np.array(frame.convert("RGB"))
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            yield image_array


TFS = TypeVar("TFS", bound=FrameSource)
RepackSaver: TypeAlias = Callable[[TFS, Iterator[np.ndarray]], Awaitable[Segment]]
repack_savers: Dict[Type[FrameSource], RepackSaver] = {}


def repack_saver(t: Type[TFS]):
    def deco(func: RepackSaver[TFS]):
        repack_savers[t] = func
        return func

    return deco


# https://github.com/MeetWq/meme-generator/blob/main/meme_generator/utils.py#L60
def save_gif(frames: list[Img.Image], duration: float) -> BytesIO:
    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration * 1000,
        loop=0,
        disposal=2,
        optimize=False,
    )

    # 没有超出最大大小，直接返回
    nbytes = output.getbuffer().nbytes
    if nbytes <= 10000000:  # meme_config.gif.gif_max_size * 10**6:
        return output

    # 超出最大大小，帧数超出最大帧数时，缩减帧数
    n_frames = len(frames)
    gif_max_frames = 100  # meme_config.gif.gif_max_frames
    if n_frames > gif_max_frames:
        index = range(n_frames)
        ratio = n_frames / gif_max_frames
        index = (int(i * ratio) for i in range(gif_max_frames))
        new_duration = duration * ratio
        new_frames = [frames[i] for i in index]
        return save_gif(new_frames, new_duration)

    # 超出最大大小，帧数没有超出最大帧数时，缩小尺寸
    new_frames = [
        frame.resize((int(frame.width * 0.9), int(frame.height * 0.9)))
        for frame in frames
    ]
    return save_gif(new_frames, duration)


# https://github.com/MeetWq/meme-generator/blob/main/meme_generator/utils.py#L97
def get_avg_duration(image: Img.Image) -> float:
    if not getattr(image, "is_animated", False):
        return 0
    total_duration = 0
    frames = list(ImageSequence.Iterator(image))
    for frame in frames:
        total_duration += frame.info.get("duration", 20)
    return total_duration / len(frames) / 1000


@repack_saver(PilImageFrameSource)
async def _(source: PilImageFrameSource, frames: Iterator[np.ndarray]) -> Segment:
    frame_images = [
        Img.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in frames
    ]
    if len(frame_images) == 1:
        bio = BytesIO()
        frame_images[0].save(bio, format="PNG")
    else:
        bio = save_gif(frame_images, get_avg_duration(source.data))
    return Image(raw=bio)


def repack_save(
        source: FrameSource,
        frames: Iterator[np.ndarray],
) -> Awaitable[Segment]:
    if (k := type(source)) not in repack_savers:
        raise NotImplementedError
    return repack_savers[k](source, frames)


TS = TypeVar("TS", bound=Segment)
SourceExtractor: TypeAlias = Callable[[TS], Awaitable[FrameSource]]
source_extractors: Dict[Type[Segment], SourceExtractor] = {}


def source_extractor(t: Type[TS]):
    def deco(func: SourceExtractor[TS]):
        source_extractors[t] = func
        return func

    return deco


async def image_fetch(url: str) -> Optional[bytes]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            image_data = response.content
            return image_data
        else:
            return None


@source_extractor(Image)
async def _(seg: Image):
    image = await image_fetch(
        seg.data['url'].replace('https://multimedia.nt.qq.com.cn/', 'http://multimedia.nt.qq.com.cn/', 1),
    )
    if not image:
        raise RuntimeError("Cannot fetch image")
    return PilImageFrameSource.from_raw(image)


@source_extractor(MarketFace)
async def _(seg: MarketFace):
    url = (
        f"https://gxh.vip.qq.com/club/item/parcel/item/{seg.id[:2]}/{seg.id}/raw300.gif"
    )
    req = Request("GET", url)
    resp = await current_bot.get().adapter.request(req)
    image = cast(bytes, resp.content)
    return PilImageFrameSource.from_raw(image)


async def extract_source(seg: Segment) -> FrameSource:
    if (k := type(seg)) not in source_extractors:
        raise NotImplementedError
    return await source_extractors[k](seg)


async def iter_sources_in_message(
        message: UniMessage,
) -> AsyncIterator[Tuple[FrameSource, Segment]]:
    for seg in message:
        try:
            yield await extract_source(seg), seg
        except NotImplementedError:
            continue
        except Exception as e:
            logger.warning(f"Failed to process {seg!r}: {type(e).__name__}: {e}")
            logger.opt(exception=e).debug("Stacktrace")
