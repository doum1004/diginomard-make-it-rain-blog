import json
import os
import yt_dlp
import requests

from .utils import SaveUtils

class YoutubeLoader:
    saveUtils = SaveUtils('__output/youtube')
    def __init__(self):
        pass

    def download_json_from_url(self, url):
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            return None

    def find_node_with_key(self, node, target_key):
        if isinstance(node, dict):
            if target_key in node:
                return node[target_key]
            else:
                for value in node.values():
                    result = self.find_node_with_key(value, target_key)
                    if result is not None:
                        return result
        elif isinstance(self, node, list):
            for item in node:
                result = self.find_node_with_key(item, target_key)
                if result is not None:
                    return result
        return None

    def ms_to_mm_ss(self, ms):
        """Converts milliseconds to mm:ss:.. format."""
        minutes = int(ms / 60000)
        seconds = int(ms % 60000 / 1000)
        milliseconds = ms % 1000
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    def getScriptByTimeframe(self, json_data):
        scripts = ''
        previous_timeframe = None  # 이전 t_start_ms 값 저장 변수

        for event in json_data.get("events", []):
            timeframe = self.ms_to_mm_ss(int(event.get("tStartMs")))
            segs = event.get("segs", [])

            for seg in segs:
                utf8 = seg.get("utf8")

                if timeframe is not None and utf8:
                    if len(utf8) > 2:
                        if timeframe == previous_timeframe:
                            scripts += utf8.strip() + " "
                        else:
                            scripts += f"\n{timeframe}: {utf8.strip()} "

                        previous_timeframe = timeframe

        return scripts

    def getYoutubeScript(self, fileName, url, lang = 'ko'):
        ydl_opts = {'writesubtitles': True, 'skip-download': True}
        output = ''
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # ℹ️ ydl.sanitize_info makes the info json-serializable
            jsonDatas = ydl.sanitize_info(info) #infoData = json.dumps(ydl.sanitize_info(info))
            title = self.find_node_with_key(jsonDatas, 'title')
            automatic_captions = self.find_node_with_key(jsonDatas, 'automatic_captions')
            langURL = self.find_node_with_key(automatic_captions, lang)[0]['url']
            scriptData = self.download_json_from_url(langURL)
            scriptsByFrame = self.getScriptByTimeframe(scriptData)
            output = f'{title} scripts : \r\n\r\n{scriptsByFrame}'
            print(output)
        self.saveUtils.saveData(fileName, output)
        return output
        

    def getYoutubeVideoClip(self, fileName, url):
        #   ydl_opts = {
        # 'format': 'bestaudio/best', # choice of quality
        # 'extractaudio' : True,      # only keep the audio
        # 'audioformat' : "mp3",      # convert to mp3
        # 'outtmpl': '%(id)s.mp3',        # name the file the ID of the video
        # 'noplaylist' : True,        # only download single song, not playlist
        #               }

        dirs = self.saveUtils.getDirs()[:1]
        fileName = self.saveUtils.getUniqueFileNameUnderDirs(dirs, fileName, 'mp4')
        filePath = os.path.join(dirs[0], fileName)

        ydl_opts = {
        'format': 'bestvideo+bestaudio/best', # choice of quality +bestaudio[ext=m4a]/best
        'outtmpl': f'{filePath}',        # name the file the ID of the video
        'noplaylist' : True,        # only download single song, not playlist
                    }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    def downloadYoutube(self, fileName, url, lang):
        youtubeLoader.getYoutubeScript(fileName, url, lang)
        #youtubeLoader.getYoutubeVideoClip(fileName, url) # Need to fix for ffmpeg package issue on Window

youtubeLoader = YoutubeLoader()
url = input('Get URL : ')
if url == '':
    url = 'https://www.youtube.com/watch?v=3-hTgRO093Q'
youtubeLoader.downloadYoutube('YoutubeScript', url, 'en')