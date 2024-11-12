import glob
import os
import shutil

import cv2 as cv
import numpy as np
from PIL import Image
from tqdm import tqdm

# Tips: Only can handle 'GIF' and 'JPEG' files now.
'''
│  image_data_handle.py
│  image_data_handle_self.py
│  sort.py
│
├─input
│  ├─anime
│  │      20241026132655386916.jpg
│  │      frame14_D276EA0B35661E06BE3298D0CEAB301B.jpg
│  │
│  ├─nailong
│  │      1.jpg
│  │      555.jpg
│  │
│  └─others
│          D276EA0B35661E06BE3298D0CEAB301B.gif
│
└─nailong
    ├─anime
    │      20241026132655386916.jpg
    │
    └─nailong
            1.jpg
'''
# root_dir='nailongClassification'
root_dir = 'nailong'
input_dir = 'input'
success_dir = 'success'
failure_dir = 'failure'
dsize = (224, 224)
use_gpu = True
if use_gpu:
    import cupy as cp


def get_similarity(image1: np.ndarray, image2: np.ndarray) -> float:
    if use_gpu:
        image1_gpu = cp.asarray(image1)
        image2_gpu = cp.asarray(image2)

        vector1 = cp.mean(image1_gpu, axis=-1).flatten()
        vector2 = cp.mean(image2_gpu, axis=-1).flatten()

        norm1 = cp.linalg.norm(vector1)
        norm2 = cp.linalg.norm(vector2)

        cosine_similarity = cp.dot(vector1, vector2) / (norm1 * norm2)

        return float(cosine_similarity)
    else:
        vector1 = np.mean(image1, axis=-1).flatten()
        vector2 = np.mean(image2, axis=-1).flatten()

        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)

        cosine_similarity = np.dot(vector1, vector2) / (norm1 * norm2)

        return cosine_similarity


# GIF_to_JPEG
def process_gif_and_save_jpgs(input_gif_path, similarity_threshold=0.85):
    output_dir = os.path.dirname(input_gif_path)
    gif = Image.open(input_gif_path)
    frame_count = [i for i in range(gif.n_frames)]
    while len(frame_count) > 0:
        frame_num1 = frame_count[0]
        frame_count.remove(frame_num1)
        gif.seek(frame_num1)
        frame1 = gif.copy()
        frame1 = frame1.convert('RGB')
        frame1 = np.array(frame1)
        frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)
        frame_filename = os.path.join(output_dir, "frame{}_{}.jpg".format(frame_num1,
                                                                          os.path.basename(input_gif_path).split('.')[
                                                                              0]))
        assert not os.path.exists(frame_filename), f'{frame_filename} already exists'
        cv.imwrite(frame_filename, frame1)
        frame1 = cv.resize(frame1, dsize)
        for frame_num2 in list(frame_count):
            gif.seek(frame_num2)
            frame2 = gif.copy()
            frame2 = frame2.convert('RGB')
            frame2 = np.array(frame2)
            frame2 = cv.cvtColor(frame2, cv.COLOR_BGR2RGB)
            frame2 = cv.resize(frame2, dsize)
            if get_similarity(frame1, frame2) > similarity_threshold:
                frame_count.remove(frame_num2)


path = glob.glob(os.path.join(input_dir, '*/*.gif'))
for img_path in path:
    process_gif_and_save_jpgs(img_path)
    os.remove(img_path)

# Similarity_Test
path = glob.glob(os.path.join(input_dir, '*/*.jpg'))
root_path = glob.glob(os.path.join(root_dir, '*/*.jpg'))
for image_path1 in list(path):
    is_success = True
    for image_path2 in tqdm(list(root_path), desc=f'Processing {image_path1}', unit='file'):
        image1 = cv.imread(image_path1)
        image2 = cv.imread(image_path2)
        image1 = cv.resize(image1, dsize)
        image2 = cv.resize(image2, dsize)
        similarity = get_similarity(image1, image2)
        if similarity > 0.99:
            if not os.path.exists(os.path.join(failure_dir, image_path2.split('\\')[-2], image_path2.split('\\')[-1])):
                os.makedirs(os.path.join(failure_dir, image_path2.split('\\')[-2], image_path2.split('\\')[-1]))
                shutil.copy(image_path2,
                            os.path.join(failure_dir, image_path2.split('\\')[-2], image_path2.split('\\')[-1],
                                         os.path.basename(image_path2)))  # Origin Image
            failure_filename = os.path.join(failure_dir, image_path2.split('\\')[-2], image_path2.split('\\')[-1],
                                            f"{similarity:.2f}-" + os.path.basename(image_path1))
            while os.path.exists(failure_filename):
                failure_filename = f'{failure_filename}-exists'
            shutil.copy(image_path1, failure_filename)
            is_success = False
            break
    if is_success:
        if not os.path.exists(os.path.join(success_dir, image_path1.split('\\')[-2])):
            os.makedirs(os.path.join(success_dir, image_path1.split('\\')[-2]))
        assert not os.path.exists(os.path.join(success_dir, image_path1.split('\\')[-2],
                                               os.path.basename(image_path1))), '{} already exists'.format(
            os.path.join(success_dir, image_path1.split('\\')[-2], os.path.basename(image_path1)))
        shutil.copy(image_path1, os.path.join(success_dir, image_path1.split('\\')[-2], os.path.basename(image_path1)))
        root_path.append(os.path.join(success_dir, image_path1.split('\\')[-2], os.path.basename(image_path1)))
