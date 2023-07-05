from google_trend import GoogleTrend
from news import News
from ai_openai import OpenAI
from utils import SaveUtils, Utils

def getInfoBeforeDie():
    def getPrompts(keyword):
        systemContent = f"I want you to act as a wikipedia. You will provide valuable information everyone must know."
        userContent = f'Give me a 20 seconds video script about 3 {keyword} before we die we must know. And put 5 hash tags. Write in English'
        assistantContent = f""
        return systemContent, userContent, assistantContent
    
    def getTranslateion(answer):
        #systemContent = f"I want you to act as a news reporter. We will utilize the following news article to provide valuable information:\n\n{newsData[:2500]}."
        systemContent = f""
        userContent = "Translate to Korean. Must Write in Korean"
        assistantContent = f"{answer}"
        return systemContent, userContent, assistantContent
    
    def getBriftPrompts(answer):
        #systemContent = f"I want you to act as a news reporter. We will utilize the following news article to provide valuable information:\n\n{newsData[:2500]}."
        systemContent = f""
        userContent = "Give brift."
        assistantContent = f"{answer}"
        return systemContent, userContent, assistantContent
    
    def getDetailPrompts(answer):
        #systemContent = f"I want you to act as a news reporter. We will utilize the following news article to provide valuable information:\n\n{newsData[:2500]}."
        systemContent = f""
        userContent = "Give more detail."
        assistantContent = f"{answer}"
        return systemContent, userContent, assistantContent

    keyword = input('Give keyword : ')

    openai = OpenAI()
    prompts = getPrompts(keyword)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    prompts = getTranslateion(result)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])

getInfoBeforeDie()
