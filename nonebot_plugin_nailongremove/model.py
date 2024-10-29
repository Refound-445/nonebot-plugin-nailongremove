import cv2
import numpy as np
import torch
from torch import Tensor, nn
from torch.hub import load_state_dict_from_url
from torchvision import transforms

from .config import config
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if config.nailong_model==0:
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
        ],
    )
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)  # 修改最后一层为分类层
    model_filename = "nailong.pth"
    if config.nailong_model_dir.exists():
        model.load_state_dict(
            torch.load(
                config.nailong_model_dir / model_filename,
                weights_only=True,
                map_location=device,
            ),
        )
    else:
        url = f"https://github.com/Refound-445/nonebot-plugin-nailongremove/releases/download/weights/{model_filename}"
        state_dict = load_state_dict_from_url(
            url=url,
            model_dir=str(config.nailong_model_dir),
            map_location=device,
            check_hash=True,
            progress=True,
        )
        model.load_state_dict(state_dict)

    model.eval()
    def check_image(images: list[np.ndarray]) -> bool:
        """
        :param image: OpenCV图像数组。
        :return: 如果图像中有奶龙，返回True；否则返回False。
        """
        for image in images:
            if image.shape[0]<224 or image.shape[1]<224:
                return False
            image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image=cv2.resize(image,(224,224))
            image = transform(image)
            image = image.unsqueeze(0)
            with torch.no_grad():
                output = model(image.to(device))
                _, pred = torch.max(output, 1)
                if pred.item()==1:
                    return True
        return False
elif config.nailong_model==1:
    import os
    from .uniapi.yolox_utils import mkdir, multiclass_nms, demo_postprocess, vis,COCO_CLASSES,preprocess
    import onnxruntime

    model_filename = "nailong_v2.1_m.onnx"
    if not os.path.exists(config.nailong_model_dir/model_filename):
        url = f'https://github.com/Refound-445/nonebot-plugin-nailongremove/releases/download/weights/{model_filename}'
        torch.hub.download_url_to_file(url, model_filename, progress=True)
    session = onnxruntime.InferenceSession(model_filename)
    input_shape = (640, 640)
    def check_image(images: list[np.ndarray]) -> bool:
        """
        :param image: OpenCV图像数组。
        :return: 如果图像中有奶龙，返回True；否则返回False。
        """
        for image in images:
            img, ratio = preprocess(image, input_shape)
            ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}
            output = session.run(None, ort_inputs)
            predictions = demo_postprocess(output[0], input_shape)[0]

            boxes = predictions[:, :4]
            scores = predictions[:, 4:5] * predictions[:, 5:]

            boxes_xyxy = np.ones_like(boxes)
            boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.
            boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.
            boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.
            boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.
            boxes_xyxy /= ratio
            dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.1)
            if dets is not None:
                final_boxes, final_scores, final_cls_inds = dets[:, :4], dets[:, 4], dets[:, 5]
                # image = vis(image, final_boxes, final_scores, final_cls_inds,
                #                  conf=0.3, class_names=COCO_CLASSES)
                for i in range(len(final_scores)):
                    if final_cls_inds[i]==1 and final_scores[i]>0.5:
                        return True
        return False