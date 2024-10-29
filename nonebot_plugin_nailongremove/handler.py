import io
from typing import Any, Awaitable, Callable, Iterable, List, TypeVar, cast

import cv2
import numpy as np
from nonebot import logger, on_message
from nonebot.adapters import Bot as BaseBot, Event as BaseEvent
from nonebot.drivers import Request
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot.utils import run_sync
from nonebot_plugin_alconna.builtins.uniseg.market_face import MarketFace
from nonebot_plugin_alconna.uniseg import Image, UniMessage, UniMsg, image_fetch
from nonebot_plugin_uninfo import QryItrface, Uninfo
from PIL import Image as PilImage

from .config import config
from .model import check_image
from .uniapi import mute, recall

T = TypeVar("T")


def transform_image(image_data: bytes) -> list[np.ndarray]:
    image = PilImage.open(io.BytesIO(image_data))
    frames = []

    if getattr(image, "is_animated", False):
        # 遍历每一帧
        for frame in range(image.n_frames):
            image.seek(frame)
            frame_image = image.convert("RGB")
            frame_array = np.array(frame_image)

            # 转换为BGR格式
            if len(frame_array.shape) == 3 and frame_array.shape[2] == 3:
                frame_array = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)

            frames.append(frame_array)
    else:
        image = image.convert("RGB")
        image_array = np.array(image)

        # 转换为BGR格式
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

        frames.append(image_array)

    return frames



def judge_list(lst: Iterable[T], val: T, blacklist: bool) -> bool:
    return (val not in lst) if blacklist else (val in lst)


async def execute_functions_any_ok(
    func: Iterable[Callable[[], Awaitable[Any]]],
) -> bool:
    ok = False
    for f in func:
        try:
            await f()
        except Exception as e:
            logger.warning(f"{type(e).__name__}: {e}")
            logger.opt(exception=e).debug("Stacktrace:")
        else:
            ok = True
    return ok


async def nailong_rule(
    bot: BaseBot,
    event: BaseEvent,
    session: Uninfo,
    ss_interface: QryItrface,
    msg: UniMsg,
) -> bool:
    return (
        # check if it's a group chat
        bool(session.member)  # this prop only exists in group chats
        # bypass
        and (
            # bypass superuser
            ((not config.nailong_bypass_superuser) or (not await SUPERUSER(bot, event)))
            # bypass group admin
            or (
                (not config.nailong_bypass_admin)
                or ((not session.member.role) or session.member.role.level <= 1)
            )
        )
        # msg has image
        and ((Image in msg) or (MarketFace in msg))
        # blacklist or whitelist
        and judge_list(
            config.nailong_list_scenes,
            session.scene_path,
            config.nailong_blacklist,
        )
        # self is admin
        and (
            (not config.nailong_need_admin)
            or bool(
                (
                    self_info := await ss_interface.get_member(
                        session.scene.type,
                        session.scene.id,
                        user_id=session.self_id,
                    )
                )
                and self_info.role
                and self_info.role.level >= 1,
            )
        )
    )


nailong = on_message(rule=Rule(nailong_rule))


@nailong.handle()
async def handle_function(
    bot: BaseBot,
    ev: BaseEvent,
    msg: UniMsg,
    session: Uninfo,
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
            check_ok = await run_sync(check_image)(
                await run_sync(transform_image)(image),
            )
        except Exception:
            logger.exception(f"Failed to process image: {seg!r}")
            continue
        if not check_ok:
            continue

        functions: List[Callable[[], Awaitable[Any]]] = []
        if config.nailong_recall:
            functions.append(lambda: recall(bot, ev))
        if config.nailong_mute_seconds > 0:
            functions.append(lambda: mute(bot, ev, config.nailong_mute_seconds))
        punish_ok = (not functions) or (await execute_functions_any_ok(functions))

        template_str = config.nailong_tip if punish_ok else config.nailong_failed_tip
        await (
            UniMessage.template(template_str)
            .format_map(
                {
                    "$event": ev,
                    "$target": msg.get_target(),
                    "$message_id": msg.get_message_id(),
                    "$msg": msg,
                    "$ss": session,
                },
            )
            .finish()
        )
