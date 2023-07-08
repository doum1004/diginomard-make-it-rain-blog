class PromptGenerator:
    def __init__(self):
        pass

    def getMovieBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a critic. You will provide valuable information everyone must know."
        userContent = "Rewrite a Blog post. Follow this Format: ### Intro, ### 📝 Movie Story, ### 💡 Thought, ### 🎵 Fun Facts,  ### 🎥 Similar Movies, ### 🌟 Ending Message, ### 🔖 Hash Tags. Markdown style. Split lines by sentence for better readability."
        assistantContent = f"{newsData[:2500]}"
        return systemContent, userContent, assistantContent
    
    def getBlogPostPrompts(newsData):
        systemContent = f"I want you to act as a critic. You will provide valuable information everyone must know."
        userContent = "Write a Blog post. The blog includes Title, Summary, Fun facts in headers, insight, and similar movies. Put 5 hash tags at the end. Markdown style."
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