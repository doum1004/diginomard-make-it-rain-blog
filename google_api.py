import os
from googleapiclient.discovery import build
from google_images_search import GoogleImagesSearch

class GoogleAPI:
    api_key = os.getenv("GOOGLE_API_KEY")
    custom_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    def __init__(self):
        pass

    def _search(self, query, searchType = '', num=10):
        service = build("customsearch", "v1", developerKey=self.api_key)
        serviceList = service.cse().list(q=query, cx=self.custom_search_engine_id, num=num)
        if searchType != '':
            serviceList.searchType = searchType
        result = serviceList.execute()

        links = []
        for image in result['items']:
            links.append(image['link'])
        return links

    def search(self, query, num = 10):
        return self._search(query, '', num)
    
    def searchImage(self, query, num = 10):
        return self._search(query, 'image', num)
    
    def searchImage2(self, query, num = 10, size = 'large'): #size : ''(anysize), large, medium, icon
        gis = GoogleImagesSearch(self.api_key, self.custom_search_engine_id)

        search_params = {
            'q': query,
            'num': num,
            'imgSize': size,
        }

        gis.search(search_params)
        links = []
        for image in gis.results():
            links.append(image.url)
        return links