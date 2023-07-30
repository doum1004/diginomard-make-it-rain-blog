import os
import time
import datetime

try:
    from diginomard_toolkit.google_api import GoogleTranslateion
except ImportError:  # Python 3
    from .diginomard_toolkit.google_api import GoogleTranslateion
    
try:
    from diginomard_toolkit.image_search import ImageSearch
except ImportError:  # Python 3
    from .diginomard_toolkit.image_search import ImageSearch
    
try:
    from diginomard_toolkit.ai_openai import OpenAI
except ImportError:  # Python 3
    from .diginomard_toolkit.ai_openai import OpenAI
    
try:
    from diginomard_toolkit.prompts import PromptGenerator
except ImportError:  # Python 3
    from .diginomard_toolkit.prompts import PromptGenerator
    
try:
    from diginomard_toolkit.utils import ImageUtils, SaveUtils, Utils, FileUtils
except ImportError:  # Python 3
    from .diginomard_toolkit.utils import ImageUtils, SaveUtils, Utils, FileUtils

class WURG:
    korTimeZone = datetime.timezone(datetime.timedelta(hours=9))
    saveUtils = SaveUtils(f'__output/blog/wurg/{Utils.getCurrentDate()}')
    openai = OpenAI()
    gTranslator = GoogleTranslateion()
    def __init__(self):
        pass

    def getDate(self):
        #return Utils.getCurrentDate(korTimeZone)
        return "2023-06-29"

    def jsonToMarkdown(self, jsonData, production):
        nbMainContentImages = 2 if production else 20
        def getImages(images, hide = False):
            if len(images) == 0:
                return ''
            result = []
            for image in images:
                alt = 'hide' if hide else ''
                result.append(f'![{alt}]({image})')
            return '\n'.join(result)
        
        def getDetail(detail):
            content = detail['content']
            images = getImages(detail['images'][:nbMainContentImages])
            return f'{content}\n\n{images}'
        
        def getMain(main):
            result = []
            for item in main:
                heading = item['heading']
                detail = getDetail(item['detail'])
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
        if 'description' in jsonData:
            result.append(f'description: "{jsonData["description"]}"')
        if 'tags' in jsonData:
            result.append(f'tags: "{jsonData["tags"]}"')
        result.append(f'date: {date}')
        result.append(f'categories: ')
        if len(jsonData["intro"]["images"]) > 0:
            result.append(f'image: {jsonData["intro"]["images"][0]}')
        result.append(f'uuid: {jsonData["uuid"]}')
        result.append(f'lang: {lang}')

        result.append('---')
        result.append('')
        result.append(f'{jsonData["intro"]["content"]}')
        result.append('')
        result.append(f'{getImages(jsonData["intro"]["images"], True)}')
        result.append('')
        result.append('')
        result.append(f'{getMain(jsonData["main"])}')
        result.append('')
        result.append('')
        result.append(f'{jsonData["conclusion"]["content"]}')
        result.append('')
        result.append(f'{getImages(jsonData["conclusion"]["images"][:1])}')
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

    def downloadImage(self, imageDir, keywords: list, fileName, nbImages = 5):
        # remove duplicates of keywords
        keywords = list(dict.fromkeys(keywords))
        baseDir = os.path.dirname(imageDir)

        imageSearch = ImageSearch()
        imagePaths = []
        for keyword in keywords:
            imagePaths.extend(imageSearch.getImageFromBing(f'{keyword}', nbImages))
        if len(imagePaths) == 0:
            return []
        
        imagePaths = Utils.moveFiles(imagePaths, imageDir, fileName, 1)
        # replace imagePaths in relative path from baseDir
        relPaths = []
        for path in imagePaths:
            relPath = path.replace(baseDir, '')
            # replace \\ to /
            relPath = relPath.replace('\\', '/')
            if relPath[0] == '/':
                relPath = relPath[1:]
            relPaths.append(relPath)        
        return relPaths

    def getImages(self, imageDir, keywords: list, fileName, nbImages = 5):
        # remove duplicates of keywords
        keywords = list(dict.fromkeys(keywords))
        baseDir = os.path.dirname(imageDir)

        imageSearch = ImageSearch()
        imagePaths = []
        for keyword in keywords:
            imagePaths.extend(imageSearch.getImageFromBingSearch(f'{keyword}', nbImages))
        return imagePaths

    def fillImages(self, jsonData, baseDir, resetFolder = True):
        imageDir = os.path.join(baseDir, 'images')
        # reset folder if exist
        if os.path.isdir(imageDir) and resetFolder:
            Utils.deleteFilesUnderDir(imageDir)
        
        topicImages = self.getImages(imageDir, [jsonData['topic']], 10)
        jsonData['intro']['images'] = topicImages
        for idx, item in enumerate(jsonData['main']):
            keywords = [item['heading']]
            if 'tag' in item:
                keywords.append(item['tag'])
            images = self.getImages(imageDir, keywords, 5 * len(keywords))
            item['detail']['images'] = images
        jsonData['conclusion']['images'] = []

    def fillDraftJson(self, jsonData, baseDir):
        FileUtils.createDir(baseDir)
            
        jsonData['uuid'] = Utils.shortUUID()
        jsonData['lang'] = 'en'
        self.fillImages(jsonData, baseDir)

    def writeWURG(self, keyword):
        keyword = keyword.strip()

        prompts = PromptGenerator.getWURGPrompts(keyword)
        responseText = self.openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)

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

        self.fillDraftJson(resultJson, baseDir)
        jsonFilePath = os.path.join(baseDir, f"{fileName}.json")
        FileUtils.writeFile(jsonFilePath, resultJson)
        self.writeMarkdown(jsonFilePath, False)
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
            
        prompts = PromptGenerator.getSEODescription(strData)
        responseText = self.openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
        jsonData['description'] = responseText
        time.sleep(5) # up to 20 api calls per min

        prompts = PromptGenerator.getHashTags(strData)
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

    # jsonPostProcess: removeImageListItemIfNotExist, change folder name as uuid in json, change json file name ()
    def jsonPostProcess(self, jsonFilePath):
        def imageProcess(dir, filename, images: list):
            # downloadImagesIfUrl, removeImageItemIfNotExistInFile
            imageDir = os.path.join(dir, 'images')
            for idx, image in enumerate(images):
                if Utils.isUrl(image):
                    downloadedImagePath = ImageUtils.downloadImage(image, imageDir, filename)
                    if downloadedImagePath:
                        images[idx] = FileUtils.getRelPath(dir, downloadedImagePath)
                elif not os.path.isfile(os.path.join(dir, image)):
                    images.pop(idx)

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
        dirname = os.path.basename(baseDir)
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
            baseDir = newDir

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
        self.fillImages(jsonData, baseDir)
        FileUtils.writeFile(jsonFilePath, jsonData)

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
            dirPath = os.path.join(dir, dirname)
            if os.path.isdir(dirPath):
                for filename in os.listdir(dirPath):
                    if filename.startswith('article') and filename.endswith('.json'):
                        jsonFilePath = os.path.join(dirPath, filename)
                        if os.path.isfile(jsonFilePath):
                            self.writeMarkdown(jsonFilePath, True)
                        else:
                            print(f'Not found {jsonFilePath}')


    def getMainHeadings(self, jsonData):
        keywords = []
        for item in jsonData['main']:
            keywords.append(item['heading'])
        return keywords

    def writeWURGs(self, keywords: list, writeHeadings = False):
        for keyword in keywords:
            result = self.writeWURG(keyword)
            if writeHeadings:
                headings = self.getMainHeadings(result)
                for heading in headings:
                    self.writeWURG(heading)

    def writeMarkdownUnder(self, dir):
        for dirname in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, dirname)):
                jsonFilePath = os.path.join(dir, dirname, 'article.json')
                if os.path.isfile(jsonFilePath):
                    self.writeMarkdown(jsonFilePath, False)
