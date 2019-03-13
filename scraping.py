import requests
from bs4 import BeautifulSoup
import json
import urllib

url = "https://products.suntory.co.jp/0000000011/"

class DrinkGenre:
    def __init__(self, title, url):
        self.title = title
        self.url = url

class Drink:
    def __init__(self, title, url, img_url, materials):
        self.title = title
        self.url = url
        self.img_url = img_url
        self.materials = materials


def get_drink_genres(url):
    html = requests.get(url)
    html.encoding = html.apparent_encoding
    soup = BeautifulSoup(html.content, "html.parser")
    sections = soup.findAll(class_="section")
    drink_genres = []
    for section in sections:
        drink_genres.append(DrinkGenre(section.get_text().strip(), "https://products.suntory.co.jp" + section.find("a").get("href")));
    return drink_genres


def get_drink(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    title = soup.find(class_="itemTl").get_text()
    material_ele = soup.find(id="detail").findAll("td")
    if len(material_ele) == 0:
        return None
    materials = soup.find(id="detail").findAll("td")[0].get_text().split("、")
    img_url = soup.find(id="mainImg").find("img").get("src")
    return Drink(title, url, img_url, materials)
def get_drinks(genre_url):
    html = requests.get(genre_url)
    soup = BeautifulSoup(html.content, "html.parser")
    sections = soup.findAll(class_="section")
    drinks = []
    for section in sections:
        drinks.append(get_drink("https://products.suntory.co.jp" + section.find("a").get("href")))
    return drinks


def save(drinks, name):
    result = list(map(lambda x: { "title": x.title, "img": x.img_url, "materials": x.materials}, drinks))
    f = open(name + ".json", "w")
    json.dump(result, f, indent=2, ensure_ascii=False)
    
def download_image(url, dst_path):
    try:
        data = urllib.request.urlopen(url).read()
        with open(dst_path, mode="wb") as f:
            f.write(data)
    except urllib.error.URLError as e:
        print(e)


def load_json(file_path):
    with open(file_path) as f:
        jsn = json.load(f)
        for item in jsn:
            img_url = item["img"]
            title = item["title"]
            download_image(img_url, "./images/" + title + ".jpg")

#load_json("./coffee.json")
genres = get_drink_genres(url)
drinks = []
for genre in genres:
    drinks.extend(filter(lambda x: x != None, get_drinks(genre.url)))
save(drinks, "coffee")
