from diginomard_toolkit.google_api import GoogleSearch
from diginomard_toolkit.wiki import Wiki

def searchWiki(q):
    googleSearch = GoogleSearch()
    result = googleSearch.search(f'wikipedia {q}')
    wiki = Wiki()
    for item in result:
        if 'wikipedia.org' in item:
            wiki.getWikiFromUrl(item)
            break

searchWiki('가치투자')