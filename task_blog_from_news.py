from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.image_search import ImageSearch
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import SaveUtils, Utils

def getNewsBlogPost():
    googleTrend = GoogleTrend(0)
    trends = googleTrend.getTrends()
    print(trends)

    news = News(1)
    index = input('Give trend index : ')
    keyword = trends[int(index)]
    result_news = news.getAllNews(keyword)

    openai = OpenAI()
    prompts = PromptGenerator.getNewsBlogPrompts(result_news)
    resultEng = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
    if len(resultEng) < 400:
        prompts = PromptGenerator.getDetailsPrompts(resultEng)
        resultEng = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)

    prompts = PromptGenerator.getTranslatePrompts(resultEng)
    resultKor = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], [], keyword = keyword)
    
    dir = '__output/blog/news'
    saveUtils = SaveUtils(dir)
    saveUtils.saveData(keyword, resultKor)

    imageSearch = ImageSearch()
    images = imageSearch.getImageFromBing(f'{keyword}', 5)
    Utils.moveFiles(images, dir)

getNewsBlogPost()