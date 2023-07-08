from google_api import GoogleAPI
from wiki import Wiki

def searchWiki(q):
    googleAPI = GoogleAPI()
    result = googleAPI.search(f'wikipedia {q}')
    wiki = Wiki()
    for item in result:
        if 'wikipedia.org' in item:
            wiki.getWikiFromUrl(item)
            break

searchWiki('가치투자')