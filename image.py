import json
from PIL import Image
PHOTO_HEIGHT = 400

def is_white(pixel):
    return pixel[0] + pixel[1] + pixel[2] >= 250 * 3
def cut_white_area(before, after):
    img = Image.open(before, "r")
    rgb = img.convert("RGB")
    size = rgb.size
    top = 0
    bottom = size[1]
    left = 0
    right = size[0]
    for y in range(size[1]):
        for x in range(size[0]):
            if not is_white(rgb.getpixel((x, y))):
                top = y
                break
        else:
            continue
        break
    for y in reversed(range(size[1])):
        for x in range(size[0]):
            if not is_white(rgb.getpixel((x, y))):
                bottom = y
                break
        else:
            continue
        break
    for x in range(size[0]):
        for y in range(size[1]):
            if not is_white(rgb.getpixel((x, y))):
                left = x
                break
        else:
            continue
        break
    for x in reversed(range(size[0])):
        for y in range(size[1]):
            if not is_white(rgb.getpixel((x, y))):
                right = x
                break
        else:
            continue
        break
    crop = img.crop((left, top, right, bottom))
    crop.save(after, quality=100)




def resize(before, after, width=400, height=400):
    img = Image.open(before, "r")
    before_x, before_y = img.size[0], img.size[1]
    x = width
    y = height
    resized_img = img
    resized_img = resized_img.resize((x, y))
    resized_img.save(after, "jpeg", quality=100)


def load_json(file_path):
    with open(file_path) as f:
        jsn = json.load(f)
        for item in jsn:
            img_url = item["img"]
            title = item["title"]
            img_filename = title + ".jpg"
            img_path_from = "./images/" + img_filename
            img_path_to = "./cut/" + img_filename
            try:
                cut_white_area(img_path_from, img_path_to)
            except:
                continue
            img_path_from = img_path_to
            img_path_to = "./resized/" + img_filename
            resize(img_path_from, img_path_to)

load_json("./coffee.json")
