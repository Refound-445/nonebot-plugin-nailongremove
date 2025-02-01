Here's the English translation of the provided text:

---

<!-- markdownlint-disable MD028 MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# Nonebot-Plugin-NaiLongRemove

_✨ A simple plugin based on an AI model~ ✨_

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
        <a href="https://github.com/Refound-445/nonebot-plugin-nailongremove/">简体中文</a> |
        <b>English</b> |
    </p>
</h4>

## 📖 Introduction

### Disclaimer

This plugin is for entertainment and educational purposes only.

### Overview

NaiLongRemove is a simple AI model-based plugin designed to identify "NaiLong" meme images in groups and automatically
remove them.

### Technology

Currently, the plugin supports three models, which can be switched via the configuration file, as detailed in the
configuration section below.  
Users can choose the model that best suits their needs; both models have been optimized for performance, but errors may
still occur to varying degrees. Feedback is welcome!

## 💿 Installation

### Cloud Deployment

- The [run_with_napcat_en.ipynb](https://github.com/Refound-445/nonebot-plugin-nailongremove/blob/main/ipynb/run_with_napcat_en.ipynb) file supports one-click deployment on platforms like Kaggle or Huggingface's Spaces. You can complete the bot deployment simply by clicking "Run" and scanning the QR code!
- Supports [Docker](https://github.com/Refound-445/nonebot-plugin-nailongremove/tree/main/docker) one-click deployment.

### Local Deployment

**If you are new to NoneBot, please refer
to [this guide](https://github.com/Refound-445/nonebot-plugin-nailongremove/blob/main/docs/tutorial_en.md)**

To avoid dependency issues, we've separated the installation methods for using GPU inference from the regular
installation. Choose the one that suits your needs.

#### Using CPU Inference

You can choose one of the following methods.

<details open>
<summary>[Recommended] Install using nb-cli</summary>
Open a terminal in the root directory of the NoneBot2 project and run the following command to install:

```bash
nb plugin install nonebot-plugin-nailongremove
```

</details>

<details>
<summary>Install using a package manager</summary>
Open a terminal in the plugin directory of the NoneBot2 project, and use the appropriate command based on your package manager.

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

Open the `pyproject.toml` file in the root directory of the NoneBot2 project, and add the following to
the `[tool.nonebot]` section:

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_nailongremove"
]
```

</details>

#### Using GPU Inference

<details>
<summary>Click to expand</summary>

> [!NOTE]
> These steps are more technical and complicated, so non-technical users may choose to skip them.  
> In fact, CUDA acceleration has minimal impact on the models used by this plugin, so do not attempt these steps without
> understanding them.

First, enter the Bot virtual environment (if any).

> [!NOTE]
> If you've previously installed the CPU inference version, please uninstall it first:
>
> ```bash
> pip uninstall nonebot-plugin-nailongremove torch torchvision onnxruntime
> ```

Install the base package:

```bash
pip install nonebot-plugin-nailongremove-base
```

Based on your installed CUDA and CuDNN versions (if you have them; if not, install them), follow the official
instructions to install the corresponding dependencies:

- `torch` ([Official guide](https://pytorch.org/get-started/locally/#start-locally))
- `onnxruntime-gpu` ([Official guide](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements))

After installation, configure the plugin to use CUDA for inference:

```properties
NAILONG_ONNX_PROVIDERS=["CUDAExecutionProvider"]
```

Finally, configure NoneBot2 to load the plugin. Open the `pyproject.toml` file in the root directory of the NoneBot2
project, and add the following to the `[tool.nonebot]` section:

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_nailongremove"
]
```

When updating the plugin later, you only need to update the base package. Do not install or update the non-base package:

```bash
pip install nonebot-plugin-nailongremove-base -U
```

</details>

## ⚙️ Configuration

Add the required configurations from the table below to the `.env` file in your NoneBot2 project.

| Configuration Item                     | Required | Default Value                                                                             | Description                                                                                                                                                                                                                                  |
|----------------------------------------|----------|-------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Global Configuration**               |          |                                                                                           |                                                                                                                                                                                                                                              |
| `PROXY`                                | No       | `None`                                                                                    | Proxy address used for downloading model files.                                                                                                                                                                                              |
| **Response Configuration**             |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_BYPASS_SUPERUSER`             | No       | `False`                                                                                   | Whether to bypass checking images sent by superusers.                                                                                                                                                                                        |
| `NAILONG_BYPASS_ADMIN`                 | No       | `False`                                                                                   | Whether to bypass checking images sent by group administrators.                                                                                                                                                                              |
| `NAILONG_NEED_ADMIN`                   | No       | `False`                                                                                   | Whether to skip checking all images in the group when the bot is not an administrator.                                                                                                                                                       |
| `NAILONG_LIST_SCENES`                  | No       | `[]`                                                                                      | List of allowed or disallowed chat scene IDs (e.g., group IDs or channel IDs).                                                                                                                                                               |
| `NAILONG_BLACKLIST`                    | No       | `True`                                                                                    | Whether to use blacklist mode.                                                                                                                                                                                                               |
| `NAILONG_USER_BLACKLIST`               | No       | `[]`                                                                                      | List of user IDs to be blacklisted.                                                                                                                                                                                                          |
| `NAILONG_PRIORITY`                     | No       | `100`                                                                                     | Matcher priority.                                                                                                                                                                                                                            |
| **Behavior Configuration**             |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_RECALL`                       | No       | `["nailong"]`                                                                             | Whether to recall the message                                                                                                                                                                                                                |
| `NAILONG_MUTE_SECONDS`                 | No       | `{"nailong":0}`                                                                           | Set the mute duration. If not set or the duration is 0, no mute will be applied.<br/>Unit: seconds                                                                                                                                           |                                                                                                                                      |
| `NAILONG_TIP`                          | No       | `{"nailong": ["This group prohibits NaiLong images!"]}`                                   | Message to send as a tip, using [Alconna message template](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E4%BD%BF%E7%94%A8%E6%B6%88%E6%81%AF%E6%A8%A1%E6%9D%BF) with custom variables.                                              |
| `NAILONG_FAILED_TIP`                   | No       | `{"nailong": ["{:Reply($message_id)} Oh no, please don't send NaiLong images! 🥺 👉👈"]}` | Message sent when recalling fails or when recalling is disabled.                                                                                                                                                                             |
| `NAILONG_CHECK_ALL_FRAMES`             | No       | `False`                                                                                   | Specifies whether to check all frames in the image when using model 1. Requires setting `NAILONG_CHECK_MODE` to 0. When enabled, the `$checked_result` variable in the message template will return a GIF if the original image is animated. |
| `NAILONG_CHECK_RATE`                   | No       | `0.8`                                                                                     | When checking all frames of an image, the image will only be recalled or processed if a certain proportion of the frames meet the detection criteria.                                                                                        |
| `NAILONG_CHECK_MODE`                   | No       | `0`                                                                                       | Selects the detection method for GIF animations.<br/>0. Check all frames<br/>1. Check only the first frame<br/>2. Random frame sampling                                                                                                      |
| **Similarity Detection Configuration** |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_SIMILARITY_ON`                | No       | `False`                                                                                   | Specifies whether to enable similarity detection on local storage before processing images.                                                                                                                                                  |
| `NAILONG_SIMILARITY_MAX_STORAGE`       | No       | `10`                                                                                      | Maximum number of errored images stored locally. When the limit is reached, older images will be compressed and uploaded to the database, but it won’t affect previously stored images.                                                      |
| `NAILONG_HF_TOKEN`                     | No       | `None`                                                                                    | Hugging Face Access Token, which allows automatic data upload to Hugging Face and becomes a contributor to the dataset.                                                                                                                      |
| **General Model Configuration**        |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_MODEL_DIR`                    | No       | `./data/nailongremove`                                                                    | The download location for the model.                                                                                                                                                                                                         |
| `NAILONG_MODEL`                        | No       | `1`                                                                                       | Specifies which model to load; available models are listed below.                                                                                                                                                                            |
| `NAILONG_AUTO_UPDATE_MODEL`            | No       | `True`                                                                                    | Specifies whether to automatically update the model.                                                                                                                                                                                         |
| `NAILONG_CONCURRENCY`                  | No       | `1`                                                                                       | Maximum concurrency number for identifying frames of animated images.                                                                                                                                                                        |
| `NAILONG_ONNX_PROVIDERS`               | No       | `["CPUExecutionProvider"]`                                                                | List of providers used for loading ONNX models; please refer to installation documentation above.                                                                                                                                            |
| **Model 1 Specific Configuration**     |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_MODEL1_TYPE`                  | No       | `tiny`                                                                                    | The model type used for model 1; options are `tiny` / `m`.                                                                                                                                                                                   |
| `NAILONG_MODEL1_YOLOX_SIZE`            | No       | `None`                                                                                    | For model 1, custom input sizes may be changed.                                                                                                                                                                                              |
| **Model 2 Specific Configuration**     |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_MODEL2_ONLINE`                | No       | `False`                                                                                   | For model 2, specifies whether to enable online inference; this mode is currently not suitable with `NAILONG_CHECK_MODE` set to 0.                                                                                                           |
| **Model 1&2 Specific Configuration**   |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_MODEL1_SCORE`                 | No       | `{"nailong": 0.5}`                                                                        | Confidence threshold for models 1&2; range is `0` ~ `1`. Values can be customized according to labels; set the corresponding threshold for detection, setting it to `null` or leaving it blank will ignore that label.                       |
| **Miscellaneous Configuration**        |          |                                                                                           |                                                                                                                                                                                                                                              |
| `NAILONG_GITHUB_TOKEN`                 | No       | `None`                                                                                    | GitHub Access Token; can be filled in to address issues with model downloads or updates.                                                                                                                                                     |

### Available Models

- `0`: Inference trained on the Renet50 image classification model, thanks
  to [@spawner1145](https://github.com/spawner1145) for providing the model, original
  link: [spawner1145/NailongRecognize](https://github.com/spawner1145/NailongRecognize.git)
- `1`: Inference trained on the YOLOX object detection model, thanks to [@NKXingXh](https://github.com/nkxingxh) for
  providing the model, original link: [nkxingxh/NailongDetection](https://github.com/nkxingxh/NailongDetection)
- `2`: Inference trained on the YOLOv11 object detection model, thanks to [@Hakureirm](https://github.com/Hakureirm) for
  providing the model, original link: [Hakureirm/NailongKiller](https://huggingface.co/Hakureirm/NailongKiller)
- `3`: Inference trained on the YOLOv11 object detection model, thanks to [@Threkork](https://github.com/Threkork) for
  providing the model, original
  link: [Threkork/kovi-plugin-check-alllong](https://github.com/Threkork/kovi-plugin-check-alllong), it is recommended
  to set `{"nailong": 0.78}` in the `NAILONG_MODEL1_SCORE` configuration, and `NAILONG_MODEL1_YOLOX_SIZE`
  to `[640,640]`.

### Available Variables in Message Templates

| Variable Name     | Type                                                                                                                         | Description                                                                                          |
|-------------------|------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `$event`          | [`Event`](https://nonebot.dev/docs/api/adapters/#Event)                                                                      | The current event                                                                                    |
| `$target`         | [`Target`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E6%B6%88%E6%81%AF%E5%8F%91%E9%80%81%E5%AF%B9%E8%B1%A1)     | The target of the event                                                                              |
| `$message_id`     | `str`                                                                                                                        | The message ID                                                                                       |
| `$msg`            | [`UniMessage`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E9%80%9A%E7%94%A8%E6%B6%88%E6%81%AF%E5%BA%8F%E5%88%97) | The current message                                                                                  |
| `$ss`             | [`Session`](https://github.com/RF-Tar-Railt/nonebot-plugin-uninfo?tab=readme-ov-file#session)                                | The current session                                                                                  |
| `$checked_result` | [`Image`](https://nonebot.dev/docs/best-practice/alconna/uniseg#%E9%80%9A%E7%94%A8%E6%B6%88%E6%81%AF%E6%AE%B5)               | The image after selecting the corresponding target, exists only when the model is configured as `1`. |

## 🎉 Usage

Whenever a "NaiLong" meme is recognized, it will be retracted and notified.

To store errored images locally (for `SUPERUSERS`): Send "This is [type]"+image, for example: "This is nailong+image",
and it will be automatically stored locally. When similarity detection is on, in the next image check, it will
prioritize recognizing the images already stored locally.

## 📞 Contact

- [Plugin Learning Group](https://qm.qq.com/q/o6x7IEZyO4): 200980266 (For installation, deployment, robot bugs, model
  accuracy issues, feedback here)
- [Plugin Performance Testing Group](https://qm.qq.com/q/7MMizTMMV2): 829463462 (This group has deployed bots for
  testing existing model performance)
- [AI Learning Group](https://qm.qq.com/q/xdRGrt3y3C): 949992679 (Join for learning and discussing AI-related
  technologies)

Welcome everyone to join the group for learning and exchange!

## 📝 Changelog

### 2.3.6

- Fixed some SSL connection errors

### Minor Update

- Added the [run_with_napcat_en.ipynb](https://github.com/Refound-445/nonebot-plugin-nailongremove/blob/main/ipynb/run_with_napcat_en.ipynb) file, which supports one-click deployment on platforms like Kaggle or Huggingface's Spaces. You can complete the bot deployment simply by clicking "Run" and scanning the QR code!
- Added [Docker](https://github.com/Refound-445/nonebot-plugin-nailongremove/tree/main/docker) one-click deployment.
### 2.3.5

- The update adds a feature to select a mute tag, allowing users to choose whether to mute or recall the processing for
  different types of images.
- A new configuration option, `NAILONG_CHECK_RATE`, has been added. When detecting all frames of an animated image, this
  optional configuration allows success in judgment when the proportion of frames containing the "nailong" frame reaches
  a certain threshold.

### 2.3.4

- Added `model3` to `NAILONG_MODEL`, a model trained based on YOLOv11. It is recommended to set `{"nailong": 0.78}` in
  the `NAILONG_MODEL1_SCORE` configuration, and `NAILONG_MODEL1_YOLOX_SIZE` to `[640,640]`.
- Updated default values for configuration
  items: `NAILONG_BYPASS_SUPERUSER` -> `False`, `NAILONG_BYPASS_ADMIN` -> `False`.

### 2.3.3

- Optimized temporary processing solutions to reduce performance pressure and improve speed (the vector library faiss
  also supports GPU processing, but it is not recommended for non-professionals to use GPU due to the complex
  installation process).
- Added `NAILONG_HF_TOKEN` to automatically upload errored images to the Hugging Face dataset.
- Changed the formats of the configuration items `NAILONG_TIP` and `NAILONG_FAILED_TIP`, allowing random response
  messages. When the corresponding value is an empty list `[]`, only the image will be checked (or the mute/revoke
  action will be performed) without returning a message.

### 2.3.2

- Updated the three frame processing modes for GIFs. You can choose through `NAILONG_CHECK_MODE`.
- Updated the temporary handling for errored images. By enabling `NAILONG_SIMILARITY_ON`, local storage similarity
  matching can be used. Additionally, by sending "This is [type]"+image through `SUPERUSERS`, errored images can be
  saved to local records.
- Added `model2` to `NAILONG_MODEL`, which is based on the YOLOv11-trained model. Currently, it only supports Nailong
  recognition.

### 2.3.1

- Modified plugin dependencies to avoid some issues that affected the installation process. Please refer to the
  installation documentation for more details.
    - Corresponding configuration changes: Removed the `NAILONG_ONNX_TRY_TO_USE_GPU` configuration item and added
      the `NAILONG_ONNX_PROVIDERS` configuration item.

### 2.3.0

- Added support for checking all frames in a GIF and re-encapsulating the results into a new GIF. This is disabled by
  default. The `$checked_image` variable has been deprecated, and a new `$checked_result` variable has been added.
- The input size for model 1 can now be automatically configured based on the model type, but if specified in the
  configuration, it will be used as the priority.
- Supported processing of images containing other tags. Some configuration items now allow custom values based on the
  tags.
- Added a user blacklist.
- The default model has been changed to 1.

### 2.2.1

- Optimized model auto-update (possibly a reverse optimization).

### 2.2.0

- Renamed the configuration item `NAILONG_YOLOX_SIZE` to `NAILONG_MODEL1_YOLOX_SIZE`.
- Model 1 can now automatically get the latest version, and you can also choose the model type through configuration.
- Model 1 can now control the confidence threshold for recognition via configuration.
- When loading the ONNX model, the system will attempt to use GPU by default. If it fails, a warning will be shown. If
  you don't want to see the warning, you can refer to the above to disable the corresponding configuration.

### 2.1.4

- Fixed a bug where the `NAILONG_NEED_ADMIN` configuration was not effective.

### 2.1.3

- Fixed a bug where the group manager and superuser settings were ignored.

### 2.1.2

- Refactored some code and fixed potential bugs.

### 2.1.1

- Added the `$checked_image` variable.

### 2.1.0

- Download models from the original repository.

### 2.0.0

- Refactored the plugin to support multiple platforms.
- Updated two new models and optimized model accuracy. Users can choose one of them for inference.
- Added features like mute, group blacklist and whitelist, optional admin detection disablement.
- Added an option for auto-updating the model.
