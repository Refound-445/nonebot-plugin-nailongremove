import re
from typing import Any, Awaitable, Callable, Iterable, List, TypeVar
from nonebot import logger, on_message
from nonebot.adapters import Bot as BaseBot, Event as BaseEvent
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot_plugin_alconna.uniseg import UniMessage, UniMsg, Text
from nonebot_plugin_uninfo import QryItrface, Uninfo

from .config import DEFAULT_LABEL, config
from .frame_source import iter_sources_in_message, source_extractors
from .model import check
from .uniapi import mute, recall
from .model.utils.common import process_gif_and_save_jpgs


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
            # user blacklist
            and (session.user.id not in config.nailong_user_blacklist)
            # scene blacklist or whitelist
            and judge_list(
        config.nailong_list_scenes,
        session.scene_path,
        config.nailong_blacklist,
    )
            # bypass superuser
            and ((not config.nailong_bypass_superuser) or (not await SUPERUSER(bot, event)))
            # bypass group admin
            and (
                    (not config.nailong_bypass_admin)
                    or ((not session.member.role) or session.member.role.level <= 1)
            )
            # msg has supported seg
            and (any(True for x in msg if type(x) in source_extractors))
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
input_shape = config.nailong_model1_yolox_size or config.nailong_model1_type.yolox_size

@nailong.handle()
async def handle_function(bot: BaseBot, ev: BaseEvent, msg: UniMsg, session: Uninfo):
    save_img = False
    if await SUPERUSER(bot, ev):
        for seg in msg:
            if type(seg) == Text and "这是" in seg.text:
                save_img = True
                label = re.search(r"这是(\S+)", seg.text.replace(" ", "")).group(1)
                break
    async for source, seg in iter_sources_in_message(msg):
        if save_img:
            frames = []
            temp_iter = iter(source)
            while True:
                try:
                    temp_image = next(temp_iter)
                    frames.append(temp_image)
                except StopIteration:
                    break
            zip_filename = process_gif_and_save_jpgs(frames, label, input_shape)
            if zip_filename is None:
                await nailong.finish(f"已保存数据到目录{config.nailong_model_dir}\\records\\{label}，标签：{label}")
            else:
                await nailong.finish(
                    f"记录数据超过{config.nailong_similarity_max_storage}，已清除原记录数据，压缩并保存至{zip_filename}\n已保存数据到目录{config.nailong_model_dir}\\records\\{label}，标签：{label}")
        else:
            try:
                check_res = await check(source)
            except Exception:
                logger.exception(f"Failed to check {seg!r}")
                continue
            if not check_res.ok or check_res.label not in config.nailong_tip:
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
