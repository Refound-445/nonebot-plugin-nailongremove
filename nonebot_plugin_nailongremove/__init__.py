
from nonebot.plugin import PluginMetadata

from .config import Config
from nonebot import get_plugin_config
from .handler import *

__plugin_meta__ = PluginMetadata(
    name="NailongRemove",
    description="喜欢发奶龙的小朋友，你好呐~",
    usage="只要群内有人发奶龙就会被撤回",
    type="application",
    homepage="https://github.com/Refound-445/onoebot-plugin-nailongremove",
    config=Config,
    supported_adapters={"~onebot.v11"},
)
config = get_plugin_config(Config)


