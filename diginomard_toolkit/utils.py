import shutil
import time
import uuid
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

# if not '_SAVE_GOOLECLOUD_' in os.environ:
#     os.environ['_SAVE_GOOLECLOUD_'] = '0'

context = ssl.create_default_context(cafile=certifi.where())

class Preference:
    maxToken = 2500

class Utils:
    def __init__(self):
        pass

    def shortUUID():
        return str(uuid.uuid4()).split('-')[0]
    
    def loadJson(data):
        if Utils.isJsonString(data):
            return json.loads(data)
        return None     

    def readTextFile(filePath):
        with open(filePath, 'r', encoding='utf8') as f:
            text = f.read()
        return text

    def readFilelines(filePath):
        with open(filePath, 'r', encoding='utf8') as f:
            lines = f.readlines()
        return lines

    def readJsonFile(filePath):
        with open(filePath, 'r', encoding='utf8') as file:
            return json.load(file)

    def readJsonFileAsOneLineText(filePath):
        with open(filePath, 'r') as file:
            # Load the JSON data
            return json.dumps(json.load(file), separators=(',', ':'))

    def isJsonString(data):
        if type(data) == dict or type(data) == list:
            return True
        try:
            json.loads(data)
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

    def getCurrentDate():
        return datetime.datetime.now().strftime("%y%m%d")
    
    def getCurrentTime():
        return datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    
    def getUniqueFileNameUnderDirs(dirs, ext, fileName = ''):
        def getFileName(prefix, i, ext):
            # assign it to a variable
            if prefix == None or prefix == '':
                prefix = Utils.getCurrentTime()
            # remove space on fileName
            prefix = prefix.replace(' ', '_')
            # if i == 0 no suffix
            suffix = ''
            if i != 0:
                suffix = f'_{i}'
            return f'{prefix}{suffix}.{ext}'
        
        i = 0
        newFileName = getFileName(fileName, i, ext)
        for dir in dirs:
            filePath = os.path.join(dir, newFileName)
            while os.path.exists(filePath):
                i += 1
                newFileName = getFileName(fileName, i, ext)
                filePath = os.path.join(dir, newFileName)
        return newFileName
    
    def splitText(text, max_tokens = Preference.maxToken):
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

    # get unique file name regardless of extension
    def getUniqueFileName(dir, name, ext, i = 0):
        while True:
            checkExts = ['.jpg', '.jpeg', 'png']
            if not ext in checkExts:
                checkExts.append(ext)
                
            # check all ext that all name are not exist
            exist = False
            for checkExt in checkExts:
                if i > 0:
                    newNameWithoutExt = f'{name}_{i}'
                else:
                    newNameWithoutExt = f'{name}'
                newPath = os.path.join(dir, f'{newNameWithoutExt}{checkExt}')
                if os.path.exists(newPath):
                    exist = True
                    break
            if not exist:
                break
            i += 1
        newPath = os.path.join(dir, f'{newNameWithoutExt}{ext}')
        return newPath
    
    # rename files with prefix if exist then add number suffix
    def renameFiles(files, fileName):
        # remove space on prefix
        fileName = fileName.replace(' ', '_')
        
        newNames = []
        for file in files:
            dir = os.path.dirname(file)
            ext = os.path.splitext(file)[-1]

            newName = Utils.getUniqueFileName(dir, fileName, ext)
            os.rename(file, newName)
            newNames.append(newName)
        return newNames
        
    def moveFiles(files, dir, newNameWithoutExt = '', i = 0):
        newNames = []
        os.makedirs(dir, exist_ok=True)
        for source in files:
            filename = os.path.basename(source)               
            # get ext and name
            nameWihtoutExt, ext = os.path.splitext(filename)
            if newNameWithoutExt != '':
                nameWihtoutExt = newNameWithoutExt
            dest = Utils.getUniqueFileName(dir, nameWihtoutExt, ext, i)
            shutil.move(source, dest)
            newNames.append(dest)
        return newNames
    
    def sanitize_folder_name(folder_name):
        # Define a regex pattern to remove invalid characters from the folder name
        valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        sanitized_name = ''.join(c for c in folder_name if c in valid_chars)
        return sanitized_name

    def deleteFilesUnderDir(dir):
        try:
            if os.path.exists(dir):
                shutil.rmtree(dir)
        except:
            pass
        os.makedirs(dir, exist_ok=True)

    # getCurrentDate(yyyy-mm-dd) depending on timezone (default Korea)
    def getCurrentDate(timeZone = datetime.timezone(datetime.timedelta(hours=9))):        
        return datetime.datetime.now(timeZone).strftime("%Y-%m-%d")
    
    # get RandomHour before current hour depending on timezone
    def getTimeBeforeCurrentHour(timeZone = datetime.timezone(datetime.timedelta(hours=9))):
        currentHour = datetime.datetime.now(timeZone).hour
        randHour = np.random.randint(currentHour)
        # return '##:00:00 GMT+9(depending on timezone)
        return f'{randHour:02d}'

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

    def writeFile(filePath, data):
        # get extension
        ext = os.path.splitext(filePath)[-1]
        with open(filePath, 'w', encoding='utf-8') as writefile:
            if ext == '.json':
                json.dump(data, writefile, ensure_ascii=False, indent=None)
            else:
                writefile.write(data)

    def writeJsonFile(filePath, data):
        with open(filePath, 'w', encoding='utf-8') as writefile:
            json.dump(data, writefile, ensure_ascii=False, indent=None)

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
            text = '\n'.join(   )
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
    
    def saveData(self, subDir, data, ext = 'txt', fileName = ''):
        subDir = subDir.strip()
        if data == None or data == '':
            raise 'Invalid Argument'
        
        isJson = type(data) == dict
        if isJson:
           ext = 'json'

        baseDir = self.getBaseDir(subDir)
        dirs = Utils.getDirs(baseDir)
        fileName = Utils.getUniqueFileNameUnderDirs(dirs, ext, fileName)

        filePaths = []
        for dir in dirs:
            filePath = os.path.join(dir, fileName)
            with open(filePath, 'w', encoding='utf-8') as writefile:
                if isJson:
                    json.dump(data, writefile, ensure_ascii=False, indent=None)
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
            try:
                urllib.request.urlretrieve(url, filePath)
                filePaths.append(filePath)
            except:
                pass
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
    
