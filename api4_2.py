#テンプレートマッチング(種類を絞る）
import falcon
import io
import json
from falcon_multipart.middleware import MultipartMiddleware
from PIL import Image
import cv2
import numpy as np
import imagehash
from statistics import mean
import glob
import os

jsn = None
images = {}

def add_image(title, img_path):
    images[title] = cv2.imread(img_path)


def match(target_img, candidate_img):
    result = cv2.matchTemplate(target_img, candidate_img, cv2.TM_CCOEFF_NORMED)
    threshold = 0.4
    loc = np.where(result >= threshold)
    return (loc[0].shape[0] > 0)

def search(target_img, length):
    top_images = []
    for title in images:
        image = images[title]
        result = cv2.matchTemplate(target_img, image, cv2.TM_CCOEFF_NORMED)
        for threshold in range(0, 100, 5)[::-1]:
            threshold /= 100
            loc = np.where(result >= threshold)
            if loc[0].shape[0] > 0:
                top_images.append((title, threshold))
    print(top_images)
    top_images = sorted(top_images, key=lambda x: x[1])
    top_images = list(reversed(top_images))
    top_images = top_images[0:length]
    return top_images




def load_json(file_path):
    global jsn
    with open(file_path) as f:
        jsn = json.load(f)
        img_paths = glob.glob("./small/*.jpg")   
        for img_path in img_paths:
            title = os.path.basename(img_path).split(".")[0]
            add_image(title, img_path)
            
def getMaterials(title):
    item = None
    for drink in jsn:
        if drink["title"] == title:
            item = drink
    if item is None:
        return None
    return item["materials"]

def getImageUrl(title):
    item = None
    for drink in jsn:
        if drink["title"] == title:
            item = drink
    if item is None:
        return None
    return item["img"]

    

class DrinkRecAPI(object):
    def on_post(self, req, res):
        data = req.get_param("file").file.read()
        pil_img = Image.open(io.BytesIO(data))
        target_img = np.asarray(pil_img)
        target_img = cv2.cvtColor(target_img, cv2.COLOR_BGR2RGB)
        result = search(target_img, 3)
        result = list(map(lambda x: { "title": x[0], "score": x[1], "materials": getMaterials(x[0]), "img": getImageUrl(x[0])}, result))

        res.body = json.dumps(result, ensure_ascii=False)




load_json("./data.json")
        
app = falcon.API(middleware=[MultipartMiddleware()])

app.add_route("/", DrinkRecAPI())
