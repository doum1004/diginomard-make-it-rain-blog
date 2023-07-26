import os
import requests
import base64
from googleapiclient.discovery import build
from google_images_search import GoogleImagesSearch
from .utils import SaveUtils
from google.cloud import translate_v3 as translate
from googletrans import Translator
import html

class GoogleSearch:
    api_key = os.getenv("GOOGLE_API_KEY")
    custom_search_cx = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")
    def __init__(self):
        pass

    def _search(self, query, searchType = '', num=10, itemKey = 'link'):
        service = build("customsearch", "v1", developerKey=self.api_key)
        if searchType != '':
            serviceList = service.cse().list(q=query, cx=self.custom_search_cx, num=num, searchType = searchType)
        else:
            serviceList = service.cse().list(q=query, cx=self.custom_search_cx, num=num)
        result = serviceList.execute()

        links = []
        for item in result['items']:
            #print(item)
            links.append(item[itemKey])
        return links

    def search(self, query, num = 10, itemKey = 'link'):
        return self._search(query, '', num, itemKey)
    
    def searchImage(self, query, num = 10):
        return self._search(query, 'image', num)
    
    def searchImage2(self, query, num = 10, size = 'large'): #size : ''(anysize), large, medium, icon
        gis = GoogleImagesSearch(self.api_key, self.custom_search_cx)

        search_params = {
            'q': query,
            'num': num,
            'imgSize': size,
        }

        gis.search(search_params)
        links = []
        for image in gis.results():
            links.append(image.url)
        return links

class GoogleVoiceService:
    api_key = os.getenv("GOOGLE_API_KEY")
    saveUtils = SaveUtils('__output/')

    def __init__(self):
        pass

    def textToSpeech(self, text):
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        params = {"key": self.api_key}
        payload = {
            "input": {"text": text},
            "voice": {"languageCode": "ko-KR", "name": "ko-KR-Neural2-B"},
            "audioConfig": {
                "audioEncoding": "Linear16",
                "speakingRate": 1.1
                }
        }

        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()

        audio_content = response.json()["audioContent"]
        #audio_data = base64.b64decode(audio_content.encode())
        audio_data = base64.b64decode(audio_content)
        self.saveUtils.saveAudio('tts', audio_data)

class GoogleTranslateion:
    # https://cloud.google.com/translate/docs/languages
    api_key = 'api-project-427856712714' #os.getenv("GOOGLE_API_KEY")
    translate_client = translate.TranslationServiceClient()
    def __init__(self):
        pass

    def translateCloud(self, text, target_lang):
        # Split the input text into paragraphs based on new lines
        paragraphs = text.split('\n')

        # Translates each paragraph separately
        translated_paragraphs = []
        for paragraph in paragraphs:
            if paragraph != '':
                # Translates the paragraph
                response = self.translate_client.translate_text(
                    parent=f"projects/{self.api_key}/locations/global",
                    contents=[paragraph],
                    target_language_code=target_lang,
                )

                # Appends the translated paragraph to the result
                for translation in response.translations:
                    translated_paragraphs.append(html.unescape(translation.translated_text))
            else:
                translated_paragraphs.append(paragraph)

        # Join the translated paragraphs back together with new lines
        translated_text = '\n'.join(translated_paragraphs)
        return translated_text
            
    def translateFree(self, text, target_lang):
        # Create an instance of the Translator class
        translator = Translator()

        # Translate the text
        translation = translator.translate(text, dest=target_lang)

        # Print the translation
        print(f'Translated text: {translation.text}')
        return translation.text
    
    def translate(self, text, target_lang):
        return self.translateCloud(text, target_lang)