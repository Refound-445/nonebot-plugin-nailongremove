from time import time
from typing import Awaitable, Callable, Dict, TypeVar
from typing_extensions import TypeAlias

from nonebot.adapters import Bot as BaseBot, Event as BaseEvent
from nonebot.drivers import Request

Muter: TypeAlias = Callable[[BaseBot, BaseEvent, int], Awaitable[None]]
MT = TypeVar("MT", bound=Muter)

muter_map: Dict[str, Muter] = {}


def muter(adapter_name: str):
    def deco(func: MT) -> MT:
        muter_map[adapter_name] = func
        return func

    return deco


@muter("DoDo")
async def dodo(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot.adapters.dodo import Bot, MessageEvent

    if not (
        isinstance(bot, Bot)
        and isinstance(ev, MessageEvent)
        and ev.island_source_id
        and ev.dodo_source_id
    ):
        raise TypeError("Unsupported bot or event type")

    if seconds > 0:
        await bot.set_member_mute_add(
            island_source_id=ev.island_source_id,
            dodo_source_id=ev.dodo_source_id,
            duration=seconds,
        )
    else:
        await bot.set_member_mute_remove(
            island_source_id=ev.island_source_id,
            dodo_source_id=ev.dodo_source_id,
        )


@muter("Kritor")
async def kritor(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot.adapters.kritor import Bot
    from nonebot.adapters.kritor.event import GroupMessage

    if not (isinstance(bot, Bot) and isinstance(ev, GroupMessage)):
        raise TypeError("Unsupported bot or event type")

    await bot.ban_member(
        group=ev.sender.group_id,
        target=ev.sender.uin,
        duration=seconds,
    )


@muter("Mirai")
async def mirai(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot.adapters.mirai import Bot
    from nonebot.adapters.mirai.event import GroupMessage

    if not (isinstance(bot, Bot) and isinstance(ev, GroupMessage)):
        raise TypeError("Unsupported bot or event type")

    await bot.mute_member(group=ev.sender.group.id, member=ev.sender.id, time=seconds)


@muter("OneBot V11")
async def onebot_v11(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, GroupMessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.set_group_ban(group_id=ev.group_id, user_id=ev.user_id, duration=seconds)


@muter("RedProtocol")
async def red(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot.adapters.red import Bot, GroupMessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, GroupMessageEvent)):
        raise TypeError("Unsupported bot or event type")

    if seconds > 0:
        await bot.mute_member(int(ev.peerUin), int(ev.senderUin), duration=seconds)
    else:
        await bot.unmute_member(int(ev.peerUin), int(ev.senderUin))


@muter("Satori")
async def satori(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot.adapters.satori import Bot
    from nonebot.adapters.satori.event import (
        PublicMessageCreatedEvent,
        PublicMessageUpdatedEvent,
    )

    if not (
        isinstance(bot, Bot)
        and isinstance(ev, (PublicMessageCreatedEvent, PublicMessageUpdatedEvent))
        and ev.guild
    ):
        raise TypeError("Unsupported bot or event type")

    req = Request(
        "POST",
        bot.info.api_base / "guild.member.mute",
        json={
            "guild_id": ev.guild.id,
            "user_id": ev.user.id,
            "duration": seconds * 1000,
        },
    )
    await bot._request(req)  # noqa: SLF001


@muter("Telegram")
async def telegram(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot.adapters.telegram import Bot
    from nonebot.adapters.telegram.event import GroupMessageEvent
    from nonebot.adapters.telegram.model import ChatPermissions

    if not (isinstance(bot, Bot) and isinstance(ev, GroupMessageEvent)):
        raise TypeError("Unsupported bot or event type")

    should_not_mute = seconds < 30
    await bot.restrict_chat_member(
        chat_id=ev.chat.id,
        user_id=ev.from_.id,
        permissions=ChatPermissions(can_send_messages=should_not_mute),
        until_date=None if should_not_mute else int(time()) + seconds,
    )


@muter("Tailchat")
async def tailchat(bot: BaseBot, ev: BaseEvent, seconds: int):
    from nonebot_adapter_tailchat import Bot
    from nonebot_adapter_tailchat.event import MessageEvent

    if not (
        isinstance(bot, Bot)
        and isinstance(ev, MessageEvent)
        and ev.is_group()
        and (group_id := ev.get_group_id())
    ):
        raise TypeError("Unsupported bot or event type")

    await bot.muteGroupMember(
        muteMs=seconds * 1000,
        groupId=group_id,
        memberId=ev.get_user_id(),
    )


async def mute(bot: BaseBot, ev: BaseEvent, seconds: int):
    if f := muter_map.get(bot.adapter.get_name()):
        return await f(bot, ev, seconds)
    raise NotImplementedError
