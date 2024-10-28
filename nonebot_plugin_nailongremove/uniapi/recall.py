from typing import Awaitable, Callable, Dict, TypeVar
from typing_extensions import TypeAlias

from nonebot.adapters import Bot as BaseBot, Event as BaseEvent

Recaller: TypeAlias = Callable[[BaseBot, BaseEvent], Awaitable[None]]
RT = TypeVar("RT", bound=Recaller)

recall_map: Dict[str, Recaller] = {}


def recaller(adapter_name: str):
    def deco(func: RT) -> RT:
        recall_map[adapter_name] = func
        return func

    return deco


@recaller("Discord")
async def discord(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.discord import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.delete_message(channel_id=ev.channel_id, message_id=ev.message_id)


@recaller("DoDo")
async def dodo(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.dodo import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.set_channel_message_withdraw(message_id=ev.message_id)


@recaller("Feishu")
async def feishu(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.feishu import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    return await bot.call_api(f"im/v1/messages/{ev.message_id}", method="DELETE")


@recaller("Kaiheila")
async def kook(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.kaiheila import Bot
    from nonebot.adapters.kaiheila.event import MessageEvent, PrivateMessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    if isinstance(ev, PrivateMessageEvent):
        await bot.directMessage_delete(msg_id=ev.msg_id)
    else:
        await bot.message_delete(msg_id=ev.msg_id)


@recaller("Kritor")
async def kritor(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.kritor import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.recall_message(message_id=ev.message_id)


@recaller("Mirai")
async def mirai(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.mirai import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.recall_message(message=ev.message_id)


@recaller("OneBot V11")
async def onebot_v11(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.onebot.v11 import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.delete_msg(message_id=ev.message_id)


@recaller("OneBot V12")
async def onebot_v12(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.onebot.v12 import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.delete_message(message_id=ev.message_id)


@recaller("QQ")
async def qq(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.qq import (
        AtMessageCreateEvent,
        Bot,
        C2CMessageCreateEvent,
        DirectMessageCreateEvent,
        GroupAtMessageCreateEvent,
        MessageCreateEvent,
        MessageEvent,
    )

    if isinstance(bot, Bot) and isinstance(ev, MessageEvent):
        if isinstance(ev, C2CMessageCreateEvent):  # 私聊
            await bot.delete_c2c_message(openid=ev.author.id, message_id=ev.id)
        elif isinstance(ev, GroupAtMessageCreateEvent):  # 群聊
            await bot.delete_group_message(
                group_openid=ev.group_openid,
                message_id=ev.id,
            )
        elif isinstance(ev, DirectMessageCreateEvent):  # 频道私聊
            await bot.delete_dms_message(guild_id=ev.guild_id, message_id=ev.id)
        elif isinstance(ev, (AtMessageCreateEvent, MessageCreateEvent)):  # 频道
            await bot.delete_message(channel_id=ev.channel_id, message_id=ev.id)

    raise TypeError("Unsupported bot or event type")


@recaller("RedProtocol")
async def red(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.red import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.recall_message(ev.chatType, ev.peerUin, ev.msgId)


@recaller("Satori")
async def satori(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.satori import Bot, MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.message_delete(channel_id=ev.channel.id, message_id=ev.message.id)


@recaller("Telegram")
async def telegram(bot: BaseBot, ev: BaseEvent):
    from nonebot.adapters.telegram import Bot
    from nonebot.adapters.telegram.event import MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    await bot.delete_message(chat_id=ev.chat.id, message_id=ev.message_id)


@recaller("Tailchat")
async def tailchat(bot: BaseBot, ev: BaseEvent):
    from nonebot_adapter_tailchat import Bot
    from nonebot_adapter_tailchat.event import MessageEvent

    if not (isinstance(bot, Bot) and isinstance(ev, MessageEvent)):
        raise TypeError("Unsupported bot or event type")

    try:
        await bot.recallMessage(messageId=ev.get_message_id())
    except Exception:
        await bot.deleteMessage(messageId=ev.get_message_id())


async def recall(bot: BaseBot, ev: BaseEvent):
    if f := recall_map.get(bot.adapter.get_name()):
        return await f(bot, ev)
    raise NotImplementedError
