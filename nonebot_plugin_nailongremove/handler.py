import io
from typing import Iterable, TypeVar, cast

import cv2
import numpy as np
from nonebot import logger, on_message
from nonebot.adapters import Bot as BaseBot, Event as BaseEvent
from nonebot.drivers import Request
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot.utils import run_sync
from nonebot_plugin_alconna.builtins.uniseg.market_face import MarketFace
from nonebot_plugin_alconna.uniseg import Image, UniMsg, image_fetch
from nonebot_plugin_uninfo import Uninfo
from PIL import Image as PilImage

from .config import config
from .model import check_image
from .recall import recall

T = TypeVar("T")


def transform_image(image_data: bytes) -> np.ndarray:
    image = PilImage.open(io.BytesIO(image_data))

    if (
        # image.format == "GIF" and
        getattr(image, "is_animated", False)
    ):
        # 处理动图：仅获取第一帧
        image = image.convert("RGB")
        image = image.copy()  # 获取第一帧
    else:
        image = image.convert("RGB")

    image_array = np.array(image)
    # OpenCV通常使用BGR格式，因此需要转换
    if len(image_array.shape) == 3 and image_array.shape[2] == 3:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

    return image_array


def judge_list(lst: Iterable[T], val: T, blacklist: bool) -> bool:
    return (val not in lst) if blacklist else (val in lst)


async def nailong_rule(
    bot: BaseBot,
    event: BaseEvent,
    ss_info: Uninfo,
    msg: UniMsg,
) -> bool:
    return (
        bool(ss_info.member)  # 检查是否是群聊消息，此值仅在群聊与频道中存在
        and (
            # bypass superuser
            (not await SUPERUSER(bot, event))
            # bypass group admin
            or ((not ss_info.member.role) or ss_info.member.role.level <= 1)
        )
        and ((Image in msg) or (MarketFace in msg))  # msg has image
        and judge_list(
            config.nailong_list_scenes,
            ss_info.scene_path,
            config.nailong_blacklist,
        )
    )


nailong = on_message(rule=Rule(nailong_rule))


@nailong.handle()
async def handle_function(
    m: Matcher,
    bot: BaseBot,
    ev: BaseEvent,
    msg: UniMsg,
    state: T_State,
):
    for seg in msg:
        if isinstance(seg, Image):
            image = await image_fetch(ev, bot, state, seg)
            if not image:
                logger.warning(f"Failed to fetch image: {seg!r}")
                continue

        elif isinstance(seg, MarketFace):
            url = f"https://gxh.vip.qq.com/club/item/parcel/item/{seg.id[:2]}/{seg.id}/raw300.gif"
            req = Request("GET", url)
            try:
                resp = await bot.adapter.request(req)
            except Exception as e:
                logger.warning(f"Failed to fetch {seg!r}: {type(e).__name__}: {e}")
                continue
            image = cast(bytes, resp.content)

        else:
            continue

        try:
            ok = await run_sync(check_image)(
                await run_sync(transform_image)(image),
            )
        except Exception:
            logger.exception(f"Failed to process image: {seg!r}")
            continue

        if ok:
            logger.info(f"尝试撤回包含奶龙的图片并发送警告：{seg!r}")
            await m.send("本群禁止发送奶龙！")
            try:
                await recall(bot, ev)
            except Exception as e:
                logger.warning(f"{type(e).__name__}: {e}")
            await m.finish()
