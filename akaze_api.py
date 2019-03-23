#AKAZE比較
import falcon
import io
import json
from falcon_multipart.middleware import MultipartMiddleware
from PIL import Image
import cv2
import numpy as np

akaze = cv2.AKAZE_create()
image_des_list = {}
jsn = None
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
def search_in_cache(target_des, comparing_des_list):
    max_title = None
    max_score = 0
    for title in comparing_des_list:
        c_des = comparing_des_list[title]
        matches = bf.knnMatch(target_des, c_des, k=2)
        dist = [m.distance for m in matches]
        ret = sum(dist) / len(dist)
        if max_score < ret:
            max_score = ret
            max_title = title
    return (max_title, max_score)



def add_image_des(title, img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kp, des = akaze.detectAndCompute(img, None)
    image_des_list[title] = des
    

def load_json(file_path):
    global jsn
    with open(file_path) as f:
        jsn = json.load(f)
        for item in jsn:
            title = item["title"]
            img_path = item["image_path"]
            add_image_des(title, img_path)
            
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
        target_img = cv2.cvtColor(target_img, cv2.COLOR_RGB2GRAY)
        target_img = cv2.resize(target_img, dsize=(400, 400))
        print(target_img.shape)
        kp, target_des = akaze.detectAndCompute(target_img, None)
        result_title, result_score = search_in_cache(target_des, image_des_list)
        res.body = json.dumps({
            "title": result_title,
            "score": result_score,
            "materials": getMaterials(result_title),
            "image_url": getImageUrl(result_title)
        }, ensure_ascii=False)




load_json("./data.json")
        
app = falcon.API(middleware=[MultipartMiddleware()])

app.add_route("/", DrinkRecAPI())
