import os
import time
import datetime
from diginomard_toolkit.google_api import GoogleTranslateion
from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.image_search import ImageSearch
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import SaveUtils, Utils, FileUtils

saveUtils = SaveUtils('__output/blog/wurg')
timeZone = datetime.timezone(datetime.timedelta(hours=9))

def getDate():
    #return Utils.getCurrentDate(timeZone)
    return "2023-06-27"

def jsonToMarkdown(jsonData):
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
        images = getImages(detail['images'][:2])
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
    time = '00' if lang == 'en' else Utils.getTimeBeforeCurrentHour(timeZone)
    date = f'{getDate()} {time}:00:00 {timeZone}"'
    
    # json to markdown like exFormat
    result = []
    result.append('---')
    result.append(f'layout: post')
    result.append(f'title: "{jsonData["title"]}"')
    if 'description' in jsonData:
        result.append(f'description: "{jsonData["description"]}"')
    result.append(f'date: {date}')
    result.append(f'categories: ')
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

def writeMarkdown(jsonFilePath):
    jsonData = Utils.readJsonFile(jsonFilePath)
    dir = os.path.dirname(jsonFilePath)
    # filename given by date-uuid ofjson and put under dir
    fileName = f'{getDate()}-{jsonData["uuid"]}-{jsonData["lang"]}.md'
    markdownFilePath = os.path.join(dir, fileName)
    markdownData = jsonToMarkdown(jsonData)
    FileUtils.writeFile(markdownFilePath, markdownData)

def downloadImage(imageDir, keywords: list, fileName, nbImages = 5):
    baseDir = os.path.dirname(imageDir)

    imageSearch = ImageSearch()
    imagePaths = []
    for keyword in keywords:
        imagePaths.extend(imageSearch.getImageFromBing(f'{keyword}', int(nbImages / len(keywords))))
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

def fillImages(jsonData, baseDir, resetFolder = True):
    imageDir = os.path.join(baseDir, 'images')
    # reset folder if exist
    if os.path.isdir(imageDir) and resetFolder:
        Utils.deleteFilesUnderDir(imageDir)
    
    topicImages = downloadImage(imageDir, [jsonData['topic']], 'intro', 10)
    jsonData['intro']['images'] = topicImages
    for idx, item in enumerate(jsonData['main']):
        imgFileName = 'main' + str(idx + 1)
        keywords = [item['heading']]
        if 'tag' in item:
            keywords.append(item['tag'])
        images = downloadImage(imageDir, keywords, imgFileName, 10)
        item['detail']['images'] = images
    jsonData['conclusion']['images'] = []

def fillDraftJson(jsonData, baseDir):
    # create baseDir if not exist
    if not os.path.isdir(baseDir):
        os.makedirs(baseDir)
        
    jsonData['uuid'] = Utils.shortUUID()
    jsonData['lang'] = 'en'
    fillImages(jsonData, baseDir)

def writeWURG(keyword):
    keyword = keyword.strip()
    openai = OpenAI()

    prompts = PromptGenerator.getWURGPrompts(keyword)
    responseText = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)

    i1 = responseText.find('{')
    i2 = responseText.rfind('}')
    resultJson = responseText[i1:i2+1]

    isValidJson = type(Utils.loadJson(resultJson)) == dict

    fileName = 'article'
    subDir = keyword
    baseDir = os.path.join(saveUtils.baseDir, subDir)

    if not isValidJson:    
        FileUtils.writeFile(os.path.join(baseDir, f"{fileName}_invalid.json"), resultJson)
        print('-- Fix Json --')        
        prompts = PromptGenerator.getFixJsonPrompts(resultJson)
        resultJson = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)

    resultJson = fillDraftJson(resultJson, baseDir)
    jsonFilePath = os.path.join(baseDir, f"{fileName}.json")
    FileUtils.writeFile(jsonFilePath, resultJson)
    writeMarkdown(jsonFilePath)

def fillSEODescription(jsonData):
    if 'description-pass' in jsonData:
        return
    
    openai = OpenAI()
    prompts = PromptGenerator.getSEODescription(jsonData)
    responseText = openai.chatMessageContents(prompts[0], prompts[1], prompts[2])
    jsonData['description'] = responseText
    jsonData['description-pass'] = True

