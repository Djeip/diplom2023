from tensorflow.keras.utils import load_img, img_to_array
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
import numpy as np
from sklearn.cluster import KMeans
import os, shutil, glob, os.path
from matplotlib import pyplot as plt

import joblib

from PIL import Image as pil_image

load_img.LOAD_TRUNCATED_IMAGES = True
model = VGG16(weights='imagenet', include_top=False)

# Variables
imdir = r'D:\imgs\train\images'
targetdir = r"D:\imgs\train_cl\images\"

# Loop over files and get features
filelist = glob.glob(os.path.join(imdir, '*.jpg'))
filelist.sort()
featurelist = []
for i, imagepath in enumerate(filelist):
    print("    Status: %s / %s" % (i, len(filelist)), end="\r")
    img = load_img(imagepath, target_size=(224, 224))
    img_data = img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    features = np.array(model.predict(img_data))
    featurelist.append(features.flatten())

X = np.array(featurelist)

distortions = []

kmeanModel = KMeans(n_clusters=36, random_state=0).fit(X)

try:
    os.makedirs(targetdir)
except OSError:
    pass
# Copy with cluster name
print("\n")
for i, m in enumerate(kmeanModel.labels_):
    print("    Copy: %s / %s" %(i, len(kmeanModel.labels_)), end="\r")
    shutil.copy(filelist[i], targetdir + str(m) + "_" + str(i) + ".jpg")


kmeanModel.predict(features.flatten().reshape(1, -1))

joblib.dump(kmeanModel, 'yolo_test/cluster.joblib')
