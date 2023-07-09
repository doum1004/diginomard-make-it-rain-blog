import os
import time
from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.ai_openai_embed import OpenAIEmbedding
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import SaveUtils, Utils, FileUtils

def getFileSummary(inputPath = ''):
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
    text_summary = openai.getSummary(text)

    prompts = PromptGenerator.getBlogPostPrompts(text_summary)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    print(result)

    prompts = PromptGenerator.getTranslatePrompts(result)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    print(result)

getFileSummary(f'__output/wiki/230707-164048_애드 아스트라_0.txt')
#getFileSummary(f'__input/namu-movie9.pdf')
#getFileSummary(f'https://en.wikipedia.org/wiki/Night_Train_to_Lisbon_(film)')