import imghdr
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
import posixpath
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from pathlib import Path

context = ssl.create_default_context(cafile=certifi.where())

class Preference:
    maxToken = 3000


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
       
    def getCurrentDate():
        return datetime.datetime.now().strftime("%y%m%d")
    
    def getCurrentTime():
        return datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        
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
    def getUniqueFilePath(dir, name, ext, i = 0):
        if (ext.startswith('.') == False):
            ext = '.' + ext

        # get all files under dir and get file name without extension
        fileNames = []
        if os.path.exists(dir):
            files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
            fileNames = [os.path.splitext(f)[0] for f in files]

        if name == None or name == '':
            name = Utils.getCurrentTime()
        name = name.replace(' ', '_')
    
        fileName = name
        if i > 0:
            fileName = f'{name}_{i}'
        # compare this name with name param
        if fileName in fileNames:
            # if exist then add number suffix
            i += 1
            return Utils.getUniqueFilePath(dir, name, ext, i)
        else:
            FileUtils.createDir(dir)
            return os.path.join(dir, f'{fileName}{ext}')
    
    # rename files with prefix if exist then add number suffix
    def renameFiles(files, fileName):
        # remove space on prefix
        fileName = fileName.replace(' ', '_')
        
        newNames = []
        for file in files:
            dir = os.path.dirname(file)
            ext = os.path.splitext(file)[-1]

            newFilePath = Utils.getUniqueFilePath(dir, fileName, ext)
            os.rename(file, newFilePath)
            newNames.append(newFilePath)
        return newNames
    
    def copyFiles(files, targetDir, suffixIndex = 0):
        newNames = []
        for file in files:
            if not os.path.exists(file):
                continue
            filename = os.path.basename(file)
            ext = os.path.splitext(filename)[-1]
            newFilePath = Utils.getUniqueFilePath(targetDir, filename, ext, suffixIndex)
            shutil.copy(file, newFilePath)
            newNames.append(newFilePath)
        return newNames

    def moveFiles(files, dir, newNameWithoutExt = '', suffixIndex = 0):
        newNames = []
        FileUtils.createDir(dir)
        for source in files:
            if not os.path.exists(source):
                continue
            filename = os.path.basename(source)               
            # get ext and name
            nameWihtoutExt, ext = os.path.splitext(filename)
            if newNameWithoutExt != '':
                nameWihtoutExt = newNameWithoutExt
            dest = Utils.getUniqueFilePath(dir, nameWihtoutExt, ext, suffixIndex)
            shutil.move(source, dest)
            newNames.append(dest)
        return newNames
    
    def deleteFilesUnderDir(dir):
        try:
            if os.path.exists(dir):
                shutil.rmtree(dir)
        except:
            pass
        FileUtils.createDir(dir)

    # getCurrentDate(yyyy-mm-dd) depending on timezone (default Korea)
    def getCurrentDate(timeZone = datetime.timezone(datetime.timedelta(hours=9))):        
        return datetime.datetime.now(timeZone).strftime("%Y-%m-%d")
    
    # get RandomHour before current hour depending on timezone
    def getTimeBeforeCurrentHourInTimeZone(timeZone: datetime.timezone):
        currentHour = datetime.datetime.now(timeZone).hour
        randHour = currentHour if currentHour == 0 else np.random.randint(currentHour)
        # return '##:00:00 GMT+9(depending on timezone)
        return f'{randHour:02d}'
    
    def isUrl(url):
        return validators.url(url)

