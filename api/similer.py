import os
from PIL import Image
import imagehash

import cv2
import numpy as np
import matplotlib.pyplot as plt

def image_show(img_1, img_2):
    img_1 = cv2.imread(img_1)
    img_2 = cv2.imread(img_2)
    plt.figure(figsize=(20, 15))
    plt.subplots_adjust(wspace=0.0, hspace=0.0)
        
    plt.imshow(img_1)
    plt.imshow(img_2)


userpath = './thum'  # 検索するパス

image_files = []
f = [os.path.join(userpath, path) for path in os.listdir(userpath)]
for i in f:
    if i.endswith('.jpg') or i.endswith('.png'):
        image_files.append(i)

imgs = {}
img_hashs = []
for img in sorted(image_files):
    hash = imagehash.average_hash(Image.open(img))
    img_hashs.append({"hash":hash, "path": img})
    if hash in imgs:
        print('Similar image :', img, imgs[hash])
    else:
        imgs[hash] = img

for i in img_hashs:
    for j in img_hashs:
        hash_diff = i["hash"]-j["hash"]
        if i["path"] == j["path"]:
            break
        elif hash_diff < 5:
            print(hash_diff,i["path"],j["path"])
            image_show(i["path"],j["path"])




