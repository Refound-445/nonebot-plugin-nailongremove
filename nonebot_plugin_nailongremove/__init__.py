
from nonebot.plugin import PluginMetadata

from .config import Config
from nonebot import get_plugin_config
from .handler import *

__plugin_meta__ = PluginMetadata(
    name="自动撤回奶龙",
    description="一个基于图像分类模型的简单插件~",
    usage="只要群内有人发奶龙就会被撤回",
    type="application",
    homepage="https://github.com/Refound-445/onoebot-plugin-nailongremove",
    config=Config,
    supported_adapters={"~onebot.v11"},
)
config = get_plugin_config(Config)


