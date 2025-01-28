<!-- markdownlint-disable MD028 MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# Nonebot-Plugin-NaiLongRemove

_✨ 一个基于 AI 模型的简单插件~ ✨_

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

<h4 align="center">
    <p>
        <b>简体中文</b> |
        <a href="https://github.com/Refound-445/nonebot-plugin-nailongremove/blob/main/i18n/README_en.md">English</a> |
    </p>
</h4>

## 📖 介绍

### 声明

本插件仅供娱乐和学习交流。

### 简介

NaiLongRemove 是一款由简单的 AI 模型建立的奶龙识别插件，可以识别群中的奶龙表情包并撤回该表情。

### 技术

目前插件支持三种模型，可通过配置文件更换，详见文档下方配置一节。  
用户可以根据需要自行选择心仪的模型，两个模型性能都已经经过优化，但仍可能会有不同程度的误差，也欢迎各位继续反馈给我们~

## 💿 安装

### 1.云部署

- [run_with_napcat.ipynb](https://github.com/Refound-445/nonebot-plugin-nailongremove/blob/main/ipynb/run_with_napcat.ipynb)文件，支持Kaggle或者Huggingface的Space等一键部署，仅需点击运行和扫码即可完成bot部署！
- 支持[Docker](https://github.com/Refound-445/nonebot-plugin-nailongremove/tree/main/docker)一键部署

### 2.本地部署

**如果你从来没接触过
NoneBot，请查看 [这个文档](https://github.com/Refound-445/nonebot-plugin-nailongremove/blob/main/docs/tutorial.md)**

为避免依赖问题，我们把使用 GPU 推理的插件安装方式与普通安装分开了，供有需要的用户选择安装

#### 使用 CPU 推理

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

#### 使用 GPU 推理

<details>
<summary>点击展开</summary>

> [!NOTE]
> 以下操作比较专业及繁琐，非专业用户可以不考虑使用  
> 实际上对于本插件使用的模型使用 CUDA 加速效果不大，不要什么都不懂就犟着要来搞这些

先进入 Bot 虚拟环境（如果有）

> [!NOTE]
> 如果你以前安装了使用 CPU 推理的包，请先卸载
>
> ```bash
> pip uninstall nonebot-plugin-nailongremove torch torchvision onnxruntime
> ```

安装底包

```bash
pip install nonebot-plugin-nailongremove-base
```

根据你安装的 CUDA 与 CuDNN 版本（如果有装，没有就去装），按照官网说明安装对应版本的以下依赖：

- `torch`（[官网说明](https://pytorch.org/get-started/locally/#start-locally)）
- `onnxruntime-gpu`（[官网说明](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements)）

安装完后配置插件使用 CUDA 进行推理

```properties
NAILONG_ONNX_PROVIDERS=["CUDAExecutionProvider"]
```

最后配置让 nonebot2 加载插件  
打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_nailongremove"
]
```

之后更新插件的话，进入虚拟环境只更新底包即可，不要安装及更新不带 base 的包

```bash
pip install nonebot-plugin-nailongremove-base -U
```

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 文件中添加下表中的必填配置

|               配置项                | 必填 |                            默认值                            |                                                                                                                 说明                                                                                                                 |
|:--------------------------------:|:--:|:---------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|             **全局配置**             |    |                                                           |                                                                                                                                                                                                                                    |
|             `PROXY`              | 否  |                          `None`                           |                                                                                                          下载模型等文件时使用的代理地址                                                                                                           |
|             **响应配置**             |    |                                                           |                                                                                                                                                                                                                                    |
|    `NAILONG_BYPASS_SUPERUSER`    | 否  |                          `False`                          |                                                                                                           是否不检查超级用户发送的图片                                                                                                           |
|      `NAILONG_BYPASS_ADMIN`      | 否  |                          `False`                          |                                                                                                          是否不检查群组管理员发送的图片                                                                                                           |
|       `NAILONG_NEED_ADMIN`       | 否  |                          `False`                          |                                                                                                       当自身不为群组管理员时是否不检查群内所有图片                                                                                                       |
|      `NAILONG_LIST_SCENES`       | 否  |                           `[]`                            |                                                                       聊天场景 ID 黑白名单列表<br />在单级聊天下为该聊天 ID，如 QQ 群号；<br />在多级聊天下为以 `_` 分割的各级聊天 ID，如频道下的子频道或频道下私聊                                                                       |
|       `NAILONG_BLACKLIST`        | 否  |                          `True`                           |                                                                                                             是否使用黑名单模式                                                                                                              |
|     `NAILONG_USER_BLACKLIST`     | 否  |                           `[]`                            |                                                                                                            用户 ID 黑名单列表                                                                                                             |
|        `NAILONG_PRIORITY`        | 否  |                           `100`                           |                                                                                                            Matcher 优先级                                                                                                             |
|             **行为配置**             |    |                                                           |                                                                                                                                                                                                                                    |
|         `NAILONG_RECALL`         | 否  |                       `["nailong"]`                       |                                                                                                               是否撤回消息                                                                                                               |
|      `NAILONG_MUTE_SECONDS`      | 否  |                      `{"nailong":0}`                      |                                                                                                  设置禁言时间，未被设置或者设置时间为0即不禁言<br/>单位：秒                                                                                                  |
|          `NAILONG_TIP`           | 否  |                `{"nailong": ["本群禁止发奶龙！"]}`                | 发送的提示，使用 [Alconna 的消息模板](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E4%BD%BF%E7%94%A8%E6%B6%88%E6%81%AF%E6%A8%A1%E6%9D%BF)，可用变量见下，可以根据标签自定义对应值，随机发送列表其中一条消息，<br/>如遇其中没有的标签会回退到 `nailong`<br/>如果对应值为空列表`[]`，则会检测而不会发送消息 |
|       `NAILONG_FAILED_TIP`       | 否  | `{"nailong": ["{:Reply($message_id)}呜，不要发奶龙了嘛 🥺 👉👈"]}` |                                                                                                         撤回失败或禁用撤回时发送的提示，同上                                                                                                         |
|    `NAILONG_CHECK_ALL_FRAMES`    | 否  |                          `False`                          |                                                                   使用模型 1 时是否检查图片中的所有帧，需要同时设置`NAILONG_CHECK_MODE`为0，启用该项后消息模板中的 `$checked_result` 变量当原图为动图时会变为动图                                                                    |
|       `NAILONG_CHECK_RATE`       | 否  |                           `0.8`                           |                                                                                                 检查图片中的所有帧时，当被检测到的图片满足一定比例时才会被撤回等处理                                                                                                 |
|       `NAILONG_CHECK_MODE`       | 否  |                            `0`                            |                                                                                        选择对GIF动图的检测方式<br/>0.检测所有帧<br/>1.只检测第一帧<br/>2.随机抽帧检测                                                                                         |
|           **相似度检测配置**            |    |                                                           |                                                                                                                                                                                                                                    |
|     `NAILONG_SIMILARITY_ON`      | 否  |                          `False`                          |                                                                                                       是否启用处理图片前对本地存储进行相似度检测                                                                                                        |
| `NAILONG_SIMILARITY_MAX_STORAGE` | 否  |                           `10`                            |                                                                                                本地存储报错图片上限，到达上限会压缩并上传数据库，但并不影响之前的存储                                                                                                 |
|        `NAILONG_HF_TOKEN`        | 否  |                          `None`                           |                                                                                           Hugging Face Access Token，自动上传数据到hf，并成为数据集贡献者                                                                                            |
|            **模型通用配置**            |    |                                                           |                                                                                                                                                                                                                                    |
|       `NAILONG_MODEL_DIR`        | 否  |                  `./data/nailongremove`                   |                                                                                                              模型的下载位置                                                                                                               |
|         `NAILONG_MODEL`          | 否  |                            `1`                            |                                                                                                          选择需要加载的模型，可用模型见下                                                                                                          |
|   `NAILONG_AUTO_UPDATE_MODEL`    | 否  |                          `True`                           |                                                                                                              是否自动更新模型                                                                                                              |
|      `NAILONG_CONCURRENCY`       | 否  |                            `1`                            |                                                                                                     当图片为动图时，针对该图片并发识别图片帧的最大并发数                                                                                                     |
|     `NAILONG_ONNX_PROVIDERS`     | 否  |                `["CPUExecutionProvider"]`                 |                                                                                                加载 onnx 模型使用的 provider 列表，请参考上方安装文档                                                                                                 |
|          **模型 1 特定配置**           |    |                                                           |                                                                                                                                                                                                                                    |
|      `NAILONG_MODEL1_TYPE`       | 否  |                          `tiny`                           |                                                                                                    模型 1 使用的模型类型，可用 `tiny` / `m`                                                                                                    |
|   `NAILONG_MODEL1_YOLOX_SIZE`    | 否  |                          `None`                           |                                                                                                       针对模型 1，自定义模型输入可能会有尺寸更改                                                                                                       |
|          **模型 2 特定配置**           |    |                                                           |                                                                                                                                                                                                                                    |
|     `NAILONG_MODEL2_ONLINE`      | 否  |                          `False`                          |                                                                                           针对模型 2，是否启用在线推理，此模式目前不适用`NAILONG_CHECK_MODE`为0                                                                                           |
|         **模型 1&2 特定配置**          |    |                                                           |                                                                                                                                                                                                                                    |
|      `NAILONG_MODEL1_SCORE`      | 否  |                    `{"nailong": 0.5}`                     |                                                                            模型 1&2 置信度阈值，范围 `0` ~ `1`，可以根据标签自定义对应值，设置对应标签的阈值以检测该标签，设为 `null` 或者不填可以忽略该标签                                                                            |
|             **杂项配置**             |    |                                                           |                                                                                                                                                                                                                                    |
|      `NAILONG_GITHUB_TOKEN`      | 否  |                          `None`                           |                                                                                               GitHub Access Token，遇到模型下载或更新问题时可尝试填写                                                                                                |

### 可用模型

- `0`：基于 Renet50 图像分类模型训练推理，感谢 [@spawner1145](https://github.com/spawner1145)
  提供的模型，原链接：[spawner1145/NailongRecognize](https://github.com/spawner1145/NailongRecognize.git)
- `1`：基于 YOLOX 目标检测模型训练推理，感谢 [@NKXingXh](https://github.com/nkxingxh)
  提供的模型，原链接：[nkxingxh/NailongDetection](https://github.com/nkxingxh/NailongDetection)
- `2`：基于 YOLOv11 目标检测模型训练推理，感谢 [@Hakureirm](https://github.com/Hakureirm)
  提供的模型，原链接：[Hakureirm/NailongKiller](https://huggingface.co/Hakureirm/NailongKiller)
- `3`：基于 YOLOv11 目标检测模型训练推理，感谢 [@Threkork](https://github.com/Threkork)
  提供的模型，原链接：[Threkork/kovi-plugin-check-alllong](https://github.com/Threkork/kovi-plugin-check-alllong)
  ，建议`NAILONG_MODEL1_SCORE`配置项中设置`{"nailong": 0.78}`，`NAILONG_MODEL1_YOLOX_SIZE`设置为`[640,640]`

### 消息模板可用变量

| 变量名               | 类型                                                                                                                           | 说明                          |
|-------------------|------------------------------------------------------------------------------------------------------------------------------|-----------------------------|
| `$event`          | [`Event`](https://nonebot.dev/docs/api/adapters/#Event)                                                                      | 当前事件                        |
| `$target`         | [`Target`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E6%B6%88%E6%81%AF%E5%8F%91%E9%80%81%E5%AF%B9%E8%B1%A1)     | 事件目标                        |
| `$message_id`     | `str`                                                                                                                        | 消息 ID                       |
| `$msg`            | [`UniMessage`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E9%80%9A%E7%94%A8%E6%B6%88%E6%81%AF%E5%BA%8F%E5%88%97) | 当前消息                        |
| `$ss`             | [`Session`](https://github.com/RF-Tar-Railt/nonebot-plugin-uninfo?tab=readme-ov-file#session)                                | 当前会话                        |
| `$checked_result` | [`Image`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E9%80%9A%E7%94%A8%E6%B6%88%E6%81%AF%E6%AE%B5)               | 框选出对应目标后的图片，仅在模型配置为 `1` 时存在 |

## 🎉 使用

只要有人发奶龙表情包被识别出来，就会被撤回并提醒。

本地存储报错图片（限`SUPERUSERS`）：发送"这是[种类]"+图片，例如："这是nailong+图片"，便会自动存储到本地，开启相似度检测后，在下一次检测图片会优先识别本地已存储的图片。

## 📞 联系

- [机器人插件学习交流群](https://qm.qq.com/q/o6x7IEZyO4)：200980266（安装部署，机器人 BUG 模型精度等问题反馈来这里哟）
- [插件性能测试群](https://qm.qq.com/q/7MMizTMMV2)：829463462（此群有已部署bot，可以测试当前已有模型的性能）
- [人工智能学习交流群](https://qm.qq.com/q/xdRGrt3y3C)：949992679（学习交流 AI 相关技术可以来这里捏）

欢迎大家进群一起学习交流~

## 📝 更新日志

### 小更新

- 增加[run_with_napcat.ipynb](https://github.com/Refound-445/nonebot-plugin-nailongremove/blob/main/ipynb/run_with_napcat.ipynb)文件，支持Kaggle或者Huggingface的Space等一键部署，仅需点击运行和扫码即可完成bot部署！
- 增加[Docker](https://github.com/Refound-445/nonebot-plugin-nailongremove/tree/main/docker)一键部署

### 2.3.5

- 更新可以增加禁言标签选择功能，分别对不同种类的图片选择是否禁言或者撤回处理
- 增加配置项`NAILONG_CHECK_RATE`，检测动图的全部帧时，可选配置全部帧出现奶龙帧到某个比例时成功判定

### 2.3.4

- `NAILONG_MODEL`加入model3，基于YOLOv11训练的模型，建议`NAILONG_MODEL1_SCORE`
  配置项中设置`{"nailong": 0.78}`，`NAILONG_MODEL1_YOLOX_SIZE`设置为`[640,640]`
- 更新配置项默认值`NAILONG_BYPASS_SUPERUSER`->`False`，`NAILONG_BYPASS_ADMIN`->`False`

### 2.3.3

- 优化临时处理方案，减小性能压力同时提升速度（向量库faiss也支持GPU处理，但非专业人士不推荐使用GPU，因为这个安装过程比较复杂）
- 增加`NAILONG_HF_TOKEN`实现自动将报错图片上传Hugging Face数据集
- 更改配置项`NAILONG_TIP`和`NAILONG_FAILED_TIP`格式，允许随机发送返回消息，并且对应值为空列表`[]`时，仅检测图片（或者禁言撤回）而不会返回消息

### 2.3.2

- 更新对GIF动图的三种帧处理模式，通过`NAILONG_CHECK_MODE`自行选择
- 更新对于报错图片临时处理方案，通过设置`NAILONG_SIMILARITY_ON`开启浏览本地存储相似度匹配，通过`SUPERUSERS`发送"
  这是[种类]"+图片，可将报错图片保存到本地记录
- `NAILONG_MODEL`加入model2，基于YOLOv11训练的模型，目前仅支持奶龙识别

### 2.3.1

- 修改插件依赖以避免一些问题，影响了安装过程，请查看安装文档了解
    - 对应配置项修改：删除配置项 `NAILONG_ONNX_TRY_TO_USE_GPU`，添加配置项 `NAILONG_ONNX_PROVIDERS`

### 2.3.0

- 支持了检查 GIF 中的所有帧并将结果重新封成 GIF，默认禁用，同时弃用 `$checked_image` 变量，新增 `$checked_result` 变量
- 现在模型 1 的输入大小可以根据模型类型自动配置了，但是如果配置项指定了那么会优先使用
- 支持处理含有其他标签的图片了，部分配置项支持根据标签自定义对应值
- 增加用户黑名单
- 默认模型调整至 1

### 2.2.1

- 优化模型自动更新（可能是反向优化）

### 2.2.0

- 重命名配置项 `NAILONG_YOLOX_SIZE` -> `NAILONG_MODEL1_YOLOX_SIZE`
- 模型 1 现可以自动获取最新版本，也可以通过配置选择要使用的模型类型
- 模型 1 现可通过配置项控制识别置信度阈值
- 加载 onnx 模型时会默认尝试使用 GPU，如果失败则会显示一串警告，如果不想看见警告参考上面关闭对应配置

### 2.1.4

- 修复 `NAILONG_NEED_ADMIN` 配置不生效的 Bug

### 2.1.3

- 修复忽略群管与超级用户无效的 Bug

### 2.1.2

- 重构部分代码，修复潜在 Bug

### 2.1.1

- 新增变量 `$checked_image`

### 2.1.0

- 从原仓库下载模型

### 2.0.0

- 重构插件，适配多平台
- 更新了两个新模型，优化了模型精度，用户可自行选择其中之一进行推理
- 增加了禁言、群黑白名单、可选关闭管理员检测等功能
- 增加了自动更新模型可选
