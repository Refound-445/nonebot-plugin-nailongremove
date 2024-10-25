# nonebot_plugin_nailongremove

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
_✨ 一个基于分类模型的简单插件~ ✨_
<!-- prettier-ignore-end -->

## 声明
本插件仅供娱乐和学习交流。
关于一些问题：
- 模型精度：目前模型只是轮廓所以精度相对较低，还在进一步优化中，如果您也是人工智能方面的兴趣爱好者，欢迎来群里交流学习和开发，届时我们会署上贡献者名单~
- 关于插件安装：目前插件需要通过nonebot2进行加载，也可本地调试(供学习者研究)但是就不能实现撤回功能，关于nonebot2及其插件安装请移到官方群768887710交流咨询~
- 如果只是安装插件，请先到官方群咨询安装768887710
- 如果只是安装插件，请先到官方群咨询安装768887710
- 如果只是安装插件，请先到官方群咨询安装768887710
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
- 人工智能学习交流群：949992679<span style="color: yellow;">（开源代码，数据集，从本群获取）</span>


- 机器人插件学习交流群：200980266<span style="color: yellow;">（机器人及插件安装包，从本群获取）</span>


欢迎大家进群一起学习交流~
## 许可证

`noneBot_plugin_picsbank` 采用 `MIT` 协议开源，协议文件参考 [LICENSE](../plugins/nonebot_plugin_picsbank-master/LICENSE)。

