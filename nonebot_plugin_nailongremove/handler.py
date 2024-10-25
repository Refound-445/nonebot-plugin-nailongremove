import logging

import httpx
import cv2
import numpy as np

from nonebot.rule import Rule
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent
from PIL import Image
import io
from .model import *


logger = logging.getLogger(__name__)
async def download_image(url: str) -> np.ndarray:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            image_data = response.content

            # 将字节数据加载为Pillow图像对象
            image = Image.open(io.BytesIO(image_data))

            # 检查图像格式并处理
            if image.format == 'GIF' and hasattr(image, 'is_animated') and image.is_animated:
                # 处理GIF动图：仅获取第一帧
                image = image.convert("RGB")
                image = image.copy()  # 获取第一帧
            else:
                # 对于非GIF图像（如JPEG）
                image = image.convert("RGB")

            # 将Pillow图像转换为NumPy数组
            image_array = np.array(image)

            # OpenCV通常使用BGR格式，因此需要转换
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

            return image_array



async def group_message_contains_image(event: MessageEvent) -> bool:
    if isinstance(event, GroupMessageEvent) and any(seg.type == 'image' or seg.type=='mface' for seg in event.message):
        return True
    return False


nailong =on_message(rule=Rule(group_message_contains_image))
@nailong.handle()
async def handle_function(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    member_info = await bot.get_group_member_info(group_id=group_id, user_id=event.self_id)  # 管理员检测
    if member_info['role'] != 'admin' and member_info['role'] != 'owner':
        return
    for seg in event.message:
        if seg.type == 'image' or seg.type == 'mface':
            try:
                image_url = seg.data['url']
                image = await download_image(image_url)
                if check_image(image):
                    await bot.call_api('delete_msg', message_id=event.message_id)
                    await bot.send(event, "本群禁止发送奶龙！")
                    logger.info(f"撤回了包含奶龙的图片并发送警告：{image_url}")
                else:
                    logger.debug("Image does not contain monkey.")
            except Exception as e:
                logger.error(f"处理图片时出错：{e}")