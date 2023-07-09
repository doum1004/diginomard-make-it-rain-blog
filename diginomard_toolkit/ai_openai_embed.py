import hashlib
import os
import time
import jsonlines
import openai
import tiktoken
import json
import tqdm
import numpy as np
from numpy.linalg import norm
from pathlib import Path
from .utils import SaveUtils
from .ai_openai import OpenAI

class OpenAIEmbedding:
    openAI = OpenAI()
    def __init__(self):
        pass

    def getSummary(self, chunk):
        content = "The following is a passage fragment. Please summarize what information the readers can take away from it:"
        content += "\n" + chunk
        messages = [
                    {"role": "user", "content": content}
                ]
        summary = self.openAI._chatMessages(messages)[0]
        return summary
    
    
    def getInfo(self, info, text, chunk_sz = 700, max_memory = 100):
        text = text.replace("\n", " ").split()
        print(f'Text: {text}')
        # raise error if the anticipated api usage is too massive
        if (len(text) / chunk_sz) >= max_memory:
            raise ValueError("Processing is aborted due to high anticipated costs.")
        summaries = []
        for idx in tqdm(range(0, len(text), chunk_sz)):
            chunk = " ".join(text[idx: idx + chunk_sz])
            checkSize = OpenAI.getTokenUsage(chunk)
            if checkSize > chunk_sz * 3:
                print(f"Skipped an uninformative chunk {checkSize}. {chunk}")
                a = input("Continue ? ")
                if a != '':
                    raise
            attempts = 0
            while True:
                try:
                    summary = self.getSummary(chunk)
                    embd = self.openAI._embedding(chunk)
                    summary_embd = self.openAI._embedding(summary)
                    item = {
                        "id": len(info),
                        "text": chunk,
                        "embd": embd,
                        "summary": summary,
                        "summary_embd": summary_embd,
                    }
                    info.append(item)
                    time.sleep(3)  # up to 20 api calls per min
                    summaries.append(summary)
                    break
                except Exception as e:
                    attempts += 1
                    if attempts >= 3:
                        raise Exception(f"{str(e)}")
                    time.sleep(3)
        return summaries
    
    def storeInfo(self, text, memory_path, chunk_sz = 700, max_memory = 100):
        if memory_path == '':
            print(f'Invalid path : {memory_path}')
            return
        info = []
        summaries = ['Start', 'End']
        while len(summaries) >= 2:
            summaries = self.getInfo(info, text, chunk_sz, max_memory)
            print(summaries)
            print(f'size of summaries: {len(summaries)}')
            i = input('Continue ? (anytext) ')
            if i == '':
                break
            text = "\r\n\r\nSummary about above arcticle here: " + " ".join(summaries)

        with jsonlines.open(memory_path, mode="w") as f:
            f.write(info)
            print(f"Finish storing info in {memory_path}")

    def load_info(self, memory_path):
        with jsonlines.open(memory_path, 'r') as jsonl_f:
                for line in jsonl_f:
                    info = line
        return info
    
    
    def retrieve(q_embd, info):
        # return the indices of top three related texts
        text_embds = []
        summary_embds = []
        for item in info:
            text_embds.append(item["embd"])
            summary_embds.append(item["summary_embd"])
        # compute the cos sim between info_embds and q_embd
        text_cos_sims = np.dot(text_embds, q_embd) / (norm(text_embds, axis=1) * norm(q_embd))
        summary_cos_sims = np.dot(summary_embds, q_embd) / (norm(summary_embds, axis=1) * norm(q_embd))
        cos_sims = text_cos_sims + summary_cos_sims
        top_args = np.argsort(cos_sims).tolist()
        top_args.reverse()
        indices = top_args[0:3]
        return indices
    
    def chatGPT_query(self, user, assistant):
        content = "Please summarize what information the readers can take away from it: Must not write 'the readers can take away from it' from begining. Must not write 'the readers can take away from it'. Must write in Korean"
        content += "\n" + user
        messages = [
                    {"role": "user", "content": content}
                ]
        if assistant != "":
            messages.append(
                        {"role": "assistant", "content": assistant}
            )
        return self.openAI._chatMessages(messages)[0]
    
    # You are a very enthusiastic Diginormad who loves to help people! Given the following sections from the documentation, answer the qeuestion using only that information, outputted in mardown format. If you are unsure and the answer is not explicity written in the documentation, say "Sorry I don't know how to help with that"
    # Context sections:
    # {contextText}
    # Question: """
    # {query}
    # """
    # Answer as markdown (including related code snippets if available)
    def get_qa_content(self, q, retrieved_text):
        content = "After reading some relevant passage fragments from the same document, please respond to the following query. Note that there may be typographical errors in the passages due to the text being fetched from a PDF file or web page."

        content += "\nQuery: " + q

        for i in range(len(retrieved_text)):
            content += "\nPassage " + str(i + 1) + ": " + retrieved_text[i]

        content += "\nAvoid explicitly using terms such as 'passage 1, 2 or 3' in your answer as the questioner may not know how the fragments are retrieved. Please use the same language as in the query to respond."
        return content

    def generate_answer(self, q, retrieved_indices, info):
        while True:
            sorted_indices = sorted(retrieved_indices)
            retrieved_text = [info[idx]["text"] for idx in sorted_indices]
            content = self.get_qa_content(q, retrieved_text)
            if len(tokenizer.encode(content)) > 3800:
                retrieved_indices = retrieved_indices[:-1]
                print("Contemplating...")
                if not retrieved_indices:
                    raise ValueError("Failed to respond.")
            else:
                break
        messages = [
            {"role": "user", "content": content}
        ]
        answer = self.openAI._chatMessages(messages)[0]
        return answer

    def memorize(self, text):
        sha = hashlib.sha256(text.encode('UTF-8')).hexdigest()
        dirs = [f'/content/memory/', f'/content/drive/MyDrive/embed/memory/']

        file_exists = False
        memory_path = ''
        for dir in dirs:
            Path(dir).mkdir(parents=True, exist_ok=True)
            path = f"{dir}{sha}.json"
            if memory_path == '':
                memory_path = path
            file_exists |= os.path.exists(path)
            if file_exists:
                memory_path = path
                print(f"Detected cached memories in {memory_path}")

        if not file_exists:
            print("Memorizing...")
            self.store_info(text,memory_path)

        return memory_path

    def answer(self, q, info):
        q_embd = self.openAI._embedding(q, model="text-embedding-ada-002")
        retrieved_indices = self.retrieve(q_embd, info)
        answer = self.generate_answer(q, retrieved_indices, info)
        return answer

    def chat(self, memory_path):
        info = self.load_info(memory_path)
        while True:
            q = self.get_question()
            if len(tokenizer.encode(q)) > 200:
                raise ValueError("Input query is too long!")
            attempts = 0
            while True:
                try:
                    response = self.answer(q, info)
                    print()
                    print(f"{response}")
                    print()
                    time.sleep(3) # up to 20 api calls per min
                    break
                except Exception as e:
                    attempts += 1
                    if attempts >= 1:
                        raise Exception(f"{str(e)}")
                    time.sleep(3)