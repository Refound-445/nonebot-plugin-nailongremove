from typing import Any, Awaitable, Callable, Iterable, List, TypeVar

from nonebot import logger, on_message
from nonebot.adapters import Bot as BaseBot, Event as BaseEvent
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot_plugin_alconna.builtins.uniseg.market_face import MarketFace
from nonebot_plugin_alconna.uniseg import Image, UniMessage, UniMsg
from nonebot_plugin_uninfo import QryItrface, Uninfo

from nonebot_plugin_nailongremove.frame_source import iter_sources_in_message

from .config import DEFAULT_LABEL, config
from .model import check
from .uniapi import mute, recall

T = TypeVar("T")


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
        # bypass superuser
        and ((not config.nailong_bypass_superuser) or (not await SUPERUSER(bot, event)))
        # bypass group admin
        and (
            (not config.nailong_bypass_admin)
            or ((not session.member.role) or session.member.role.level <= 1)
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
                and self_info.role.level > 1,
            )
        )
    )


nailong = on_message(rule=Rule(nailong_rule), priority=config.nailong_priority)


@nailong.handle()
async def handle_function(bot: BaseBot, ev: BaseEvent, msg: UniMsg, session: Uninfo):
    async for source, seg in iter_sources_in_message(msg):
        try:
            check_res = await check(source)
        except Exception:
            logger.exception(f"Failed to check {seg!r}")
            continue
        if not check_res.ok:
            continue

        functions: List[Callable[[], Awaitable[Any]]] = []
        if config.nailong_recall:
            functions.append(lambda: recall(bot, ev))
        if config.nailong_mute_seconds > 0:
            functions.append(lambda: mute(bot, ev, config.nailong_mute_seconds))
        punish_ok = functions and (await execute_functions_any_ok(functions))

        template_dict = config.nailong_tip if punish_ok else config.nailong_failed_tip
        template_str = template_dict[
            check_res.label if (check_res.label in template_dict) else DEFAULT_LABEL
        ]
        mapping = {
            "$event": ev,
            "$target": msg.get_target(),
            "$message_id": msg.get_message_id(),
            "$msg": msg,
            "$ss": session,
            **check_res.extra_vars,
        }
        await UniMessage.template(template_str).format_map(mapping).finish()
