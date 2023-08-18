import os
import re
import time
import datetime

try:
    from google_api import GoogleTranslateion
except ImportError:  # Python 3
    from .google_api import GoogleTranslateion
    
try:
    from video_search import VideoSearch
except ImportError:  # Python 3
    from .video_search import VideoSearch

try:
    from image_search import ImageSearch
except ImportError:  # Python 3
    from .image_search import ImageSearch
    
try:
    from utils import ImageUtils, SaveUtils, Utils, FileUtils
except ImportError:  # Python 3
    from .utils import ImageUtils, SaveUtils, Utils, FileUtils

try:
    from ai_scale_image import ScaleImage
except ImportError:  # Python 3
    from .ai_scale_image import ScaleImage

try:
    from prompts import PromptGenerator
except ImportError:  # Python 3
    from .prompts import PromptGenerator

try:
    from ai_openai import OpenAI
except ImportError:  # Python 3
    from .ai_openai import OpenAI
     
class WURG:
    korTimeZone = datetime.timezone(datetime.timedelta(hours=9))
    saveUtils = SaveUtils(f'__output/blog/wurg/{Utils.getCurrentDate()}')
    openai = OpenAI()
    gTranslator = GoogleTranslateion()
    scaleImage = ScaleImage()
    videoSearch = VideoSearch()
    def __init__(self):
        pass

    def getDate(self):
        #return Utils.getCurrentDate(korTimeZone)
        return "2023-06-29"

    def jsonToMarkdown(self, jsonData, production):
        nbMainContentImages = 2 if production else 20
        def getImages(images, alt):
            if len(images) == 0:
                return ''
            result = []
            for image in images:
                result.append(f'![{alt}]({image})')
            return '\n'.join(result)
        
        def getDetail(detail, imageAlt):
            content = detail['content']
            images = ''
            if "images" in detail:
                images = getImages(detail['images'][:nbMainContentImages], imageAlt)
            return f'{content}\n\n{images}'
        
        def getMain(main):
            result = []
            for item in main:
                heading = item['heading']
                detail = getDetail(item['detail'], item['tag'])
                result.append(f'## {heading}\n{detail}')
                result.append('')
                result.append('')
            return '\n'.join(result)
        
        lang = 'en'
        if 'lang' in jsonData:
            lang = jsonData['lang']
        time = '00' if lang == 'en' else Utils.getTimeBeforeCurrentHourInTimeZone(self.korTimeZone)
        date = f'{self.getDate()} {time}:00:00 {self.korTimeZone}"'
        
        # json to markdown like exFormat
        result = []
        result.append('---')
        result.append(f'layout: post')
        result.append(f'title: "{jsonData["title"]}"')
        if 'topic' in jsonData:
            result.append(f'topic: "{jsonData["topic"]}"')
        if 'description' in jsonData:
            result.append(f'description: "{jsonData["description"]}"')
        if 'tags' in jsonData:
            result.append(f'tags: "{jsonData["tags"]}"')
        result.append(f'date: {date}')
        result.append(f'categories: ')
        mainImage = ''
        if "images" in jsonData["intro"] and len(jsonData["intro"]["images"]) > 0:
            mainImage = jsonData["intro"]["images"][0]
        result.append(f'image: {mainImage}')
        result.append(f'uuid: {jsonData["uuid"]}')
        result.append(f'lang: {lang}')

        result.append('---')
        result.append('')
        result.append(f'{jsonData["intro"]["content"]}')
        result.append('')
        if "images" in jsonData["intro"]:
            result.append(f'{getImages(jsonData["intro"]["images"], "hide")}')
        result.append('')
        result.append('')
        result.append(f'{getMain(jsonData["main"])}')
        result.append('')
        result.append('')
        result.append(f'{jsonData["conclusion"]["content"]}')
        result.append('')
        if "images" in jsonData["conclusion"]:
            result.append(f'{getImages(jsonData["conclusion"]["images"][:1], jsonData["topic"])}')
        result.append('')
        return '\n'.join(result)

    def writeMarkdown(self, jsonFilePath, production):
        jsonData = Utils.readJsonFile(jsonFilePath)
        dir = os.path.dirname(jsonFilePath)
        # filename given by date-uuid ofjson and put under dir
        fileName = f'{self.getDate()}-{jsonData["uuid"]}-{jsonData["lang"]}.md'
        markdownFilePath = os.path.join(dir, fileName)
        markdownData = self.jsonToMarkdown(jsonData, production)
        FileUtils.writeFile(markdownFilePath, markdownData)

    def getImageLinks(self, keywords: list, nbLinks = 5):
        # remove duplicates of keywords
        keywords = list(dict.fromkeys(keywords))
        print(f'getImages : {keywords}')
        imageSearch = ImageSearch()
        imagePaths = []
        for keyword in keywords:
            imagePaths.extend(imageSearch.getImageFromBingSearch(f'{keyword}', nbLinks))
        return imagePaths

    def getVideoLinks(self, keywords: list, nbLinks = 5):
        # remove duplicates of keywords
        keywords = list(dict.fromkeys(keywords))
        print(f'getVideos : {keywords}')

        links = []
        for keyword in keywords:
            links.extend(self.videoSearch.searchPexels(f'{keyword}', nbLinks))
        return links
    
    def fillResources(self, jsonData, baseDir, resetFolder = True, fillImages = True, fillVideos = True):
        # reset folder if exist
        if resetFolder:
            imagesDir = os.path.join(baseDir, 'images')
            if os.path.isdir(imagesDir):
                Utils.deleteFilesUnderDir(imagesDir)
            videosDir = os.path.join(baseDir, 'videos')
            if os.path.isdir(videosDir):
                Utils.deleteFilesUnderDir(videosDir)

        images = []
        videos = []
        keywords = [jsonData['topic']]
        if fillImages:
            images = self.getImageLinks(keywords, 5)
        if fillVideos:
            videos = self.getVideoLinks(keywords, 5)
        jsonData['intro']['images'] = images
        jsonData['intro']['videos'] = videos

        for item in jsonData['main']:
            keywords = [item['heading'], f"{jsonData['topic']} {item['heading']}"]
            if 'tag' in item:
                keywords.append(item['tag'])

            images = []
            videos = []
            if fillImages:
                images = self.getImageLinks(keywords, 5)
            if fillVideos:
                videos = self.getVideoLinks(keywords, 5)
            item['detail']['images'] = images
            item['detail']['videos'] = videos

        jsonData['conclusion']['images'] = []
        jsonData['conclusion']['videos'] = []
            
    def fillDraftJson(self, jsonData, baseDir):
        FileUtils.createDir(baseDir)
        
        # traverse main heading to remove number prefix
        for item in jsonData['main']:
            heading = item['heading']
            pattern = re.compile(r'\d+\.\s+')
            heading = pattern.sub('', heading)
            item['heading'] = heading

        jsonData['uuid'] = Utils.shortUUID()
        jsonData['lang'] = 'en'
        self.fillResources(jsonData, baseDir, fillImages=False)

    def writeWURG(self, keyword):
        keyword = keyword.strip()
        print(f'WURG Keyword: {keyword}')

        messages = []
        prompts = PromptGenerator.getWURGPrompts(keyword)
        responseText = self.openai.chatMessageContents(prompts[0], prompts[1], prompts[2], messages, keyword = keyword)

        i1 = responseText.find('{')
        i2 = responseText.rfind('}')
        resultJson = responseText[i1:i2+1]

        if Utils.isJsonString(resultJson):
            resultJson = Utils.loadJson(resultJson)
        isValidJson = type(resultJson) == dict

        fileName = 'article'
        subDir = FileUtils.fixDirectoryName(keyword)
        baseDir = os.path.join(self.saveUtils.baseDir, subDir)

        if not isValidJson:    
            FileUtils.writeFile(os.path.join(baseDir, f"{fileName}_invalid.json"), resultJson)
            print('-- Fix Json --')        
            prompts = PromptGenerator.getFixJsonPrompts(resultJson)
            resultJson = self.openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)

        resultJson['topic'] = keyword
        self.fillDraftJson(resultJson, baseDir)
        jsonFilePath = os.path.join(baseDir, f"{fileName}.json")
        FileUtils.writeFile(jsonFilePath, resultJson)
        self.writeMarkdown(jsonFilePath, False)

        baseDir = self.renameFolderByUUID(baseDir, resultJson)
        return resultJson

    def fillSEODescription(self, jsonData):
        if 'description-pass' in jsonData:
            return
        
        # get intro content, each main headings
        strData = 'topic: ' + jsonData['topic']
        strData = 'title: ' + jsonData['title']
        strData += jsonData['intro']['content']
        for item in jsonData['main']:
            strData += 'Heading: ' + item['heading']
            
        prompts = PromptGenerator.getSEODescription(strData, jsonData['lang'])
        responseText = self.openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
        jsonData['description'] = responseText
        time.sleep(5) # up to 20 api calls per min

        prompts = PromptGenerator.getHashTags(strData, jsonData['lang'])
        responseText = self.openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
        jsonData['tags'] = responseText
        jsonData['description-pass'] = True

    def writeAllWURGUnderDir(self, dir):
        # iternate folder and key name of dirname as keyword
        for dirname in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, dirname)):
                # delete files under dir
                Utils.deleteFilesUnderDir(os.path.join(dir, dirname))
                # Write
                keyword = dirname
                self.writeWURG(keyword)
                # sleep 5 sec
                time.sleep(10)

    def renameFolderByUUID(self, baseDir, jsonData):
        # change folder name as uuid in json
        dirname = os.path.basename(baseDir)
        newDir = baseDir
        if dirname != jsonData['uuid']:
            newDir = os.path.join(os.path.dirname(baseDir), jsonData['uuid'])
            # try and tach to retry
            while True:
                try:
                    os.rename(baseDir, newDir)
                    break
                except:
                    # Show error and wait for user input
                    print(f'Error on rename {baseDir} to {newDir}')
                    input('Press any key to continue')
        return newDir

    # jsonPostProcess: removeImageListItemIfNotExist, change folder name as uuid in json, change json file name ()
    def jsonPostProcess(self, jsonFilePath):
        def imageProcess(dir, filename, images: list):
            # downloadImagesIfUrl, removeImageItemIfNotExistInFile
            imageDir = os.path.join(dir, 'images')
            for idx, image in reversed(list(enumerate(images))):
                if Utils.isUrl(image):
                    downloadedImagePath = ImageUtils.downloadImage(image, imageDir, filename)
                    if downloadedImagePath:
                        images[idx] = FileUtils.getRelPath(dir, downloadedImagePath)
                    else:
                        images[idx] = ''
                elif not os.path.isfile(os.path.join(dir, image)):
                    images[idx] = ''

                if images[idx] == '':
                    images.pop(idx)

            for image in images:
                self.scaleImage.scale(os.path.join(dir, image))

        def deleteFileIfNotExistInList(dir, images: list):
            imageDir = os.path.join(dir, 'images')
            for idx, filename in reversed(list(enumerate(os.listdir(imageDir)))):
                if os.path.isfile(os.path.join(imageDir, filename)):
                    exist = False
                    for image in images:
                        if filename == os.path.basename(image):
                            exist = True
                            break
                    if not exist:
                        os.remove(os.path.join(imageDir, filename))
                    
        # remove image list item if not exist
        jsonData = Utils.readJsonFile(jsonFilePath)
        baseDir = os.path.dirname(jsonFilePath)
        if not jsonData['lang']:
            jsonData['lang'] = 'en'
        
        imageProcess(baseDir, 'intro', jsonData['intro']['images'])
        for idx, item in enumerate(jsonData['main']):
            imgFileName = 'main' + str(idx + 1)
            imageProcess(baseDir, imgFileName, item['detail']['images'])
        imageProcess(baseDir, 'con', jsonData['conclusion']['images'])

        images = []
        images.extend(jsonData['intro']['images'])
        images.extend(jsonData['conclusion']['images'])
        for item in jsonData['main']:
            images.extend(item['detail']['images'])
        deleteFileIfNotExistInList(baseDir, images)

        introImages = []
        introImages.extend(jsonData['intro']['images'])
        introImages.extend(jsonData['conclusion']['images'])
        jsonData['intro']['images'] = introImages[:1]
        jsonData['conclusion']['images'] = introImages[1:]
        self.fillSEODescription(jsonData)

        # change folder name as uuid in json
        baseDir = self.renameFolderByUUID(baseDir, jsonData)

        # update json file path keep filename
        jsonFilePath = os.path.join(baseDir, os.path.basename(jsonFilePath))

        # save json and markdown    
        FileUtils.writeFile(jsonFilePath, jsonData)
        return jsonFilePath

    def traverseDictOrListToTranslate(self, data, targetLang, blacklist):
        if type(data) == dict:
            for key in data:
                if key not in blacklist:
                    if type(data[key]) == str:
                        data[key] = self.gTranslator.translate(data[key], targetLang)
                    else:
                        self.traverseDictOrListToTranslate(data[key], targetLang, blacklist)
        elif type(data) == list:
            for idx, item in enumerate(data):
                if type(item) == str:
                    data[idx] = self.gTranslator.translate(item, targetLang)
                else:
                    self.traverseDictOrListToTranslate(item, targetLang, blacklist)


    def translateAndSaveJson(self, jsonFilePath, targetLang):
        jsonData = Utils.readJsonFile(jsonFilePath)
        
        blacklist = ['uuid', 'lang', 'images', 'description-pass']
        jsonData['lang'] = targetLang
        self.traverseDictOrListToTranslate(jsonData, targetLang, blacklist)

        # add lang suffix to json file name
        jsonFilePath = os.path.splitext(jsonFilePath)[0] + f'-{targetLang}.json'
        FileUtils.writeFile(jsonFilePath, jsonData)
        return jsonFilePath

    def fillNewImages(self, jsonFilePath):
        jsonData = Utils.readJsonFile(jsonFilePath)
        baseDir = os.path.dirname(jsonFilePath)
        self.fillResources(jsonData, baseDir, fillVideos=False)
        FileUtils.writeFile(jsonFilePath, jsonData)

    def copyImages(self, sourceJsonFilePath, targetJsonFilePath):
        sourceJsonData = Utils.readJsonFile(sourceJsonFilePath)
        targetJsonData = Utils.readJsonFile(targetJsonFilePath)
        targetJsonData['intro']['images'] = sourceJsonData['intro']['images']
        targetJsonData['conclusion']['images'] = sourceJsonData['conclusion']['images']
        for idx, item in enumerate(targetJsonData['main']):
            targetJsonData['main'][idx]['detail']['images'] = sourceJsonData['main'][idx]['detail']['images']
        FileUtils.writeFile(targetJsonFilePath, targetJsonData)

    def runTranslation(self, dir, lang):
        for dirname in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, dirname)):
                jsonFilePath = os.path.join(dir, dirname, 'article.json')
                if os.path.isfile(jsonFilePath):
                    jsonFilePath = self.jsonPostProcess(jsonFilePath)

                    if lang != '':
                        self.translateAndSaveJson(jsonFilePath, lang)
                else:
                    print(f'Not found {jsonFilePath}')

    def runMarkdown(self, dir):
        for dirname in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, dirname)):
                jsonFilePath = os.path.join(dir, dirname, 'article.json')
                if os.path.isfile(jsonFilePath):
                    jsonFilePath = self.jsonPostProcess(jsonFilePath)
                    self.writeMarkdown(jsonFilePath, True)

                    jsonFilePath_ko = os.path.join(dir, dirname, 'article-ko.json')
                    if os.path.isfile(jsonFilePath_ko):
                        self.copyImages(jsonFilePath, jsonFilePath_ko)
                        jsonFilePath_ko = self.jsonPostProcess(jsonFilePath_ko)
                        self.writeMarkdown(jsonFilePath_ko, True)
                else:
                    print(f'Not found {jsonFilePath}')

        # for dirname in os.listdir(dir):
        #     dirPath = os.path.join(dir, dirname)
        #     if os.path.isdir(dirPath):
        #         for filename in os.listdir(dirPath):
        #             if filename.startswith('article') and filename.endswith('.json'):
        #                 jsonFilePath = os.path.join(dirPath, filename)
        #                 jsonFilePath = self.jsonPostProcess(jsonFilePath)
        #                 if os.path.isfile(jsonFilePath):
        #                     self.writeMarkdown(jsonFilePath, True)
        #                 else:
        #                     print(f'Not found {jsonFilePath}')


    def getMainHeadings(self, jsonData):
        keywords = []
        for item in jsonData['main']:
            keywords.append(item['heading'])
        return keywords

    def writeWURGs(self, keywords: list, writeHeadings = False):
        for keyword in keywords:
            result = self.writeWURG(keyword)
            if writeHeadings:
                # ask user to write headings, start after 5 sec
                print('Write headings. Continue after 5 sec')
                time.sleep(5)

                headings = self.getMainHeadings(result)
                for heading in headings:
                    self.writeWURG(f'{heading} ({keyword})')

    def writeMarkdownUnder(self, dir):
        for dirname in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, dirname)):
                jsonFilePath = os.path.join(dir, dirname, 'article.json')
                if os.path.isfile(jsonFilePath):
                    self.writeMarkdown(jsonFilePath, False)
