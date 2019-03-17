#ヒストグラム比較
from compare import compare, compare_using_cache
import falcon
import io
import json
from falcon_multipart.middleware import MultipartMiddleware
from PIL import Image
import cv2
import numpy as np

image_hists = {}
jsn = None
def add_image_hists(title, img_path):
    comparing_img = cv2.imread(img_path)
    comparing_img = cv2.cvtColor(comparing_img, cv2.COLOR_BGR2HSV)
    channels = (0, 1, 2)
    hist_size = 256
    ranges = (0, 256)
    tmp = []
    hists = []
    for channel in channels:
        comparing_hist = cv2.calcHist([comparing_img], [channel], None, [hist_size], ranges)
        hists.append(comparing_hist)
    image_hists[title] = hists
    

def load_json(file_path):
    global jsn
    with open(file_path) as f:
        jsn = json.load(f)
        for item in jsn:
            title = item["title"]
            img_path = item["image_path"]
            add_image_hists(title, img_path)
            
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
        target_img = cv2.cvtColor(target_img, cv2.COLOR_RGB2HSV)
        scores = {}
        for title in image_hists:
            scores[title] = compare_using_cache(target_img, image_hists[title])
        max_score_and_title = None
        for title in scores:
            if max_score_and_title is None or max_score_and_title[0] < scores[title]:
                max_score_and_title = (scores[title], title)
        res.body = json.dumps({
            "title": max_score_and_title[1],
            "score": max_score_and_title[0],
            "materials": getMaterials(max_score_and_title[1]),
            "image_url": getImageUrl(max_score_and_title[1])
        }, ensure_ascii=False)
        print("飲み物：" + max_score_and_title[1])
        print("確率：" + str(max_score_and_title[0]))
        print("原材料：" + ", ".join(getMaterials(max_score_and_title[1])))




load_json("./data.json")
        
app = falcon.API(middleware=[MultipartMiddleware()])

app.add_route("/", DrinkRecAPI())
