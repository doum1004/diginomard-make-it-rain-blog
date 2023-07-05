import os
import openai
from numpy import maximum
from utils import SaveUtils

os.environ['OPENAI_API_KEY']='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'

class OpenAI:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    saveUtils = SaveUtils('__output/chagpt/')
    def __init__(self):
        pass

    def _chatMessages(self, messages: list):
        print(messages)
        response = openai.ChatCompletion.create (
            model="gpt-3.5-turbo", #gpt-3.5-turbo-0613
            messages = messages
        )
        responseContents = []
        for choice in response["choices"]:
            responseContents.append(choice["message"]["content"])
        responseContent = "\n".join(responseContents)
        self.saveUtils.saveData("chatgpt", str(messages) + "\n" + responseContent)
        print(responseContent)
        return responseContent

    def _createImage(self, q, nbImage, size=512):
        if (q == ''):
            print('Invalid Prompt')
            return
        response = openai.Image.create(
            prompt=q,
            n=nbImage,
            size=f"{size}x{size}"
        )
        self.saveUtils.saveData("chatgpt_image", response.to_dict())
        imageURLs = []
        if 'data' in response:
            for result in response["data"]:
                imageURLs.append(result["url"])
        elif 'url' in response:
            imageURLs.append(response["url"])
        print(imageURLs)
        for url in imageURLs:
            self.saveUtils.saveImageFromURL('chatgpt_image', url)
        return imageURLs
    
    def chatMessageContents(self, systemConent, userConent, assistantContent = '', messages = []):
        if systemConent == '' and userConent == '':
            print('Invalid Prompts')
            return
        if systemConent != '':
            messages.append({
                    "role": "system",
                    "content": systemConent
                })
        if userConent != '':
            messages.append({
                "role": "user",
                "content": userConent
            })
        if assistantContent != '':
            messages.append({
                    "role": "assistant",
                    "content": assistantContent
                })
        return self._chatMessages(messages)

    def createImage(self, q, nbImage = 1, skipDetailing = True, skipGeneratingPrompts = True):
        # get detail description
        messages = []
        q = q[:200]
        # if not skipDetailing:
        #     system, user, assistant = getDetailPrompts(q)
        #     answer1 = ask_chatgpt_contents(system, user, assistant, messages)
        #     q = answer1[:2000]

        # # get image prompts
        # if not skipGeneratingPrompts:
        #     system, user, assistant = getImagePrompts(newQuery)
        #     answer2 = ask_chatgpt_contents(system, user, assistant, messages)
        #     q = answer2[:200]

        return self._createImage(q, nbImage)