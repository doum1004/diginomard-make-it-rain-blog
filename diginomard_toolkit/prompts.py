from diginomard_toolkit.utils import Preference, Utils


class PromptGenerator:
    def __init__(self):
        pass

    def getWURGPrompts(keyword, number = 5):
        keyword = keyword.strip()
        systemContent = f"You are an script writer that only speaks Json. Do not write normal text. Write all in one line. Use single quote instead of double quote in key value."
        userContent = f'Give me a 2 mins long script talking about {number} "{keyword}" that we must know. Must have {number} main. Must fill all values in Json except images. Main Tag should take simplied Main Heading for image search.'
        jsonFormat = Utils.readJsonFileAsOneLineText('templates/template_wurg.json')
        assistantContent = f"Use this MyJson format:\n{jsonFormat}"
        return systemContent, userContent, assistantContent
    
    def getFixJsonPrompts(json):
        systemContent = f""
        userContent = f'Fix this json. Json: {json}'
        assistantContent = f""
        return systemContent, userContent, assistantContent
    
    def getSEODescription(data):
        systemContent = f""
        userContent = "Give one paragraph blog summary for SEO-description (must be less than 100 characters, don't put emoji). Put hash 8 tags after. (must be 8 hash tags)"
        assistantContent = f"{data[:Preference.maxToken]}"
        return systemContent, userContent, assistantContent

    def getMovieBlogPostPrompts(keyword, summary):
        keyword = keyword.strip()
        systemContent = f"You are an movie review writer that only speaks Json. Do not write normal text. Write all in one line. Use single quote instead of double quote in values."
        userContent = f'Give me scripts that talking about ({keyword}) movie that we must know. Must fill all script contents in Json. Must fill all. Summary and Json format are following'
        jsonFormat = Utils.readJsonFileAsOneLineText('templates/template_movie.json')
        assistantContent = f"Use this summary:\n{summary}\n\nUse this MyJson format:\n{jsonFormat}"
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