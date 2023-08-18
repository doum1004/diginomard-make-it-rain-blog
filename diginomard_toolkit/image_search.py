import os
import imghdr
import re
import time
import urllib.request
import urllib
from bing_image_downloader import downloader
import requests

try:
    from google_api import GoogleSearch
except ImportError:  # Python 3
    from .google_api import GoogleSearch

try:
    from utils import FileUtils, Utils, SaveUtils, HTMLUtils, ImageUtils
except ImportError:  # Python 3
    from .utils import FileUtils, Utils, SaveUtils, HTMLUtils, ImageUtils

class ImageSearch:
    outputDir = '__output/image/'
    saveUtils = SaveUtils(outputDir)
    googleSearch = GoogleSearch()
    def __init__(self):
        pass

    def getFolderFiles(self, folderPath):
        file_list = []

        # Iterate over all files in the folder
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                file_path = os.path.join(root, file)
                if imghdr.what(file_path):
                    file_list.append(file_path)

        return file_list

    def getImageFromBing(self, q, nbImage = 10):
        q = FileUtils.fixDirectoryName(q)
        targetDir = os.path.join(self.outputDir, q)
        Utils.deleteFilesUnderDir(targetDir)
        downloader.download(q, limit=nbImage, output_dir=self.outputDir, adult_filter_off=True, force_replace=False, timeout=20)
        return self.getFolderFiles(targetDir) #Utils.renameFiles(self.getFolderFiles(os.path.join(self.outputDir, q)), fileName)
    
    def getImageFromGoogle(self, q, nbImage = 10):
        result = self.googleSearch.searchImage(q, nbImage)
        fileList = []
        for item in result:
            file = self.saveUtils.saveImageFromURL(q, item)
            fileList.append(file)
        return fileList

    def get_filter(self, shorthand):
            if shorthand == "line" or shorthand == "linedrawing":
                return "+filterui:photo-linedrawing"
            elif shorthand == "photo":
                return "+filterui:photo-photo"
            elif shorthand == "clipart":
                return "+filterui:photo-clipart"
            elif shorthand == "gif" or shorthand == "animatedgif":
                return "+filterui:photo-animatedgif"
            elif shorthand == "transparent":
                return "+filterui:photo-transparent"
            else:
                return ""
            
    def isLinkHasExtBlackList(self, link):        
        blackList = [".gif", ".cms"]
        link = link.lower()
        for ext in blackList:
            if link.find(ext) != -1:
                return True
        return False
    
    def getImageFromBingSearch(self, q, nbImage):
        page_counter = 0
        adult = 'off'
        results = []
        filter = ""
        seen = set()
        while True:
            page_counter += 1
            request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(q) \
                    + '&first=' + str(page_counter) + '&count=' + str(nbImage) \
                    + '&adlt=' + adult + '&qft=' + ('' if filter is None else self.get_filter(filter))
            request = urllib.request.Request(request_url, None, headers=HTMLUtils.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode('utf8')
            if html ==  "":
                print("[%] No more images are available")
                break
            links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            for link in links:
                if self.isLinkHasExtBlackList(link):
                    continue

                if link in seen:
                    continue

                try:
                    # response = requests.get(link, headers=HTMLUtils.headers)
                    # if response.status_code != 200:
                    #     Failed = True
                    request = urllib.request.Request(link, None, HTMLUtils.headers)
                    image_data = urllib.request.urlopen(request, timeout=20).read()
                    if imghdr.what(None, image_data):
                        imgSize = ImageUtils.getImageResolution(image_data)
                        width = imgSize[0]
                        height = imgSize[1]
                        if width >= 400 and height >= 400:
                            pass
                        else:
                            raise ValueError('Invalid image size, not saving {}x{} {}'.format(width, height, link))
                    else:
                        raise ValueError('Invalid image, not saving {}'.format(link))
                except Exception as e:
                    print("[!] Error:: {}".format(e))
                    continue
                
                print("[OK] {}".format(link))
                results.append(link)
                seen.add(link)
                if nbImage == len(seen):
                    return results
        return results