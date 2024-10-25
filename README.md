<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# Nonebot-Plugin-NaiLongRemove

_✨ 一个基于分类模型的简单插件~ ✨_

<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<a href="https://pdm.fming.dev">
  <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>

<br />

<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/Refound-445/nonebot-plugin-nailongremove.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-nailongremove">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-nailongremove.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-nailongremove">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-nailongremove" alt="pypi download">
</a>

<br />

<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-nailongremove:nonebot_plugin_nailongremove">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin%2Fnonebot-plugin-nailongremove" alt="NoneBot Registry">
</a>
<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-nailongremove:nonebot_plugin_nailongremove">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin-adapters%2Fnonebot-plugin-nailongremove" alt="Supported Adapters">
</a>

</div>

## 📖 介绍

### 声明

本插件仅供娱乐和学习交流。

关于一些问题：

- 模型精度：目前模型只是轮廓所以精度相对较低，还在进一步优化中，如果您也是人工智能方面的兴趣爱好者，欢迎来群里交流学习和开发（人工智能学习交流群 949992679），届时我们会署上贡献者名单~
- 关于插件安装：目前插件需要通过 nonebot2 进行加载，关于 nonebot2 及其插件安装请移到官方群 768887710 交流咨询~
- 如果只是安装插件，请先到官方群咨询安装 768887710
- 如果只是安装插件，请先到官方群咨询安装 768887710
- 如果只是安装插件，请先到官方群咨询安装 768887710

### 简介

NailongRemove 是一款由简单的分类模型建立的奶龙识别插件，可以识别群中的奶龙表情包并撤回该表情。

### 技术

本插件模型由三层卷积+两个全连接层构成，基于 cifar10 数据集的 10 分类，加入 200 多张奶龙表情包，并进行预处理为大小（32，32），形成 11 分类模型，在此基础上训练得到。

模型会有误差，目前仍在优化改进中……

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-nailongremove
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-nailongremove
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-nailongremove
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-nailongremove
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-nailongremove
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_nailongremove"
]
```

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中添加下表中的必填配置

|        配置项         | 必填 |         默认值         |                                                                                                                                                                                                                                    说明                                                                                                                                                                                                                                    |
| :-------------------: | :--: | :--------------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|  `NAILONG_MODEL_DIR`  |  否  | `./data/nailongremove` |                                                                                                                                                                                                                               模型的下载位置                                                                                                                                                                                                                               |
| `NAILONG_LIST_SCENES` |  否  |          `[]`          |                                                                                                                                                               聊天场景 ID 黑白名单列表<br />在单级聊天下为该聊天 ID，如 QQ 群号；<br />在多级聊天下为以 `_` 分割的各级聊天 ID，如频道下的子频道或频道下私聊                                                                                                                                                                |
|  `NAILONG_BLACKLIST`  |  否  |         `True`         |                                                                                                                                                                                                                             是否使用黑名单模式                                                                                                                                                                                                                             |
|   `NAILONG_RECALL`    |  否  |         `True`         |                                                                                                                                                                                                                                是否撤回消息                                                                                                                                                                                                                                |
|     `NAILONG_TIP`     |  否  |   `本群禁止发奶龙！`   | 发送的提示，使用 [Alconna 的消息模板](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E4%BD%BF%E7%94%A8%E6%B6%88%E6%81%AF%E6%A8%A1%E6%9D%BF)<br />可用变量：`ev`: [`Event`](https://nonebot.dev/docs/api/adapters/#Event); `msg`: [`UniMessage`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E9%80%9A%E7%94%A8%E6%B6%88%E6%81%AF%E5%BA%8F%E5%88%97); `ss`: [`Session`](https://github.com/RF-Tar-Railt/nonebot-plugin-uninfo?tab=readme-ov-file#session) |

## 🎉 使用

只要有人发奶龙表情包被识别出来，就会被撤回并提醒。

## 📞 联系

- 人工智能学习交流群：949992679<span style="color: yellow;">（开源代码，数据集，从本群获取）</span>

- 机器人插件学习交流群：200980266<span style="color: yellow;">（机器人及插件安装包，从本群获取）</span>

欢迎大家进群一起学习交流~

<!-- ## 📝 更新日志

芝士刚刚发布的插件，还没有更新日志的说 qwq~ -->
