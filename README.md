<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# Nonebot-Plugin-NaiLongRemove

_✨ 一个基于AI模型的简单插件~ ✨_

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

### 简介

NailongRemove 是一款由简单的AI模型建立的奶龙识别插件，可以识别群中的奶龙表情包并撤回该表情。

### 技术
目前插件支持两个模型"0"和"1"，通过机器人目录初始化的.env文件内修改NAILONG_MODEL参数更换模型。

- 0：基于Renet50图像分类模型训练推理，感谢 @spawner1145 提供的模型，原链接：[spawner1145/NailongRecognize](https://github.com/spawner1145/NailongRecognize.git)


- 1：基于YOLOX目标检测模型训练推理，感谢 @NKXingXh 提供的模型，原链接：[nkxingxh/NailongDetection](https://github.com/nkxingxh/NailongDetection)

用户可以根据需要自行选择心仪的模型，两个模型性能都已经经过优化，但仍可能会有不同程度的误差，也欢迎各位继续反馈给我们~

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

|            配置项             | 必填 |                   默认值                    |                                                                      说明                                                                       |
|:--------------------------:| :--: |:----------------------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------:|
|    `NAILONG_MODEL_DIR`     |  否  |          `./`          |                                                             模型的下载位置，默认机器人根目录                                                             |
| `NAILONG_BYPASS_SUPERUSER` |  否  |                  `True`                  |                                                                是否不检查超级用户发送的图片                                                                 |
|   `NAILONG_BYPASS_ADMIN`   |  否  |                  `True`                  |                                                                是否不检查群组管理员发送的图片                                                                |
|    `NAILONG_NEED_ADMIN`    |  否  |                 `False`                  |                                                            当自身不为群组管理员时是否不检查群内所有图片                                                             |
|   `NAILONG_LIST_SCENES`    |  否  |                   `[]`                   |                            聊天场景 ID 黑白名单列表<br />在单级聊天下为该聊天 ID，如 QQ 群号；<br />在多级聊天下为以 `_` 分割的各级聊天 ID，如频道下的子频道或频道下私聊                             |
|    `NAILONG_BLACKLIST`     |  否  |                  `True`                  |                                                                   是否使用黑名单模式                                                                   |
|      `NAILONG_RECALL`      |  否  |                  `True`                  |                                                                    是否撤回消息                                                                     |
|   `NAILONG_MUTE_SECONDS`   |  否  |                   `0`                    |                                                           设置禁言时间，默认为0即不禁言<br/>单位：秒                                                            |
|       `NAILONG_TIP`        |  否  |                `本群禁止发奶龙！`                | 发送的提示，使用 [Alconna 的消息模板](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E4%BD%BF%E7%94%A8%E6%B6%88%E6%81%AF%E6%A8%A1%E6%9D%BF)，可用变量见下 |
|    `NAILONG_FAILED_TIP`    |  否  | `{:Reply($message_id)}呜，不要发奶龙了嘛 🥺 👉👈` |                                                              撤回失败或禁用撤回时发送的提示，同上                                                               |
|      `NAILONG_MODEL`       |  否  |                   `0`                    |                                                    选择需要加载的模型<br/>0：基于分类模型；<br/>1：基于目标检测模型                                                     |

### 消息模板可用变量

| 变量名        | 类型                                                                                                                         | 说明     |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------- |
| `$event`      | [`Event`](https://nonebot.dev/docs/api/adapters/#Event)                                                                      | 当前事件 |
| `$target`     | [`Target`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E6%B6%88%E6%81%AF%E5%8F%91%E9%80%81%E5%AF%B9%E8%B1%A1)     | 事件目标 |
| `$message_id` | `str`                                                                                                                        | 消息 ID  |
| `$msg`        | [`UniMessage`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E9%80%9A%E7%94%A8%E6%B6%88%E6%81%AF%E5%BA%8F%E5%88%97) | 当前消息 |
| `$ss`         | [`Session`](https://github.com/RF-Tar-Railt/nonebot-plugin-uninfo?tab=readme-ov-file#session)                                | 当前会话 |

## 🎉 使用

只要有人发奶龙表情包被识别出来，就会被撤回并提醒。

## 📞 联系
- Nonebot2官方交流群：768887710<span style="color: yellow;">（基础的安装部署问题可在这里询问）</span>

- 人工智能学习交流群：949992679<span style="color: yellow;">（学习交流AI相关技术可以来这里捏）</span>

- 机器人插件学习交流群：200980266<span style="color: yellow;">（机器人BUG模型精度等问题反馈来这里哟）</span>

欢迎大家进群一起学习交流~

## 📝 更新日志

2024.10.29更新：
- 优化了模型精度
- 更新了两个新模型，用户可自行选择其中之一进行推理
- 增加了撤回并禁言功能（可选）