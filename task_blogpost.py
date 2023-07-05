from google_trend import GoogleTrend
from news import News
from ai_openai import OpenAI

def getNewsBlogPost():
    def getNewsBlogPrompts(newsData):
        #systemContent = f"I want you to act as a news reporter. You will utilize the following news article to provide valuable information:\n\n{newsData[:2500]}."
        systemContent = f"I want you to act as a news reporter. You will utilize the news article to provide valuable information."
        userContent = "Summury Suggest title and subheaders. Put 5 hash tags on the bottom. Must write it in Markdown style and Korean."
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent

    def getBlogDetails(previousAnswer):
        systemContent = f""
        userContent = "Give more details"
        assistantContent = f"{previousAnswer}"
        return systemContent, userContent, assistantContent

    def getBlogPrompts2(q):
        systemContent = f"You are an assistant who is good at creating prompts for image creation. Your job is to provide detailed and creative descriptions that will inspire unique and interesting images from the AI. Keep in mind that the AI is capable of understanding a wide range of language and can interpret abstract concepts. It has to be within 500 chars." #so feel free to be as imaginative and descriptive as possible. It has to be within 500 chars."
        userContent = f"Condense up to 4 outward description to focus on nouns and adjectives separated by ,"
        assistantContent = f"{q}"
        return systemContent, userContent, assistantContent

    googleTrend = GoogleTrend(0)
    trends, keywords = googleTrend.getTrendAndKeywords()
    print(trends)
    #print(keywords)

    news = News(0)
    index = input('Give trend index : ')
    keyword = trends[int(index)]
    result_news = news.getAllNews(keyword)

    openai = OpenAI()
    prompts = getNewsBlogPrompts(result_news)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    if len(result) < 400:
        prompts = getBlogDetails(result)
        result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])

getNewsBlogPost()