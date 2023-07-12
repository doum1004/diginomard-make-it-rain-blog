import shutil
import cv2
import numpy as np
import base64
import json
import datetime
import os
import urllib.request
import re
import requests
import ssl
import certifi
import fitz
import docx
import validators
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from pathlib import Path
from diginomard_toolkit.prompts import PromptGenerator

# if not '_SAVE_GOOLECLOUD_' in os.environ:
#     os.environ['_SAVE_GOOLECLOUD_'] = '0'

context = ssl.create_default_context(cafile=certifi.where())

class Utils:
    def __init__(self):
        pass

    def loadJson(data):
        data = data.replace("\'", "\"").replace('"', '\"')
        return json.loads(data, strict=False)

    def readFilelines(filePath):
        with open(filePath, 'r', encoding='utf8') as f:
            lines = f.readlines()
        return lines

    def readJsonFile(filePath):
        try:
            with open(filePath, 'r') as file:
                # Load the JSON data
                return json.load(file)
        except:
            print('Failed')

    def isJsonString(data):
        if type(data) == dict or type(data) == list:
            return True
        try:
            Utils.loadJson(data)
        except:
            return False
        return True
       
    def fixDirectoryName(path):
        pattern = r'[<>:"/\\|?*]'
        new_path = re.sub(pattern, '', path)
        return new_path

    def getDirs(baseDir):
        dirs = [f'{baseDir}']
        # if '_SAVE_GOOLECLOUD_' in os.environ and os.environ['_SAVE_GOOLECLOUD_']:
        #    dirs.append(os.path.join('/content/drive/MyDrive/diginormad', baseDir))
        for dir in dirs:
            Path(dir).mkdir(parents=True, exist_ok=True)
        return dirs

    def getCurrentTime():
        return datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    
    def getUniqueFileNameUnderDirs(dirs, ext, fileName = ''):
        def getFileName(fileName, i, ext):
            return f'{Utils.getCurrentTime()}_{fileName}_{i}.{ext}'
        
        i = 0
        newFileName = getFileName(fileName, i, ext)
        for dir in dirs:
            filePath = os.path.join(dir, newFileName)
            while os.path.exists(filePath):
                i += 1
                newFileName = getFileName(fileName, i, ext)
                filePath = os.path.join(dir, newFileName)
        return newFileName
    
    def splitText(text, max_tokens = PromptGenerator.maxToken):
        tokens = text.split()
        split_texts = []
        current_text = ""
        for token in tokens:
            token = token.strip()
            if token == '' or token is None:
                continue
            if len(current_text) + len(token) < max_tokens:
                current_text += token + " "
            else:
                split_texts.append(current_text.strip())
                current_text = token + " "
        if current_text:
            split_texts.append(current_text.strip())
        return split_texts
    
    def splitLinesBySentence(text, max_length = 70):
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result = []
        current_line = ""
        for sentence in sentences:
            if len(current_line + sentence) <= max_length:
                current_line += sentence
            else:
                result.append(current_line.strip())
                current_line = sentence
        if current_line:
            result.append(current_line.strip())
        return "\n".join(result)
    
    def moveFiles(files, dir):
        for source in files:
            filename = os.path.basename(source)
            destination = os.path.join(dir, filename)
            shutil.move(source, destination)

    
class HTMLUtils:
    def __init__(self):
        pass
    
    def getHTML(url):
        html = ''
        try:
            response = requests.get(url, timeout=0.5)
            html = response.text
        except:
            html = ''

        if html == '':
            try:
                response = urllib.request.urlopen(url, context=context)
                html = response.read().decode('utf-8')
            except:
                html = ''
        return html


    def remove_html_tags(text):
        filtered = re.sub('<.*?>', '', text) #regex
        return re.sub(r'<script\b[^>]*>(.*?)</script>', '', filtered, flags=re.MULTILINE|re.DOTALL)

    def cleanText(text):
        content_black_list = ["Comprehensive up-to-date news coverage, aggregated from sources all over the world by Google News."]

        text = HTMLUtils.remove_html_tags(text)
        text = text.strip().replace("{", "").replace("}", "").replace("[", "").replace("]", "")
        text = " ".join(text.split())
        if text in content_black_list:
            text = ""
        return text

    def getAllMetas(soup):
        meta_tags = soup.find_all('meta')

        meta_data = {}
        for tag in meta_tags:
            name = tag.get('name')
            property = tag.get('property')
            content = tag.get('content')
            if name:
                meta_data[name] = content
            elif property:
                meta_data[property] = content

        return meta_data


class FileUtils:
    def __init__(self):
        pass
    
    def getFileText(text_path, splitText = True):
        url = text_path
        suffix = os.path.splitext(text_path)[-1]
        if validators.url(url):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text()
            else:
                raise ValueError(f"Invalid URL! Status code {response.status_code}.")
        elif suffix == ".pdf":
            full_text = ""
            num_pages = 0
            with fitz.open(text_path) as doc:
                for page in doc:
                    num_pages += 1
                    text = page.get_text()
                    full_text += text + "\n"
            text = f"This is a {num_pages}-page document.\n" + full_text
        elif ".doc" in suffix:
            doc = docx.Document(text_path)
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text)
            text = '\n'.join(fullText)
        elif suffix == ".txt":
            lines = Utils.readFilelines(text_path)
            text = '\n'.join(lines)
        else:
            raise ValueError("Invalid document path!")
        if splitText:
            text = " ".join(text.split())
        return text


class ImageUtils:
    def __init__(self):
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
    def __init__(self, baseDir):
        self.baseDir = baseDir

    def getBaseDir(self, subDir = ''):
        dir = os.path.join(self.baseDir, Utils.fixDirectoryName(subDir))
        #baseDir = os.path.join(os.getcwd(), dir)
        return dir
    
    def saveData(self, subDir, data):
        if data == '':
            raise 'Invalid Argument'
        
        isJson = Utils.isJsonString(data)
        ext = 'txt'
        if isJson:
           ext = 'json'

        baseDir = self.getBaseDir(subDir)
        dirs = Utils.getDirs(baseDir)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, ext)

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
        return filePaths

    def saveAudio(self, subDir, data):
        if data == '':
            raise 'Invalid Argument'
        
        baseDir = self.getBaseDir(subDir)
        dirs = Utils.getDirs(baseDir)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, 'wav')

        filePaths = []
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            filePaths.append(filePath)
            with open(filePath, "wb") as f:
                f.write(data)
        print(filePaths)
        return filePaths
    
    def saveImageFromURL(self, subDir, url):
        if url == '':
            return
        
        baseDir = self.getBaseDir(subDir)
        dirs = Utils.getDirs(baseDir)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, 'jpg')

        filePaths = []
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            urllib.request.urlretrieve(url, filePath)
            filePaths.append(filePath)
        print(filePaths)
        return filePaths


    def saveImageFromBase64(self, subDir, base64Code):
        if fileName == '' or fileName == '':
            return
        
        image = ImageUtils.getImageFromBase64(base64Code)

        baseDir = self.getBaseDir(subDir)
        dirs = Utils.getDirs(baseDir)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, 'jpg')

        filePaths = []
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            cv2.imwrite(filePath, image)
            filePaths.append(filePath)
        print(filePaths)
        return filePaths
    
