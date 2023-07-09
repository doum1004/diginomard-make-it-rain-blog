import os
import time
from diginomard_toolkit.google_api import GoogleAPI
from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.ai_openai_embed import OpenAIEmbedding
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import SaveUtils, Utils, FileUtils
from diginomard_toolkit.wiki import Wiki

googleAPI = GoogleAPI()
def searchWiki(q):
    result = googleAPI.search(f'wikipedia {q}')
    wiki = Wiki()
    wikiText = ''
    for item in result:
        if 'wikipedia.org' in item:
            wikiText = wiki.getWikiFromUrl(item)
            break
    input('Continue ? ')
    i = wikiText.rfind('References')
    if i >= 0:
        wikiText = wikiText[:i]
    wikiText.strip()
    return wikiText

def getMovieBlogPost(text, keyword):
    print(f'len({len(text)}) {text[:50]}')
    if len(text) < 100:
        return
    input('Continue ? ')
    openai = OpenAI()
    text_summary = openai.getSummary(text)
    prompts = PromptGenerator.getMovieBlogPostPrompts(text_summary)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
    print(result)

    prompts = PromptGenerator.getTranslatePrompts(result)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
    print(result)
    return result


q = '영화 그녀가 말했다'
text = searchWiki(q)
post = getMovieBlogPost(text, q)
#post = Utils.splitLinesBySentence(post)
if post:
    post += f"\n\n\n"
    result = googleAPI.searchImage(f'{q}', 3)
    post += f"\n{result[0]}"
    result = googleAPI.search(f'justwatch {q}', 1)
    post += f"\n{result[0]}"
    result = googleAPI.search(f'{q}', 1)
    post += f"\n{result[0]}"
    print(post)

    saveUtils = SaveUtils('__output/blog/movie')
    saveUtils.saveData(q, post)