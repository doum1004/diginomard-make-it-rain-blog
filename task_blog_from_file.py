import os
import time
from google_trend import GoogleTrend
from news import News
from ai_openai import OpenAI
from ai_openai_embed import OpenAIEmbedding
from utils import SaveUtils, Utils, FileUtils

def getFileSummary(inputPath = ''):
    def getSummaryPrompts(newsData):
        systemContent = f""
        userContent = f"Summarize what information the readers can take away from it:"
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent

    def getBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a critic. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. The blog includes Title, Summary, Fun facts in headers, insight, and similar movies. Put 5 hash tags at the end. Markdown style."
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent

    def getTranslatePrompts(previousAnswer):
        systemContent = f""
        userContent = "Translate to Korean"
        assistantContent = f"{previousAnswer}"
        return systemContent, userContent, assistantContent
    
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
    split_texts = Utils.splitText(text)
    summaries = []
    for i , text in enumerate(split_texts):
        if i > 10 and input('Too much token spend. Continue (type any) : ') == '':
            break
        prompts = getSummaryPrompts(text)
        result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], [])
        if 'I apologize, but it seems that the provided text is not clear' in result:
            print(result)
            if input('Failed to get answer. Continue (press any) ? : '):
                break
        summaries.append(result)
        time.sleep(3) # up to 20 api calls per min

    text_summary = '\r\n'.join(summaries)
    print(text_summary)

    prompts = getBlogPostPrompts(text_summary)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    print(result)

    prompts = getTranslatePrompts(result)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    print(result)

getFileSummary(f'__output/wiki/230707-164048_애드 아스트라_0.txt')
#getFileSummary(f'__input/namu-movie9.pdf')
#getFileSummary(f'https://en.wikipedia.org/wiki/Night_Train_to_Lisbon_(film)')