import os
import time
import openai
import tiktoken
import json

try:
    from prompts import PromptGenerator
except ImportError:  # Python 3
    from .prompts import PromptGenerator

try:
    from utils import SaveUtils, Utils
except ImportError:  # Python 3
    from .utils import SaveUtils, Utils

#os.environ['OPENAI_API_KEY']="YOUR_KEY"
tokenizer = tiktoken.get_encoding("cl100k_base")

class AIModel:
    def __init__(self):
        pass

    def getTokenUsage(text):
        return len(tokenizer.encode(text))
    
    def _chatMessages(self, messages: list, keyword = ''):
        pass
    
    def chatMessageContents(self, systemConent, userConent, assistantContent = '', messages = [], keyword = ''):
        keyword = keyword.strip()
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


class OpenAI(AIModel):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    saveUtils = SaveUtils('__output/chagpt/')
    def __init__(self):
        pass

    def _embedding(self, text, model="text-embedding-ada-002"):
        text = text.replace("\n", " ")
        print(f'ChatGPT openai.Embedding is used (token :{AIModel.getTokenUsage(text)})')
        return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

    def _chatMessages(self, messages: list, keyword = 'chatgpt'):
        if keyword == '':
            keyword = 'chatgpt'

        print(messages)
        json_str = json.dumps(messages)
        print(f'ChatGPT openai.ChatCompletion is used (token :{AIModel.getTokenUsage(json_str)})')
        tryCount = 5
        while tryCount > 0:
            try:
                response = openai.ChatCompletion.create (
                    model= "gpt-4", #gpt-3.5-turbo, #gpt-3.5-turbo-instruct #gpt-3.5-turbo-16k
                    messages = messages,
                    # temperature = 1,
                    # top_p = 0.95,
                    # # max_tokens=2000,
                    # frequency_penalty = 0.0,
                    # presence_penalty = 0.0
                )
                print(f'Responsed: {len(response["choices"][0]["message"]["content"])}')
                break
            except:
                tryCount -= 1
                if tryCount > 0:
                    print('ChatGPT openai.ChatCompletion error. Retry after 5 sec')
                    time.sleep(5)
                    continue
                raise Exception('ChatGPT openai.ChatCompletion error. Retry failed')

        fullResponse = {}
        responseContents = []
        for choice in response["choices"]:
            content = choice["message"]["content"]
            content.replace('\"', '')
            responseContents.append(content)
        fullResponse["messages"] = messages
        fullResponse["choices"] = responseContents
        self.saveUtils.saveData(keyword, fullResponse)
        return responseContents[0]

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
    
    def getSummary(self, text, pauseStep = 10, pauseMaxToken = 0, breakWhenExceed = True):
        split_texts = Utils.splitText(text)
        summary = ''
        for i , text in enumerate(split_texts):
            pause = pauseStep != -1 and i % pauseStep == pauseStep - 1
            pause |= pauseMaxToken != 0 and len(summary) > pauseMaxToken
            if pause:
                if not breakWhenExceed or input('Too much token spend. To continue type any and press enter : ') == '':
                    break
            prompts = PromptGenerator.getSummaryPrompts(text)
            result = self.chatMessageContents(prompts[0], prompts[1], prompts[2], [], keyword='Summary')
            if 'I apologize, but it seems that the provided text is not clear' in result:
                print(result)
                if input('Failed to get answer. To continue type any and press enter ? : ') == '':
                    break
            summary += result + '\n'
            time.sleep(5) # up to 20 api calls per min

        summary = summary.replace('\\\"', '')
        summary = summary.replace('\"', '')
        print(f'Summary: {summary}')
        return summary
        
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
