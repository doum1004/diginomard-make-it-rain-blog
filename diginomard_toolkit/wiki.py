from bs4 import BeautifulSoup
import requests
import wikipediaapi
from .utils import SaveUtils

class Wiki:
    saveUtils = SaveUtils('__output/wiki/')
    CODE_LANGS = ["ko", "en"]
    code_lang = ''
    def __init__(self):
        self.updateWikiLang(0)
        pass

    def updateWikiLang(self, country_index):
        self.code_lang = self.CODE_LANGS[country_index]
        self.wiki = wikipediaapi.Wikipedia('PersonalProject (doum1004@gmail.com)', self.code_lang, extract_format=wikipediaapi.ExtractFormat.WIKI)

    def getWikiFromUrl(self, url):
        if url is None or url == "":
            return
        
        # Get the Wikipedia page title from the URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'id': 'firstHeading'}).text
        
        return self.getWiki(title)

    def printPage(self, page_py):
        print(f"Page - Exists ({page_py.language}): {page_py.exists()}")
        print("Page - Title: %s" % page_py.title)
        print("Page - Summary: %s" % page_py.summary[:200])

    def getWikiPage(self, keyword):
        for i, lang in enumerate(self.CODE_LANGS):
            self.updateWikiLang(i)
            page_py = self.wiki.page(keyword)
            if page_py.exists():
                break
            
        if page_py.exists():
            self.printPage(page_py)

        return page_py

    def getWiki(self, keyword, lang = 'en'):
        if keyword is None or keyword == "":
            return
        
        page_py = self.getWikiPage(keyword)
        if not page_py.exists():
            return
        
        if page_py.language != lang and lang in page_py.langlinks:
            page_py_anotherlang = page_py.langlinks[lang]            
            if page_py_anotherlang.exists():
                page_py = page_py_anotherlang
                self.printPage(page_py)

        self.saveUtils.saveData(keyword, page_py.text)
        return page_py.text
