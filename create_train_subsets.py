import shutil
import os
import random

PATH = r'D:\imgs\experiments'
OLD_PATH = r'D:\imgs\train'

images = [f for f in os.listdir(os.path.join(OLD_PATH, 'images')) if '.jpg' in f.lower()]
random.seed(8)
random.shuffle(images)

parts = [0.05, 0.1, 0.2, 0.3, 0.5, 0.8]

i = 0
for p in parts:

    os.mkdir(rf'{PATH}\part{i}')
    os.mkdir(rf'{PATH}\part{i}\images')
    os.mkdir(rf'{PATH}\part{i}\labels')
    files = images[:int(p * len(images))]
    for f in files:
        shutil.copy(os.path.join(OLD_PATH, 'images', f), os.path.join(rf'{PATH}\part{i}', 'images', f))
        shutil.copy(os.path.join(OLD_PATH, 'labels', f).replace('.jpg', '.txt'),
                    os.path.join(rf'{PATH}\part{i}', 'labels', f).replace('.jpg', '.txt'))
    i += 1
