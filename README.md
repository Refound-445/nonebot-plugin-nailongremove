# nonebot_plugin_nailongremove

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
_✨ 一个基于分类模型的简单插件~ ✨_
<!-- prettier-ignore-end -->

## 声明
本插件仅供娱乐和学习交流。
## 简介

NailongRemove是一款由简单的分类模型建立的奶龙识别插件，可以识别群中的奶龙表情包并撤回该表情。

## 技术
本插件模型由三层卷积+两个全连接层构成，基于cifar10数据集的10分类，加入200多张奶龙表情包，并进行预处理为大小（32，32），形成11分类模型，在此基础上训练得到。

模型会有误差，目前仍在优化改进中...

## 使用
只要有人发奶龙表情包被识别出来，就会被撤回并提醒。

## 即刻开始

- 使用 nb-cli

```
nb plugin install nonebot_plugin_nailongremove
```

- 使用 pip

```
pip install nonebot_plugin_nailongremove
```
## 其他
- 人工智能学习交流群：949992679

- 机器人插件学习交流群：200980266

欢迎大家进群一起学习交流~
## 许可证

`noneBot_plugin_picsbank` 采用 `MIT` 协议开源，协议文件参考 [LICENSE](../plugins/nonebot_plugin_picsbank-master/LICENSE)。

