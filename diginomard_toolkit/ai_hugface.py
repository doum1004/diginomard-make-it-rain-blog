#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from hugchat import hugchat
from hugchat.login import Login
#from .utils import SaveUtils, Utils

class HugfaceAI:
    chatbot = None
    #saveUtils = SaveUtils('__output/hugface/')
    id = 0
    def __init__(self):
        sign = Login(os.environ['HUGFACE_E'], os.environ['HUGFACE_P'])
        cookies = sign.login()

        path = '__output/hugface/cookie/'
        sign.saveCookiesToDir(path)

        #sign.saveCookies()
        self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        self.newConversation()

    def newConversation(self):
        print('Clean slate!')
        self.id = self.chatbot.new_conversation()
        self.chatbot.change_conversation(self.id)


    def chatMessages(self, user_input, keyword = 'chatgpt'):
        if keyword == '':
            keyword = 'hugface'

        # Intro message
        print('[[ Welcome to ChatPAL. Let\'s talk! ]]')
        print('\'q\' or \'quit\' to exit')
        print('\'c\' or \'change\' to change conversation')
        print('\'n\' or \'new\' to start a new conversation')

        if user_input.lower() == '':
            pass
        elif user_input.lower() in ['c', 'change']:
            print('Choose a conversation to switch to:')
            print(self.chatbot.get_conversation_list())
        elif user_input.lower() in ['n', 'new']:
            self.newConversation()
        else:
            print('...')
            print(self.chatbot.chat(user_input))

        # #os.environ['OPENAI_API_KEY']="YOUR_KEY"
        # tokenizer = tiktoken.get_encoding("cl100k_base")
        # self.saveUtils.saveData(keyword, fullResponse)
        # return responseContents[0]
    
hugFace = HugfaceAI()
while True:
    user_input = input('> ')
    hugFace.chatMessages(user_input)