def writeAllWURGUnderDir(dir):
    # iternate folder and key name of dirname as keyword
    for dirname in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, dirname)):
            # delete files under dir
            Utils.deleteFilesUnderDir(os.path.join(dir, dirname))
            # Write
            keyword = dirname
            writeWURG(keyword)
            # sleep 5 sec
            time.sleep(10)

# jsonPostProcess: removeImageListItemIfNotExist, change folder name as uuid in json, change json file name ()
def jsonPostProcess(jsonFilePath):
    def removeList(images):
        # enumerate reverse remove image from list if not exist
        for idx, image in reversed(list(enumerate(images))):
            if not os.path.isfile(os.path.join(baseDir, image)):
                images.pop(idx)

    # remove image list item if not exist
    jsonData = Utils.readJsonFile(jsonFilePath)
    baseDir = os.path.dirname(jsonFilePath)
    if not jsonData['lang']:
        jsonData['lang'] = 'en'
    removeList(jsonData['intro']['images'])
    for item in jsonData['main']:
        removeList(item['detail']['images'])
    removeList(jsonData['conclusion']['images'])
    introImages = jsonData['intro']['images']
    introImages.extend(jsonData['conclusion']['images'])
    jsonData['intro']['images'] = introImages[:1]
    jsonData['conclusion']['images'] = introImages[1:]
    fillSEODescription(jsonData)

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

def translateAndSaveJson(jsonFilePath, targetLang):
    gTranslator = GoogleTranslateion()
    jsonData = Utils.readJsonFile(jsonFilePath)
    jsonData['lang'] = targetLang
    # translate only 'topic' 'title' 'intro.content' 'main[].heading' 'main[].detail.content' 'conclusion.content'
    jsonData['topic'] = gTranslator.translate(jsonData['topic'], targetLang)
    jsonData['title'] = gTranslator.translate(jsonData['title'], targetLang)
    jsonData['description'] = gTranslator.translate(jsonData['description'], targetLang)
    jsonData['intro']['content'] = gTranslator.translate(jsonData['intro']['content'], targetLang)
    for item in jsonData['main']:
        item['heading'] = gTranslator.translate(item['heading'], targetLang)
        item['detail']['content'] = gTranslator.translate(item['detail']['content'], targetLang)
    jsonData['conclusion']['content'] = gTranslator.translate(jsonData['conclusion']['content'], targetLang)
    # add lang suffix to json file name
    jsonFilePath = os.path.splitext(jsonFilePath)[0] + f'-{targetLang}.json'
    FileUtils.writeFile(jsonFilePath, jsonData)
    return jsonFilePath

def fillNewImages(jsonFilePath):
    jsonData = Utils.readJsonFile(jsonFilePath)
    baseDir = os.path.dirname(jsonFilePath)
    fillImages(jsonData, baseDir)
    FileUtils.writeFile(jsonFilePath, jsonData)

# find 'article.json', run removeImageListItemIfNotExist and translateAndSaveJson
def runPostProcessUnder(dir, lang, newImages = False):
    for dirname in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, dirname)):
            jsonFilePath = os.path.join(dir, dirname, 'article.json')
            if os.path.isfile(jsonFilePath):
                if newImages:
                    fillNewImages(jsonFilePath)
                jsonFilePath = jsonPostProcess(jsonFilePath)
                writeMarkdown(jsonFilePath)
                translatedJsonFilePath = translateAndSaveJson(jsonFilePath, lang)
                writeMarkdown(translatedJsonFilePath)
            else:
                print(f'Not found {jsonFilePath}')

#runPostProcessUnder('__output/blog/wurg_production/', 'ko', False)
#path = 'C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/blog/wurg_done/sa21-05b7b1d1/230718-180949__0__ko.json'
#path = path.replace('\\', '/')
#keyword = input('Give keyword : ')
#keyword = 'how to wake up early'
#writeAllWURGUnderDir(keyword)
#fillJsonData('__output/blog/wurg/Best Economy news website/230718-183436__0.json')
#searchAll('__output/blog/wurg')
