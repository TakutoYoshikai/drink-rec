#imagehashとヒストグラム比較を合わせる
from compare import compare, compare_using_cache
import falcon
import io
import json
from falcon_multipart.middleware import MultipartMiddleware
from PIL import Image
import cv2
import numpy as np
import imagehash
from statistics import mean

jsn = None
img_hashes = {}
img_hist_list = {}


    
def add_image_hist(title, img_path):
    img = cv2.imread(img_path)
    channels = (0, 1, 2)
    hist_size = 256
    ranges = (0, 256)
    hists = []
    for channel in channels:
        hist = cv2.calcHist([img], [channel], None, [hist_size], ranges)
        hists.append(hist)
    img_hist_list[title] = hists

    
    
def add_image_hash(title, img_path):
    hs = imagehash.average_hash(Image.open(img_path))
    img_hashes[title] = hs

def get_scores_by_hash(pil_img):
    target_hash = imagehash.average_hash(pil_img)
    min_haming = 100000
    min_title = None
    scores = {}
    for title in img_hashes:
        comparing_hash = img_hashes[title]
        haming = target_hash - comparing_hash
        haming = (100 - haming) / 100
        scores[title] = haming
    return scores

def get_scores_by_hist(np_img):
    channels = (0, 1, 2)
    hist_size = 256
    ranges = (0, 256)
    tmp = []
    scores = {}
    for img_title in img_hist_list:
        comparing_hists = img_hist_list[img_title]
        for channel in channels:
            target_hist = cv2.calcHist([np_img], [channel], None, [hist_size], ranges)
            tmp.append(cv2.compareHist(target_hist, comparing_hists[channel], 0))
        score = mean(tmp) * 10.0
        print(score)
        scores[img_title] = score
    return scores

def get_titles_and_total_scores(pil_img):
    np_img = np.asarray(pil_img)
    hist_scores = get_scores_by_hist(np_img)
    hash_scores = get_scores_by_hash(pil_img)
    result = []
    for title in hist_scores:
        result.append((title, (hist_scores[title] + hash_scores[title])))
    return sorted(result, key=lambda x:x[1])


def load_json(file_path):
    global jsn
    with open(file_path) as f:
        jsn = json.load(f)
        for item in jsn:
            title = item["title"]
            img_path = item["image_path"]
            add_image_hash(title, img_path)
            add_image_hist(title, img_path)
            
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
        pil_img = Image.fromarray(np.uint8(target_img))
        title_score_list = get_titles_and_total_scores(pil_img)
        result_title = title_score_list[-1][0]
        result_score = title_score_list[-1][1]
        res.body = json.dumps({
            "title": result_title,
            "score": result_score,
            "materials": getMaterials(result_title),
            "image_url": getImageUrl(result_title)
        }, ensure_ascii=False)




load_json("./data.json")
        
app = falcon.API(middleware=[MultipartMiddleware()])

app.add_route("/", DrinkRecAPI())
