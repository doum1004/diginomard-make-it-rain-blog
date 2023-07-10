import os
import time
from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.ai_openai_embed import OpenAIEmbedding
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import SaveUtils, Utils, FileUtils

def getFileSummary(keyword = '', inputPath = '', pauseStep = 5):
    if keyword == '':
        keyword = input(f'Give input keyword : ')

    if inputPath == '':
        inputPath = input(f'Give input file or path : ')
    
    text = FileUtils.getFileText(f'{inputPath}', False)
    text_nosplit = " ".join(text.split())
    print(f'len({len(text_nosplit)}) {text_nosplit[:50]}')
    input('Continue ? ')
    text.strip()
    i = text.rfind('References')
    if i >= 0:
        text = text[:i]
    i = text.rfind('[1]')
    if i >= 0:
        text = text[:i]

    openai = OpenAI()
    text_summary = openai.getSummary(text, pauseStep)

    prompts = PromptGenerator.getBlogPostPrompts(text_summary)
    resultEng = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    print(resultEng)

    prompts = PromptGenerator.getTranslatePrompts(resultEng)
    resultKor = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    print(resultKor)

    dir = '__output/blog/news'
    saveUtils = SaveUtils(dir)
    saveUtils.saveData(keyword, resultEng)
    saveUtils.saveData(keyword, resultKor)


getFileSummary('All-In Podcast E136', f'__output/youtube\\YoutubeScript\\230710-075228__0.txt', -1)
#getFileSummary(f'__input/namu-movie9.pdf')
#getFileSummary(f'https://en.wikipedia.org/wiki/Night_Train_to_Lisbon_(film)')