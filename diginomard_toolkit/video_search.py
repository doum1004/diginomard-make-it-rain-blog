import re
import requests
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
try:
    from  utils import SaveUtils
except ImportError:  # Python 3
    from .utils import SaveUtils

class VideoSearch:
    seen = {}
    # get html from url using selenium
    options = webdriver.ChromeOptions()
    saveUtils = SaveUtils('__output/video/')
    
    def __init__(self):
        self.options.add_argument("--headless")
        #self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
        pass

    def getDriver(self):
        #return webdriver.Chrome(options=self.options)
        return webdriver.Chrome(ChromeDriverManager().install())

    def searchPexels(self, keyword, num = 10):
        driver = self.getDriver()

        url = f'https://www.pexels.com/ko-kr/search/videos/{keyword}/?size=large&orientation=landscape'
        driver.get(url)        
        time.sleep(3)
        # scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        html_text = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html_text, 'html.parser')
        body = soup.find('body')

        srcs = re.findall(r'src="https://player.vimeo.com/external/(.*?)"', str(body))

        urls = []
        for src in srcs:
            id = src.split('.')[0]
            # get 1920 url from id
            url = f'https://player.vimeo.com/video/{id}'
            if url not in self.seen:
                self.seen[url] = True
                urls.append(url)

            if len(urls) >= num:
                break
        
        return urls[:num]

    def getVimeoDownloadLink(self, vimeoPlayerURL):
        #url = f'https://player.vimeo.com/video/{id}'
        html_text = requests.get(vimeoPlayerURL).text
        profiles = re.findall(r'{"profile".*?}', html_text)

        url = ''
        for profile in profiles:
            if url == '' or '1920' in profile:
                url = re.findall(r'"url":"(.*?)"', profile)[0]
        return url

    def getVimeoVideos(self, keyword, num):
        urls = self.searchPexels(keyword, num)
        videoLinks = []
        for url in urls:
            html_text = requests.get(url).text
            # Match the .mp4 string starting after a double quote and ending with .mp4
            match = re.search(r'"([^"]*?\.mp4)"', html_text)
            videoLinks.append(match.group(1) if match else '')
        return videoLinks

    def downloadVideo(self, keyword, num):
        videoLinks = self.getVimeoVideos(keyword, num)
        for videoLink in videoLinks:      
            print(self.saveUtils.downloadURL(keyword, videoLink))
            
    
# test VideoSearch
videoSearch = VideoSearch()
videoSearch.downloadVideo('self-discovery', 5)