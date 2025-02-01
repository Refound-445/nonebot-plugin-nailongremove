# ruff: noqa: E402

from nonebot import get_plugin_config, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from . import handler as handler
from .config import Config

__version__ = "2.3.6.post1"
__plugin_meta__ = PluginMetadata(
    name="自动撤回奶龙",
    description="一个基于图像分类模型的简单插件~",
    usage="只要群内有人发奶龙就会被撤回",
    type="application",
    homepage="https://github.com/Refound-445/nonebot-plugin-nailongremove",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna",
        "nonebot_plugin_uninfo",
    ),
)
config = get_plugin_config(Config)
