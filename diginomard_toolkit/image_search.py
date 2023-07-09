import os
import imghdr
from bing_image_downloader import downloader
from .google_api import GoogleAPI
from .utils import SaveUtils


class ImageSearch:
    outputDir = '__output/image/'
    saveUtils = SaveUtils(outputDir)
    googleAPI = GoogleAPI()
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
        downloader.download(q, limit=nbImage, output_dir=self.outputDir, adult_filter_off=True, force_replace=False, timeout=60)
        return self.getFolderFiles(f'/data/image/{q}/')
    
    def getImageFromGoogle(self, q, nbImage = 10):
        result = self.googleAPI.searchImage2(q, nbImage)
        for item in result:
            self.saveUtils.saveImageFromURL(q, item)

        
