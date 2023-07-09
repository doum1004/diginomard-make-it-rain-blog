import feedparser
import datetime
from bs4 import BeautifulSoup
from .utils import HTMLUtils
from .utils import SaveUtils

class News:
    saveUtils = SaveUtils('__output/news/')
    CODE_COUNTRIES = ['KO', 'US', 'CA']
    CODE_LANGS = ["KR", "en", "en"]
    code_country = ''
    code_lang = ''
    def __init__(self, country_index):
        self.code_country = self.CODE_COUNTRIES[country_index]
        self.code_lang = self.CODE_LANGS[country_index]
        pass

    def getContentsFromNewsUrl(self, url, content_keywords = [], visitedURL = []):
        if url is None or url == "" or url in visitedURL:
            return

        visitedURL.append(url)
        html = HTMLUtils.getHTML(url)
        soup = BeautifulSoup(html, 'html.parser')
        if soup is None:
            print('Failed getting HTML')
            return

        contents = []
        metas = HTMLUtils.getAllMetas(soup)
        if 'description' in metas:
            contents.append(metas['description'])

        for meta in metas:
            if not meta in ['og:description', 'twitter:description', 'nate:description', 'title']:
                continue

            meta_content = metas[meta]
            if meta_content is None:
                continue

            meta_content = meta_content[:20]
            contained = False
            for content_keyword in content_keywords:
                if meta_content in content_keyword:
                    contained = True
                    break
            if not contained:
                content_keywords.append(meta_content)
        print(content_keywords)

        for content_keyword in content_keywords:
            index = len(html)
            while index >= 0:
                index = html.rfind(content_keyword, 0, index)
                index1 = html.rfind('<div', 0, index)
                index2 = html.find('</div>', index)
                if index1 != -1 and index2 != -1:
                    new_content = html[index1:index2]
                    if new_content.find(content_keyword) < 100:
                        contents.append(new_content)
                    else:
                        contents.append(html[index:index2])
                    break

        result = []
        for content in contents:
            cleanContent = HTMLUtils.cleanText(content)
            if cleanContent is None or cleanContent in result:
                continue
            #print(cleanContent[:50])
            result.append(cleanContent)

        if len(result) == 0:
            print('Failed')

        return result

    def findContentByClassID(self, class_id, soup, visitedURL):
        # Find all elements with the specified class ID
        if soup is None:
            return
        elements = soup.find_all(class_=class_id)

        # If there are no elements with the specified class ID
        if not elements or len(elements) == 0:
            return None

        result = []
        for element in elements:
            cleanContent = HTMLUtils.cleanText(element.text)
            if cleanContent is None or cleanContent in result:
                continue

            #print(cleanContent[:50])
            result.append(cleanContent)
            url = element.parent.get('href')
            print(url)
            v = self.getContentsFromNewsUrl(url, [], visitedURL)
            if not v is None:
                result.extend(v)

        # Return the first element with the specified class ID
        return result

    def getNaverNews(self, q, d, nbArticle, visitedURL):
        result = []
        for p in range(int(nbArticle/16)+1):
            url = f'https://m.search.naver.com/search.naver?where=m_news&sm=mtb_jum&query={q}&nso=so%3Ar%2Cp%3A{d}d&start={p*16}'.replace(' ', '%20')
            print(url)
            html = HTMLUtils.getHTML(url)
            soup = BeautifulSoup(html, 'html.parser')
            contents = self.findContentByClassID('api_txt_lines', soup, visitedURL)
            if not contents is None:
                result.extend(contents)
        return result

    def getGoogleNewsRss(self, q, d, nbArticle, visitedURL):
        url = f'https://news.google.com/rss/search?q={q}+when:{d}d&hl={self.code_country}&gl={self.code_lang}&ceid={self.code_country}:{self.code_lang}'.replace(' ', '%20')
        print(url)

        feed = feedparser.parse(url)
        result = []
        for i, entry in enumerate(feed.entries[:nbArticle], start=1):
            title = entry.title
            link = entry.link
            print(f"{title}: {link}")

            contents = self.getContentsFromNewsUrl(link, [title[:int(len(title) * 7 / 10)]], visitedURL)
            if not contents is None:
                result.extend(contents)

        return result

    def getAllNews(self, q, d = 2, p = 1, useNaver = True, useGoogle = True):
        visitedURL = []

        result = []
        if useGoogle:
            result.extend(self.getGoogleNewsRss(q, d, p * 10, visitedURL))
        if useNaver:
            result.extend(self.getNaverNews(q, d, p * 10, visitedURL))

        resultDict = {}
        for item in result:
            if item == '':
                continue
            key = item[:15]
            if key in resultDict:
                if len(item) > len(resultDict[key]):
                    resultDict[key] = item
            else:
                resultDict[key] = item
        date = datetime.date.today().strftime('%Y%m%d')
        resultStr = f"About {q} on {date}\r\n" + ". ".join(resultDict.values())
        self.saveUtils.saveData(q, resultStr)
        return resultStr