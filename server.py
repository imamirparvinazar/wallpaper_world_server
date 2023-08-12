from flask import Flask, send_file, request
import random
import os
import ast
import hashlib
import json

class Wallpaper:
    def __init__(self) -> None:
        self.wallpapers = []
        self.server = "https://wallpaper-world-server.onrender.com"
        self.categories = []
        self.users = []
        self.backup = None
        self.api_key = hashlib.sha384(str(random.getrandbits(1024)).encode()).hexdigest()

        try:
            os.mkdir("images/")
        except FileExistsError:
            print("Images folder detected.")
        else:
            print("Ceating a new images folder ... ")

        print(self.api_key)

    def findWallpaperBackup(self, image):
        for wallpaper in self.backup["wallpapers"]:
            if wallpaper["image"] == image:
                return wallpaper
            
    def findUserBackup(self, hash):
        for user in self.backup["users"]:
            if user["hash"] == hash:
                return hash

    def setBackup(self, backup):
        self.backup = json.load(open(f"{backup}", "r"))

    def importBackup(self, backup):
        self.setBackup(backup)
        for category in self.backup["categories"]:
            self.categories.append(category)
        for user in self.backup["users"]:
            self.users.append(user)
        for wallpaper in self.backup["wallpapers"]: 
            self.wallpapers.append(wallpaper)

        return True
    
    def exportData(self):
        j = {
            "wallpapers": self.wallpapers,
            "users": self.users,
            "categories": self.categories
        }
        hash = hashlib.sha256(str(random.getrandbits(1024)).encode()).hexdigest()
        file = open(f"{hash}.json", "w")
        json.dump(j, file)
        self.backup = f"{hash}.json"
        return True

    def registerUser(self, hash):
        if self.findUser(hash) == False:
            self.users.append({
                "hash": hash,
                "favorates": []
            })
            return True
        else:
            return False

    def findUser(self, hash):
        for user in self.users:
            if user["hash"] == hash:
                return user
        return False

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
    
    def findWallpaper(self, hash):
        for wall in self.wallpapers:
            if wall["hash"] == hash:
                return hash
        return False
    
    def likeWallpaper(self, userHash, wallpaperHash):
        user = self.findUser(userHash)
        wallpaper = self.findWallpaper(wallpaperHash)
        user["favorates"].append(wallpaper)
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
    r = random.getrandbits(64)
    file.save(f"images\{r}.jpg")
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

@app.route("/register")
def register():
    hash = hashlib.sha256(str(random.getrandbits(1024)).encode()).hexdigest()
    wallpaper.registerUser(hash)
    return {
        "status": "success",
        "result": hash
    }

@app.route("/exportData")
def exportData():
    data = ast.literal_eval(request.get_data().decode())
    if data["API_KEY"] == wallpaper.api_key:
        wallpaper.exportData()
        return f"success: {wallpaper.backup}"
    else:
        return "error"
    
@app.route("/getExportedData")
def getExportedData():
    data = ast.literal_eval(request.get_data().decode())
    if data["API_KEY"] == wallpaper.api_key:
        file = data["fileName"]
        return send_file(f"{file}")
    else:
        return "error"

@app.route("/getUser/<hash>")
def getUser(hash):
    if wallpaper.users.__len__() > 0:
        for user in wallpaper.users:
            if user["hash"] == hash:
                return hash
            
        return "failed"
    else:
        return "failed"
    
@app.route("/likeWallpaper/<userHash>/<wallpaperHash>")
def likeWallpaper(userHash, wallpaperHash):
    wallpaper.likeWallpaper(userHash, wallpaperHash)
    return "success"

@app.route("/isLiked/<userHash>/<wallpaperHash>")
def isLiked(userHash, wallpaperHash):
    user = wallpaper.findUser(userHash)
    wall = wallpaper.findWallpaper(wallpaperHash)

    if wall in user["favorates"]:
        return "true"
    else:
        return "false"

@app.route("/importData", methods=["POST"])
def importData():
    if request.form.get("API_KEY") == wallpaper.api_key:
        file = request.files["file"]
        file.save("./file.json")

        wallpaper.importBackup("file.json")

        return "success"
    
    else:
        return 'error'