class HTMLUtils:
    #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",}
    #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}

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

    def isValidFilePath(filePath):
        # split first drive path
        drive, path = os.path.splitdrive(filePath)
        pattern = r'[<>:"|?*]'
        if re.search(pattern, path):
            return False
        return True
    
    def fixDirectoryName(path):
        pattern = r'[<>:"/\\|?*]'
        new_path = re.sub(pattern, '', path)
        return new_path

    def fixDirectoryPath(path):
        pattern = r'[<>:"|?*]'
        new_path = re.sub(pattern, '', path)
        return new_path

    def createDir(dir):
        if FileUtils.isValidFilePath(dir) == False:
            raise ValueError("Invalid dir path!")
        
        os.makedirs(dir, exist_ok=True)
    
    def writeFile(filePath, data):
        if FileUtils.isValidFilePath(filePath) == False:
            raise ValueError("Invalid file name!")

        FileUtils.createDir(os.path.dirname(filePath))
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
            #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",}
            response = requests.get(url, headers=HTMLUtils.headers)
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
    
    def getRelPath(baseDir, filePath):
        return os.path.relpath(filePath, baseDir).replace('\\', '/')
        # replace imagePaths in relative path from baseDir
        # relPaths = []
        # for path in imagePaths:
        #     relPath = path.replace(baseDir, '')
        #     # replace \\ to /
        #     relPath = relPath.replace('\\', '/')
        #     if relPath[0] == '/':
        #         relPath = relPath[1:]
        #     relPaths.append(relPath)        
        # return relPaths

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
    
    def downloadImage(url, dir, fileNameWithoutExtension = ''):
        # takeUrlPath before ? starts
        url = url.split('?')[0]
        path = urllib.parse.urlsplit(url).path
        fileName = posixpath.basename(path).split('?')[0]
        # get fileName without extension
        i = 1
        if fileNameWithoutExtension == '':
            fileNameWithoutExtension = os.path.splitext(fileName)[0]
            i = 0

        ext = 'jpg'
        if fileName.find(".") != -1:
            ext = fileName.split(".")[-1]
        
        if ext == "gif":
            return ''

        filePath = Utils.getUniqueFilePath(dir, fileNameWithoutExtension, "." + ext, i)
        print(filePath)
        FileUtils.createDir(os.path.dirname(filePath))
        try:
            #urllib.request.urlretrieve(url, filePath)
            request = urllib.request.Request(url, None, HTMLUtils.headers)
            image = urllib.request.urlopen(request, timeout=15).read()
            if imghdr.what(None, image):
                with open(filePath, "wb") as f:
                    f.write(image)
        except Exception as e:
            print(e)
            pass
        if not os.path.exists(filePath):            
            print('[Error]Failed to download image {}\n'.format(url))
            filePath = ''
        return filePath

    def getImageResolution(image_data):
        image = Image.open(BytesIO(image_data))
        return image.size
    
    def convertItToWebPFile(sourceFilePath):
        if not os.path.exists(sourceFilePath):
            return ''
        targetFilePath = os.path.splitext(sourceFilePath)[0] + '.webp'
        if os.path.exists(targetFilePath):
            return targetFilePath
        try:
            image = Image.open(sourceFilePath)
            image = image.convert('RGB')
            image.save(targetFilePath, 'webp')
        except:
            pass
        return targetFilePath

class SaveUtils:
    baseDir = ''
    def __init__(self, baseDir):
        self.baseDir = baseDir

    def getBaseDir(self, subDir = ''):
        dir = os.path.join(self.baseDir, FileUtils.fixDirectoryName(subDir))
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
        filePath = Utils.getUniqueFilePath(baseDir, fileName, ext)
        
        with open(filePath, 'w', encoding='utf-8') as writefile:
            if isJson:
                json.dump(data, writefile, ensure_ascii=False, indent=None)
            else:
                writefile.write(data)

        return filePath

    def saveAudio(self, subDir, data):
        if data == '':
            raise 'Invalid Argument'
        
        baseDir = self.getBaseDir(subDir)
        filePath = Utils.getUniqueFilePath(baseDir, '', 'wav')

        with open(filePath, "wb") as f:
            f.write(data)
            
        return filePath
    
    def saveImageFromURL(self, subDir, url):
        if url == '':
            return
        
        path = urllib.parse.urlsplit(url).path
        filename = posixpath.basename(path).split('?')[0]
        file_type = filename.split(".")[-1]
        if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
            file_type = "jpg"

        baseDir = self.getBaseDir(subDir)
        filePath = Utils.getUniqueFilePath(baseDir, '', file_type)

        try:
            urllib.request.urlretrieve(url, filePath)
        except:
            pass
        return filePath


    def saveImageFromBase64(self, subDir, base64Code):
        if base64Code == None or base64Code == '':
            return
        
        image = ImageUtils.getImageFromBase64(base64Code)

        baseDir = self.getBaseDir(subDir)
        filePath = Utils.getUniqueFilePath(baseDir, '', 'jpg')

        cv2.imwrite(filePath, image)

        return filePath

    def downloadURL(self, subDir, url):
        baseDir = self.getBaseDir(subDir)
        fileNameWithExt = url.split('/')[-1]
        name, ext = os.path.splitext(fileNameWithExt)
        filePath = Utils.getUniqueFilePath(baseDir, name, ext)

        r = requests.get(url, allow_redirects=True)
        open(filePath, 'wb').write(r.content)
        return filePath