try:
    from utils import Preference, Utils
except ImportError:  # Python 3
    from .utils import Preference, Utils

class PromptGenerator:
    def __init__(self):
        pass

    def getWURGPrompts(keyword, number = 5):
        keyword = keyword.strip()
        systemContent = f"You are an script writer that only writes in Json. Do not write normal text. Write all in one line. Use single quote instead of double quote in key value."
        userContent = f'Give a detail script talking about {number} "{keyword}" things we must know. Organic conversation flow. Must fill {number} main. Fill each content at least 1 min to cover. Must fill all values in Json. Fill Main Tag for better image or video search.'
        jsonFormat = Utils.readJsonFileAsOneLineText('templates/template_wurg.json')
        assistantContent = f"Use this MyJson format:\n{jsonFormat}"
        return systemContent, userContent, assistantContent
    
    def getFixJsonPrompts(json):
        systemContent = f""
        userContent = f'Fix this json. Json: {json}'
        assistantContent = f""
        return systemContent, userContent, assistantContent
    
    def getSEODescription(data, lang = 'en'):
        systemContent = f""
        if lang != 'en':
            systemContent = f"Translate to {lang}"
        userContent = "Write a blog 120 charaters blog description for search engine optimization. It has to be one line. Don't use special charaters."
        assistantContent = f"{data[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent

    def getHashTags(data, lang = 'en'):
        systemContent = f""
        if lang != 'en':
            systemContent = f"Translate to {lang}"
        userContent = "Give 7 hash tags (Add ',' between each hash tag. Remove '#' from each hash tag.)"
        assistantContent = f"{data[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent
    
    def getMovieBlogPostPrompts(keyword, summary):
        keyword = keyword.strip()
        systemContent = f"You are a movie blog writer that writes only in Json. Write all in one line."
        userContent = f'Give me scripts that talking about {keyword}. Contents should include Intro, Story, Fun fact, Similar movie, Conclusion. Data reference and Json format are following'
        jsonFormat = Utils.readJsonFileAsOneLineText('templates/template_movie.json')
        assistantContent = f"Use this reference:\n{summary}\n\nUse this MyJson format:\n{jsonFormat}"
        return systemContent, userContent, assistantContent
    
    def getMovieBlogPostPrompts2(newsData):
        systemContent = f"I want you to act as a critic. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. Follow this Format: ### Intro, ### 📝 Movie Story, ### 🎵 Fun Facts, ### 💡 Thought,  ### 🎥 Similar Movies, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent
    
    def getNewsBlogPrompts(newsData):
        systemContent = f"I want you to act as a news reporter. You will utilize the news article to provide valuable information."
        userContent = "Write a Blog post. Follow this Format: ## Title, ### Intro, ### 📝 Summary, ### 🎵 Story and Information, ### 💡 Thought and Insight, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent

    def getBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a news reporter. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. Follow this Format: ## Title, ### Intro, ### 📝 Summary, ### 🎵 Story and Information, ### 💡 Thought and Insight, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent
    
    def getBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a news reporter. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. Follow this Format: ## Title, ### Intro, ### 📝 Summary, ### 🎵 Story and Information, ### 💡 Thought and Insight, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent
    
    def getSummaryPrompts(newsData):
        systemContent = f""
        #userContent = f"Summarize what information the readers can take away from it:"
        userContent = f"Summarize:"
        assistantContent = f"{newsData[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent
    
    def getTranslatePrompts(previousAnswer):
        systemContent = f""
        userContent = "Translate to Korean"
        assistantContent = f"{previousAnswer}"
        return systemContent, userContent, assistantContent
    
    def getDetailsPrompts(previousAnswer):
        systemContent = f""
        userContent = "Give more detial"
        assistantContent = f"{previousAnswer}"
        return systemContent, userContent, assistantContent

    def getContinuePrompts(previousAnswer):
        systemContent = f""
        userContent = "Continue"
        assistantContent = f"{previousAnswer}"
        return systemContent, userContent, assistantContent