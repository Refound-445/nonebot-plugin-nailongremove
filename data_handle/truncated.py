import glob
from PIL import Image
paths = glob.glob("nailongClassification/train/*/*.jpg")
for path in list(paths):
    try:
        Image.open(path).load()
    except Exception as e:
        print(f"{path}:", e)

