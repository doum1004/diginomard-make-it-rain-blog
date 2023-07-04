import cv2
import numpy as np
import base64
import json
import datetime
import os
import urllib.request
from PIL import Image
from io import BytesIO
from pathlib import Path

class Utils:
    def __init__(self):
        pass

    def isJsonString(jsonString):
        try:
            json.loads(jsonString)
        except ValueError as e:
            return False
        return True
       
    def getDirs(baseDir, useGoogleCloud = False):
        dirs = [f'{baseDir}']
        if useGoogleCloud:
           dirs.append(os.path.join('/content/drive/MyDrive/diginormad', baseDir))
        for dir in dirs:
            Path(dir).mkdir(parents=True, exist_ok=True)
        return dirs

    def getCurrentTime():
        return datetime.datetime.now().strftime("%y%d%m-%H%M%S")
    
    def getUniqueFileNameUnderDirs(dirs, fileName, ext):
        i = 0
        def getFileName():
            return f'{fileName}_{Utils.getCurrentTime()}_{i}.{ext}'
        fileName = getFileName()
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            while os.path.exists(filePath):
                i += 1
                filePath = f'{dir}/{fileName}_{Utils.getCurrentTime()}_{i}.{ext}'
        return filePath

class ImageUtils:
    def __init__(self, localSetting = False):
        pass
    
    def getImageFromBase64UsingCV(base64_string):
        image_data = base64.b64decode(base64_string)
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return image

    def getImageFromBase64UsingPIL(base64_string):
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        return image

    def getImageFromBase64(base64_string):
        try:
            return ImageUtils.getImageFromBase64UsingCV(base64_string)
        except Exception as e:
            print("Error occurred while converting base64 to image:", e)
            return None
    
    def getBase64FromImageFile(imgFile):
        with open(imgFile, "rb") as file:
            image_data = file.read()
            base64_data = base64.b64encode(image_data).decode("utf-8")
        return base64_data

class SaveUtils:
    baseDir = ''
    localSetting = False
    def __init__(self, baseDir, localSetting = False):
        self.baseDir = baseDir
        self.localSetting = localSetting

    def saveData(self, fileName, data):
        if fileName == '' or data == '':
            return
        
        baseDir = self.baseDir
        if self.localSetting:
           baseDir = os.path.join(os.getcwd(), self.baseDir)

        isJson = Utils.isJsonString(data)
        ext = 'txt'
        if isJson:
           ext = 'json'

        dirs = Utils.getDirs(baseDir, not self.localSetting)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, fileName, ext)

        filePaths = []
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            with open(filePath, 'w', encoding='utf-8') as writefile:
                if isJson:
                    json.dump(data, writefile, ensure_ascii=False)
                else:
                    writefile.write(data)
            filePaths.append(filePath)
        print(filePaths)

    def saveImageFromURL(self, fileName, url):
        if fileName == '' or url == '':
            return
        
        baseDir = self.baseDir
        if self.localSetting:
           baseDir = os.path.join(os.getcwd(), self.baseDir)

        dirs = Utils.getDirs(baseDir, not self.localSetting)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, fileName, 'jpg')

        filePaths = []
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            urllib.request.urlretrieve(url, filePath)
            filePaths.append(filePath)
        print(filePaths)
        return filePaths


    def saveImageFromBase64(self, fileName, base64Code):
        if fileName == '' or fileName == '':
            return
        
        if self.localSetting:
           baseDir = os.path.join(os.getcwd(), baseDir)

        image = ImageUtils.getImageFromBase64(base64Code)

        dirs = Utils.getDirs(baseDir, not self.localSetting)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, baseDir, 'jpg')

        filePaths = []
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            cv2.imwrite(filePath, image)
            filePaths.append(filePath)
        print(filePaths)
        return filePaths