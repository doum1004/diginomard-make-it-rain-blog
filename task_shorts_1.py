from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.utils import SaveUtils, Utils

def getInfoBeforeDie():
    def getPrompts(keyword):
        systemContent = f"I want you to act as a wikipedia. You will provide valuable information everyone must know."
        userContent = f'Give me a 60 seconds video script about 3 {keyword} knowledge and information we must know. And put 5 hash tags. Write in English'
        assistantContent = f""
        return systemContent, userContent, assistantContent
    
    def getTranslatePrompts(answer):
        #systemContent = f"I want you to act as a news reporter. We will utilize the following news article to provide valuable information:\n\n{newsData[:2500]}."
        systemContent = f""
        userContent = "Translate to Korean. Must Write in Korean"
        assistantContent = f"{answer}"
        return systemContent, userContent, assistantContent
    
    def getBriftPrompts(answer):
        systemContent = f""
        userContent = "Give brift."
        assistantContent = f"{answer}"
        return systemContent, userContent, assistantContent
    
    def getDetailPrompts(answer):
        systemContent = f""
        userContent = "Give more detail."
        assistantContent = f"{answer}"
        return systemContent, userContent, assistantContent

    keyword = input('Give keyword : ')

    openai = OpenAI()
    prompts = getPrompts(keyword)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = f'{keyword}_en')
    print(result)

    prompts = getTranslatePrompts(result)
    result = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = f'{keyword}_ko')
    print(result)

getInfoBeforeDie()
