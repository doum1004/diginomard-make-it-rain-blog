class PromptGenerator:
    def __init__(self):
        pass

    def getMovieBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a critic. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. Follow this Format: ### Intro, ### 📝 Movie Story, ### 🎵 Fun Facts, ### 💡 Thought,  ### 🎥 Similar Movies, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent
    
    def getNewsBlogPrompts(newsData):
        systemContent = f"I want you to act as a news reporter. You will utilize the news article to provide valuable information."
        userContent = "Write a Blog post. Follow this Format: ## Title, ### Intro, ### 📝 Summary, ### 🎵 Story and Information, ### 💡 Thought and Insight, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent

    def getBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a news reporter. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. Follow this Format: ## Title, ### Intro, ### 📝 Summary, ### 🎵 Story and Information, ### 💡 Thought and Insight, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent
    
    def getBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a news reporter. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. Follow this Format: ## Title, ### Intro, ### 📝 Summary, ### 🎵 Story and Information, ### 💡 Thought and Insight, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent
    
    def getSummaryPrompts(newsData):
        systemContent = f""
        userContent = f"Summarize what information the readers can take away from it:"
        assistantContent = f"{newsData[:2500]}"
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