import os
import time
import openai
import tiktoken
import json
from pathlib import Path
from .prompts import PromptGenerator
from .utils import SaveUtils, Utils

#os.environ['OPENAI_API_KEY']="YOUR_KEY"
tokenizer = tiktoken.get_encoding("cl100k_base")

class OpenAI:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    saveUtils = SaveUtils('__output/chagpt/')
    def __init__(self):
        pass

    def getTokenUsage(text):
        return len(tokenizer.encode(text))

    def _embedding(self, text, model="text-embedding-ada-002"):
        text = text.replace("\n", " ")
        print(f'ChatGPT openai.Embedding is used (token :{OpenAI.getTokenUsage(text)})')
        return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

    def _chatMessages(self, messages: list, keyword = 'chatgpt'):
        if keyword == '':
            keyword = 'chatgpt'

        print(messages)
        json_str = json.dumps(messages)
        print(f'ChatGPT openai.ChatCompletion is used (token :{OpenAI.getTokenUsage(json_str)})')
        response = openai.ChatCompletion.create (
            model= "gpt-3.5-turbo", #gpt-3.5-turbo-instruct #gpt-3.5-turbo-16k
            messages = messages,
            # temperature = 1,
            # top_p = 0.95,
            # # max_tokens=2000,
            # frequency_penalty = 0.0,
            # presence_penalty = 0.0
        )
        responseContents = []
        for choice in response["choices"]:
            responseContents.append(choice["message"]["content"])
        responseContent = "\n".join(responseContents)
        self.saveUtils.saveData(keyword, str(messages) + "\n" + responseContent)
        #print(responseContent)
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
    
    def chatContinue(dataFile, keyword):
        lines = Utils.readFilelines(dataFile)
        messages = Utils.loadJson(lines[0])
        answer = '\n'.join(lines[1:])
        prompts = PromptGenerator.getContinuePrompts(answer)
        return openai.chatMessageContents(prompts[0], prompts[1], prompts[2], messages, keyword)

    def chatMessageContents(self, systemConent, userConent, assistantContent = '', messages = [], keyword = ''):
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
        return self._chatMessages(messages, keyword)
    
    def getSummary(self, text):
        split_texts = Utils.splitText(text)
        summaries = []
        for i , text in enumerate(split_texts):
            if i % 5 == 4 and input('Continue for typing any ? (Too much token spend) : ') == '':
                break
            prompts = PromptGenerator.getSummaryPrompts(text)
            result = self.chatMessageContents(prompts[0], prompts[1], prompts[2], [], keyword='Summary')
            if 'I apologize, but it seems that the provided text is not clear' in result:
                print(result)
                if input('Failed to get answer. Continue (press any) ? : '):
                    break
            summaries.append(result)
            time.sleep(5) # up to 20 api calls per min

        text_summary = '\r\n'.join(summaries)
        print(text_summary)
        return text_summary
        
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