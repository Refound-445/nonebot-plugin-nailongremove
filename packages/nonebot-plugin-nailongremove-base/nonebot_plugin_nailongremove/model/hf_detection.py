import asyncio
import datetime
import itertools
import os

import cv2
import numpy as np
import torch
from cookit import with_semaphore
from nonebot import logger
from nonebot.utils import run_sync
from PIL import Image

from ..config import config, ModelType
from ..frame_source import FrameSource, repack_save
from .utils.common import CheckResult, CheckSingleResult, race_check, similarity_process

if config.nailong_model2_online and config.nailong_model is ModelType.HF_DETECTION:
    import base64
    import io
    import shutil

    from gradio_client import Client, handle_file

    FILENAME = "nailong_yolo11.pt"
    client = Client("Hakureirm/NailongKiller")
    logger.info(f"Using model {FILENAME} online")
else:
    from huggingface_hub import hf_api, hf_hub_download
    from ultralytics import YOLO

    if config.nailong_model is ModelType.HF_DETECTION:
        REPO_ID = "Hakureirm/NailongKiller"
        FILENAME = "nailong_yolo11.pt"
    elif config.nailong_model is ModelType.HF_YOLO:
        REPO_ID = "Threkork/nailong"
        FILENAME = "nailong-2024-10-16.pt"
    else:
        raise NotImplementedError  # never reach here

    model_path = os.path.join(str(config.nailong_model_dir), FILENAME)
    if config.nailong_auto_update_model or not os.path.exists(model_path):
        api = hf_api.HfApi()
        file_path = os.path.join(str(config.nailong_model_dir), FILENAME)
        model_info = api.model_info(REPO_ID)


        def get_file_last_modified_time(file_path):
            try:
                timestamp = os.path.getmtime(file_path)
                last_modified_time = datetime.datetime.fromtimestamp(
                    timestamp,
                    tz=datetime.timezone.utc,
                )
                return last_modified_time
            except FileNotFoundError:
                return None


        local_time = get_file_last_modified_time(file_path)
        if local_time is None or model_info.last_modified >= local_time:
            hf_hub_download(
                repo_id=REPO_ID,
                filename=FILENAME,
                local_dir=config.nailong_model_dir,
            )
            logger.info(f"Update model {FILENAME} successfully!")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = YOLO(model_path).to(device)
    logger.info(f"Using model {FILENAME}")

input_shape = config.nailong_model1_yolox_size or config.nailong_model1_type.yolox_size


@run_sync
def _check_single(frame: np.ndarray, is_gif: bool = False) -> CheckSingleResult:
    if is_gif:
        res = similarity_process(frame)
        if res is not None:
            return CheckSingleResult(ok=res.ok, label=res.label, extra=frame)
        return CheckSingleResult(ok=False, label=None, extra=frame)
    if config.nailong_model2_online:
        input_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if not os.path.exists(
                os.path.join(str(config.nailong_model_dir), "online_temp"),
        ):
            os.makedirs(os.path.join(str(config.nailong_model_dir), "online_temp"))
        image_path = os.path.join(
            str(config.nailong_model_dir),
            "online_temp",
            "temp_{}.jpg".format(
                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            ),
        )
        while os.path.exists(image_path):
            basename = os.path.basename(image_path)
            image_path = os.path.join(
                str(config.nailong_model_dir),
                "online_temp",
                f"exist-{basename}",
            )
        input_image.save(image_path, format="JPEG")
        result_image, result_info = client.predict(
            img=handle_file(image_path),
            api_name="/predict",
        )
        os.remove(image_path)
        if (
                "检测到的目标数量: " in result_info
                and int(result_info.split("检测到的目标数量: ")[1].split("\n")[0]) < 1
        ):
            return CheckSingleResult(ok=False, label=None, extra=frame)
        if isinstance(result_image, str):
            if result_image.startswith("data:image"):
                img_data = base64.b64decode(result_image.split(",")[1])
                img = Image.open(io.BytesIO(img_data))
                result_image = np.array(img)
            else:
                img_data = result_image
                img = Image.open(img_data)
                result_image = np.array(img)
                shutil.rmtree(os.path.dirname(os.path.dirname(img_data)))
        result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
        return CheckSingleResult(ok=True, label="nailong", extra=result_image)
    input_image = Image.fromarray(frame)
    original_size = input_image.size

    max_size = max(original_size)
    pad_w = max_size - original_size[0]
    pad_h = max_size - original_size[1]

    padded_img = Image.new("RGB", (max_size, max_size), (114, 114, 114))
    padded_img.paste(input_image, (pad_w // 2, pad_h // 2))

    img_array = np.array(padded_img)

    results = model.predict(
        img_array,
        conf=config.nailong_model1_score["nailong"],
        iou=0.5,
        max_det=100,
        verbose=False,
    )
    cls = results[0].boxes.cls
    if len(cls) < 1:
        return CheckSingleResult(ok=False, label=None, extra=frame)
    result_img = results[0].plot()

    if pad_w > 0 or pad_h > 0:
        result_img = result_img[
                     pad_h // 2: pad_h // 2 + original_size[1],
                     pad_w // 2: pad_w // 2 + original_size[0],
                     ]
    return CheckSingleResult(ok=True, label="nailong", extra=result_img)


async def check_single(frame: np.ndarray, is_gif: bool = False) -> CheckSingleResult:
    if is_gif:
        res = await _check_single(frame, True)
        return CheckSingleResult(
            ok=res.ok,
            label=res.label,
            extra=res.extra,
        )
    res = await _check_single(frame)
    return CheckSingleResult(
        ok=res.ok,
        label=res.label,
        extra=res.extra,
    )


async def check(source: FrameSource) -> CheckResult:
    label = None
    extra_vars = {}
    if config.nailong_check_all_frames and config.nailong_check_mode == 0:
        if config.nailong_similarity_on:
            tem_source = itertools.tee(source, 1)[0]
            sem = asyncio.Semaphore(config.nailong_concurrency)
            results = await asyncio.gather(
                *(
                    with_semaphore(sem)(check_single)(frame, True)
                    for frame in tem_source
                ),
            )
            ok = True if sum(1 for r in results if r.ok) / len(results) >= config.nailong_check_rate else False
        else:
            ok = False
        if not ok:
            sem = asyncio.Semaphore(config.nailong_concurrency)
            results = await asyncio.gather(
                *(with_semaphore(sem)(check_single)(frame) for frame in source),
            )
            ok = True if sum(1 for r in results if r.ok) / len(results) >= config.nailong_check_rate else False
        if ok:
            all_labels = {r.label for r in results if r.label}
            label = next(
                (x for x in config.nailong_model1_score if x in all_labels),
                None,
            )
            extra_vars["$checked_result"] = await repack_save(
                source,
                (r.extra for r in results),
            )
    else:
        res = await race_check(check_single, source)
        ok = bool(res)
        if res:
            label = res.label
            extra_vars["$checked_result"] = await repack_save(
                source,
                iter((res.extra,)),
            )
    return CheckResult(ok, label, extra_vars)
