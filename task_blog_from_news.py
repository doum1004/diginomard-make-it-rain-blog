import os
from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.image_search import ImageSearch
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import FileUtils, Preference, SaveUtils, Utils
from diginomard_toolkit.google_api import GoogleTranslateion

def translate(text, target = 'ko'):
    googleTranslation = GoogleTranslateion()
    result = googleTranslation.translate(text, target)
    return result

def getNewsBlogPost():
    country = 1
    googleTrend = GoogleTrend(country)
    trends = googleTrend.getTrends()

    # input1 = input('Give trend index or keyword : ')
    # # is number or not
    # if input1.isdigit():
    #     keyword = trends[int(input1)]
    # else:
    #     keyword = input1
    news = News(country)
    for keyword in trends[:5]:
        print(f'keyword : {keyword}')
        result_news = news.getAllNews(keyword, useNaver=False, useGoogle=True)

        openai = OpenAI()
        if len(result_news) > Preference.maxToken:
            result_news = openai.getSummary(result_news, pauseMaxToken=Preference.maxToken)

        prompts = PromptGenerator.getNewsBlogPrompts(result_news)
        resultEng = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
        if len(resultEng) < 400:
            prompts = PromptGenerator.getDetailsPrompts(resultEng)
            resultEng = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)

        #prompts = PromptGenerator.getTranslatePrompts(resultEng)
        #resultKor = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], [], keyword = keyword)
        resultKor = translate(resultEng, 'ko')
        
        dir = '__output/blog/news/' + Utils.getCurrentDate()
        saveUtils = SaveUtils(dir)
        saveUtils.saveData(keyword, resultEng)
        paths = saveUtils.saveData(keyword, resultKor)

        dir = os.path.dirname(paths[0])

        imageSearch = ImageSearch()
        images = imageSearch.getImageFromGoogle(f'{keyword}', 10)
        Utils.moveFiles(images, dir)

getNewsBlogPost()
#translateFile('C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/blog/news/2023-07-26/PSG/230725-135309_0.txt', 'ko')