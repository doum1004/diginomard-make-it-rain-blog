import os
import requests
import base64
import html
from googleapiclient.discovery import build
from google_images_search import GoogleImagesSearch
from google.cloud import translate_v3 as translate
from googletrans import Translator

try:
    from utils import SaveUtils
except ImportError:  # Python 3
    from .utils import SaveUtils
    
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

    def _getSecFromDuration(self, duration):
        # duration format (such as PT13M3S, PT40S), convert it to sec
        sec = 0
        if duration[0] == 'P':
            duration = duration[2:]
        if duration[0] == 'T':
            duration = duration[1:]
        if duration.find('H') > 0:
            hour = duration.split('H')[0]
            duration = duration.split('H')[1]
            sec += int(hour) * 3600
        if duration.find('M') > 0:
            min = duration.split('M')[0]
            duration = duration.split('M')[1]
            sec += int(min) * 60
        if duration.find('S') > 0:
            sec += int(duration.split('S')[0])
        return sec - 1

    def searchVideo(self, query, num=10, cutDuration = 0):
        youtube = build("youtube", "v3", developerKey=self.api_key)

        response = youtube.search().list(q=query, part='id,snippet',
                                         type='video',
                                         videoEmbeddable="true",
                                         maxResults=num).execute()

        # get duration time
        for video in response['items'][:num]:
            id = video['id']['videoId']
            video_response = youtube.videos().list(id=id, part='contentDetails').execute()
            video['duration'] = video_response['items'][0]['contentDetails']['duration']        

        # Print out the first few video titles
        links = []
        for video in response['items'][:num]:
            title = video['snippet']['title']
            id = video['id']['videoId']
            duration = self._getSecFromDuration(video['duration'])
            link = f"https://www.youtube.com/embed/{id}"
            print(f"{title}, {id}, {duration} sec: {link}")

            if cutDuration > 0:
                offsetSec = 1
                maxCuts = 10
                nbCuts = max(int((cutDuration + offsetSec) / duration), maxCuts)
                for i in range(nbCuts):
                    start = int(i * (duration / nbCuts))
                    end = start + cutDuration
                    if end > duration:
                        end = duration
                    cutLink = f"{link}?start={start}&end={end}"
                    links.append(cutLink)
            else:
                links.append(link)
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
        translation = '\n'.join(translated_paragraphs)
        return translation
            
    def translateFree(self, text, target_lang):
        # Create an instance of the Translator class
        translator = Translator()
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    
    def translate(self, text, target_lang):
        translation = self.translateCloud(text, target_lang)
        print(f'Translated text: {translation}')
        return translation
