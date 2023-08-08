from flask import Flask, send_file, request
from operator import itemgetter
import random
import os
import ast
import hashlib

class Wallpaper:
    def __init__(self) -> None:
        self.wallpapers = []
        self.server = "http://192.168.1.8:10000"
        self.categories = []

        try:
            os.makedirs("images/")
        except Exception:
            print("Already exists.")
        else:
            print("Done.")

    def addWallpaper(self, image, categories):
        self.wallpapers.append({
            "image": image,
            "categories": categories,
            "trend": 0,
            "hash": hashlib.sha256(str(random.getrandbits(1024)).encode()).hexdigest()
        })

    def findWallpapers(self, category):
        result = []
        for wall in self.wallpapers:
            if category in wall["categories"]:
                result.append(wall)
        return result
    
    def setWallpaper(self, hash):
        for wall in self.wallpapers:
            if wall["hash"] == hash:
                wall["trend"] += 1

    def addCategories(self, name, text, color):
        self.categories.append({
            "name": name,
            "text": text,
            "color": color
        })
        return True


app = Flask("server")
wallpaper = Wallpaper()

@app.route("/images/<filename>")
def getfFile(filename):
    return send_file(f".\images\{filename}")

@app.route("/getWallpapers", methods=["GET"])
def getWallpapers():
    return wallpaper.wallpapers

@app.route("/addWallpaper", methods=["POST"])
def addWallpaper():
    file = request.files['file']
    r = random.getrandbits(32)
    file.save(f"./images/{r}.jpg")
    return f"success: {r}"

@app.route("/addCategory/<num>")
def addCategoryImage(num):
    wallpaper.addWallpaper(wallpaper.server + f"/images/{num}.jpg", ast.literal_eval(request.get_data().decode()))
    return "success"

@app.route("/search/<key>")
def search(key):
    return wallpaper.findWallpapers(key)

@app.route("/setWallpaper/<hash>")
def setWallpaper(hash):
    wallpaper.setWallpaper(hash)
    return "success"

@app.route("/trending")
def getTrending():
    newList = wallpaper.wallpapers.copy()
    newList.sort(key=lambda x: x["trend"], reverse=True)
    return newList

@app.route("/categories")
def getCategories():
    return wallpaper.categories

@app.route("/addCategory", methods=["POST"])
def addCategory():
    data = ast.literal_eval(request.get_data().decode())
    wallpaper.addCategories(data["name"], data["text"], data["color"])
    return "success"


app.run("0.0.0.0", port=10000)