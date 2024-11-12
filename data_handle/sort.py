import os
import shutil

from PIL import Image


def copy_and_rename_files(source_dir, target_dir, strat_num):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    files = sorted(os.listdir(source_dir))

    files = [f for f in files if os.path.isfile(os.path.join(source_dir, f))]

    for idx, filename in enumerate(files, start=strat_num):
        # file_extension = os.path.splitext(filename)[1]
        old_file_path = os.path.join(source_dir, filename)
        try:
            with Image.open(old_file_path) as img:
                img = img.convert("RGB")
                file_extension = '.jpg'

                new_filename = f"{str(idx).zfill(5)}{file_extension}"
                new_file_path = os.path.join(target_dir, new_filename)
                img.save(new_file_path, "JPEG")
                print(f"Successfully converted:  {filename} -> {new_filename}")
        except Exception as e:
            print(f"Conversion failed:{filename}, Error: {e}")
        # shutil.copy2(old_file_path, new_file_path)


source_dir = 'success'
target_dir = 'temp'
# root_dir='nailongClassification'
root_dir = 'nailong'
dir_paths = [os.path.join(source_dir, i) for i in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, i))]
for dir_path in dir_paths:
    if os.path.exists(os.path.join(root_dir, os.path.split(dir_path)[-1])):
        strat_num = len(os.listdir(os.path.join(root_dir, os.path.split(dir_path)[-1])))
    else:
        strat_num = 0
    copy_and_rename_files(dir_path, os.path.join(target_dir, os.path.split(dir_path)[-1]), strat_num)
