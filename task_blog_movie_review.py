import datetime
import json
import os
import re
import time
from diginomard_toolkit.google_api import GoogleSearch, GoogleTranslateion
from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.ai_openai_embed import OpenAIEmbedding
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import Preference, SaveUtils, Utils, FileUtils
from diginomard_toolkit.wiki import Wiki

googleSearch = GoogleSearch()

korTimeZone = datetime.timezone(datetime.timedelta(hours=9))
saveUtils = SaveUtils(f'__output/blog/movie/{Utils.getCurrentDate()}')

def getDate():
    return Utils.getCurrentDate()

def jsonToMarkdown(jsonData):
    def getImages(images, alt, hide = False):
        if len(images) == 0:
            return ''
        result = []
        for image in images:
            alt = 'hide' if hide else ''
            result.append(f'![{alt}]({image})')
        return '\n'.join(result)
    
    def getLinks(links):
        if len(links) == 0:
            return ''
        result = []
        for link in links:
            result.append(f'[{link}]({link})')
        return '\n'.join(result)
    
    lang = 'en'
    if 'lang' in jsonData:
        lang = jsonData['lang']
    time = '00' if lang == 'en' else Utils.getTimeBeforeCurrentHourInTimeZone(korTimeZone)
    date = f'{getDate()} {time}:00:00 {korTimeZone}"'
    
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
    if len(jsonData["images"]) > 0:
        result.append(f'image: {jsonData["images"][0]}')
    if 'uuid' in jsonData:
        result.append(f'uuid: {jsonData["uuid"]}')
    if 'lang' in jsonData:
        result.append(f'lang: {lang}')

    result.append('---')
    result.append('')
    
    for item in jsonData['content']:
        if item["text"] == "":
            continue
        result.append(f'## {item["heading"]}')
        result.append(item["text"])
        result.append('')
        result.append('')

    result.append(getImages(jsonData["images"], jsonData["topic"]))
    result.append(getLinks(jsonData["links"]))

    return '\n'.join(result)

def writeMarkdown(jsonFilePath):
    jsonData = Utils.readJsonFile(jsonFilePath)
    dir = os.path.dirname(jsonFilePath)
    # filename given by date-uuid ofjson and put under dir
    fileName = f'{getDate()}-{jsonData["uuid"]}-{jsonData["lang"]}.md'
    markdownFilePath = os.path.join(dir, fileName)
    markdownData = jsonToMarkdown(jsonData)
    FileUtils.writeFile(markdownFilePath, markdownData)

def searchWiki(q):
    result = googleSearch.search(f'wikipedia {q}')
    wiki = Wiki()
    wikiText = ''
    for item in result:
        if 'wikipedia.org' in item:
            wikiText = wiki.getWikiFromUrl(item)
            break
    input('Continue ? ')
    i = wikiText.rfind('References')
    if i >= 0:
        wikiText = wikiText[:i]
    wikiText.strip()
    return wikiText

def writeInTranslation(jsonFilePath, targetLang):
    gTranslator = GoogleTranslateion()
    jsonData = Utils.readJsonFile(jsonFilePath)
    jsonData['lang'] = targetLang
    # translate only 'topic' 'title' 'intro.content' 'main[].heading' 'main[].detail.content' 'conclusion.content'
    jsonData['topic'] = gTranslator.translate(jsonData['topic'], targetLang)
    jsonData['title'] = gTranslator.translate(jsonData['title'], targetLang)
    if 'description' in jsonData:
        jsonData['description'] = gTranslator.translate(jsonData['description'], targetLang)
    if 'tags' in jsonData:
        jsonData['tags'] = gTranslator.translate(jsonData['tags'], targetLang)
    
    for item in jsonData['content']:
        heading = item['heading']
        text = item['text']
        if item['text']:
            heading = gTranslator.translate(item['heading'], targetLang)
            text = gTranslator.translate(item['text'], targetLang)
        item['heading'] = heading
        item['text'] = text

    # add lang suffix to json file name
    jsonFilePath = os.path.splitext(jsonFilePath)[0] + f'-{targetLang}.json'
    FileUtils.writeFile(jsonFilePath, jsonData)

    writeMarkdown(jsonFilePath)

def writeMovieBlogPost(text, keyword, skipSummary = False):
    print(f'len({len(text)}) {text[:50]}')
    if len(text) < 100:
        return
    input('Continue ? ')
    
    subDir = FileUtils.fixDirectoryName(keyword)

    openai = OpenAI()
    if not skipSummary:
        text = openai.getSummary(text, pauseMaxToken=Preference.maxToken)
        summaryFilePath = os.path.join(saveUtils.baseDir, subDir, f"summary.json")
        FileUtils.writeFile(summaryFilePath, text)    

    prompts = PromptGenerator.getMovieBlogPostPrompts(keyword, text)
    responseText = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)

    responseFilePath = os.path.join(saveUtils.baseDir, subDir, f"response.json")
    FileUtils.writeFile(responseFilePath, responseText)    
    
    i1 = responseText.find('{')
    i2 = responseText.rfind('}')
    resultJson = responseText[i1:i2+1]

    if Utils.isJsonString(resultJson):
        resultJson = Utils.loadJson(resultJson)
    isValidJson = type(resultJson) == dict

    if not isValidJson:    
        FileUtils.writeFile(os.path.join(saveUtils.baseDir, subDir, f"article_invalid.json"), resultJson)
        print('-- Fix Json --')        
        prompts = PromptGenerator.getFixJsonPrompts(resultJson)
        resultJson = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
        if Utils.isJsonString(resultJson):
            resultJson = Utils.loadJson(resultJson)
        isValidJson = type(resultJson) == dict
        if not isValidJson:
            raise Exception('Invalid Json')

    if resultJson['tags'] is list:
        resultJson['tags'] = ','.join(resultJson['tags'])
        
    resultJson['uuid'] = Utils.shortUUID()
    resultJson['lang'] = 'en'
    images = googleSearch.searchImage(f'{keyword}', 10)
    resultJson['images'] = images

    link = googleSearch.search(f'justwatch {keyword}', 1)
    resultJson['links'] = link

    jsonFilePath = os.path.join(saveUtils.baseDir, subDir, f"article.json")
    FileUtils.writeFile(jsonFilePath, resultJson)    
    writeMarkdown(jsonFilePath)

    writeInTranslation(jsonFilePath, 'ko')

# def jsonFileToMarkdown(jsonFilePath, keyword):
#     jsonData = Utils.readJsonFile(jsonFilePath)
#     subDir = FileUtils.fixDirectoryName(keyword)
    
#     jsonData['uuid'] = Utils.shortUUID()
#     jsonData['lang'] = 'en'
#     images = googleSearch.searchImage(f'{keyword}', 10)
#     jsonData['images'] = images

#     link = googleSearch.search(f'justwatch {keyword}', 1)
#     jsonData['links'] = link

#     jsonFilePath = os.path.join(saveUtils.baseDir, subDir, f"article.json")
#     FileUtils.writeFile(jsonFilePath, jsonData)    
#     writeMarkdown(jsonFilePath)

#     writeInTranslation(jsonFilePath, 'ko')

# load text file 'C:\Workspace\Personal\diginomard-make-it-rain-blog\__output\blog\movie\2023-07-29\카메라를 멈추면 안 돼\article copy.json'


# def escape_inner_quotes(match):
#     return match.group(0).replace('"', '\\"')

# fixed_json_string = re.sub(r'(?<=":[\s]*")([^"]+)(?=["\s]*[,}])', escape_inner_quotes, txt)

# if Utils.isJsonString(fixed_json_string):
#     resultJson = Utils.loadJson(fixed_json_string)
# isValidJson = type(resultJson) == dict
# if not isValidJson:
#     input('Invalid Json. Continue ? ')

q = '모터사이클 다이어리 영화'
text = searchWiki(q)
#text = '''"\"Manchester by the Sea\" is a 2016 drama film directed by Kenneth Lonergan. It tells the story of a depressed man who becomes the legal guardian of his nephew after the death of his brother. The film explores themes of depression, grief, and dysfunctional families. It received critical acclaim for its performances and screenplay, winning multiple awards including two Academy Awards. The plot follows the protagonist as he deals with his guilt and tries to fulfill his responsibilities as a guardian.\nThe summary is about the events that occur after Lee Chandler's brother, Joe, dies, leaving Lee as the legal guardian of his teenage nephew, Patrick. Lee and Randi, Lee's ex-wife, divorce and he leaves town but reluctantly decides to stay in Manchester until the end of the school year for Patrick's sake. Patrick wants to live with his estranged mother, Elise, but Lee opposes it due to her history of alcoholism. Despite conflicts and strained relationships, Lee and Patrick re-establish their bond. Lee runs into Randi and they briefly reconnect, but Lee's emotional state causes him to get drunk and pick a fight. Lee arranges for Patrick to be adopted by a family friend so he can remain in Manchester. Lee and Patrick go fishing on Joe's boat, which Patrick inherits, and Lee plans to move to Boston but commits to finding a residence with an extra room so Patrick can visit.\nThe film Manchester by the Sea explores the theme of profound grief and the difficulties of recovery. The director, Kenneth Lonergan, presents the idea that grief cannot be contained and continues to affect a person's life. The film includes flashbacks and tragic events that are not smoothed over, but juxtaposes them with dark humor. Lonergan wanted to portray the unresolved nature of trauma and highlight the fact that not everyone easily gets over major events. The story is set in a blue-collar New England community, and specific details of the area were included in the film. The lead character's New England roots contribute to his emotional reticence. The film was initially brainstormed by Matt Damon and John Krasinski, who brought the idea to Lonergan.\nThe film \"Manchester by the Sea\" was initially a collaboration between Matt Damon and Kenneth Lonergan. Damon was set to star in the film and Lonergan was working on the screenplay. However, Damon later decided to step down from the lead role and Casey Affleck was chosen to replace him. Michelle Williams and Kyle Chandler were also cast in the film. Principal photography began in March 2015 in various locations in Massachusetts. The film was produced and financed by Kimberly Steward's company K Period Media, along with Damon's Pearl Street Films and other financiers. Lesley Barber was chosen to score the film, taking inspiration from New England church music.\nThe article discusses the score of the film \"Manchester by the Sea\" composed by Lesley Barber. Barber used a combination of hymns, a cappella vocals, and orchestration to create a soundtrack that reflected the emotions and themes of the film. She collaborated with her daughter to record vocals and incorporated classical pieces, including \"Adagio in G minor,\" which received mixed reviews. The score was deemed ineligible for an Oscar nomination due to the use of classical composers' music. Overall, the score was praised for its ability to add depth and emotion to the film.\n"'''
writeMovieBlogPost(text, q)

#writeInTranslation('C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/blog/movie/2023-10-23/콜럼버스 (2017년 영화)/article.json', 'ko')
#jsonFileToMarkdown('C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/chagpt/밀레니엄 여자를 증오한 남자들/230804-165515 copy.json', q)

# *최광희 : 치히로 상 (2023년 2월 넷플릭스 공개/일본/드라마/'이마이즈미 리키야' 감독)
# *거의없다 : 렌필드 (2023년 4월 개봉/미국/액션/'크리스 맥케이' 감독)
# *전민기 : See: 어둠의 나날(시즌 1) (2019년 11월 애플TV 공개/미국/판타지,SF/'프랜시스 로런스' 감독)
# *전민기 : 베컴 (2023년 넷플릭스 공개/영국/다큐멘터리/'데이비드 베컴' 주연)
# *전찬일 : 하나안 (2012년 개봉/우즈베키스탄/드라마/’박 루슬란‘ 감독)
# *라이너 : 기상천외한 헨리 슈거 이야기 (2023년 넷플릭스 공개/미국/코미디,드라마/'웨스 앤더슨' 감독)
# *거의없다 : 공작 (2023년 넷플릭스 공개/칠레/공포, 블랙 코미디/’파블로 라라인‘ 감독)
# *김의성 - 아주 평범한 사람들: 잊힌 홀로코스트 (2023년作/독일/다큐멘터리/만프레트 올덴부르크 감독)
# *라이너 - 내 사랑 (2017년作/아일랜드,캐나다/드라마/에이슬링 월쉬 감독)
# *거의없다 - 런 (2020년作/미국/미스터리/아니쉬 차간티 감독)
# *전찬일 - 봉오동 전투 (2019년作/한국/액션/원신연 감독)
# *최광희 - 모터사이클 다이어리 (2004년作/아르헨티나,미국 등/드라마/월터 살레스 감독)
# *라이너 - 애니매트릭스-오시리스 최후의 비행 (2003년作/미국/SF/앤드류 R. 존스 감독)
# *거의없다 - 프리미엄 러쉬 (2012년作/미국/액션/데이빗 코엡 감독)
# *전찬일 - 너의 순간 (2023년作/한국/로맨스/이상준 감독)
# *최광희 - 소름 (2001년作/한국/공포/윤종찬 감독)
# *최광희 - 강변의 무코리타 (2023년作/일본/드라마/오기가미 나오코 감독)
# *최광희 - 달짝지근해: 7510 (2023년作/한국/코미디/이한 감독)
# *전찬일 – 다섯 번째 흉추 (2023년作/한국/드라마/박세영 감독) 
# *라이너 - 비닐하우스 (2023년作/한국/범죄/이솔희 감독)
# *장규성 – 리바운드 (2023년作/한국/드라마/장항준 감독) 
# *라이너 – 슬픔의 삼각형 (2023년作/스웨덴,미국/코미디/루벤 외스틀룬드 감독) 
# *전찬일 – 구름에 가린 별 (1960년作/인도/드라마/리트윅 가탁 감독) 
# *최광희 - 미스 리틀 선샤인 (2006년作/미국/코미디,드라마/조나단 데이톤, 발레리 페리스 감독)
# *전찬일 – 리턴 투 서울 (2023년作/프랑스/드라마/데이비 추 감독) 
# *라이너 – 원더 (2017년作/미국/드라마/스티븐 크보스키 감독) 
# *거의없다 - 캐리 (2013년作/미국/공포/킴벌리 피어스 감독)
# *최광희 - 400번의 구타 (2016년作/프랑스/범죄,드라마/프랑수아 트뤼포 감독)
# *전찬일 – 스트레이트 스토리 (1999년作/프랑스,미국,영국/드라마/데이비드 린치 감독) 
# *라이너 – 패왕별희 (1993년作/중국/드라마,로맨스,멜로/첸 카이거 감독) 
# *거의없다 - 프로스트 VS 닉슨 (2009년作/미국,영국,프랑스/드라마/론 하워드 감독)
# *최광희 - 힘내세요, 병헌씨 (2013년作/한국/드라마,코미디/이병헌 감독)
# *정영진 - 힐빌리의 노래(2020년作/미국/드라마/론 하워드 감독)
# *전찬일 – 라스트 필름 쇼 (2023년作/인도,프랑스,미국/드라마/판 나린 감독) 
# *라이너 – 터미널 (2004년作/미국/코미디,멜로,로맨스/스티븐 스필버그 감독) 
# *거의없다 - 캐빈 인 더 우즈 (2012년作/미국/공포/스릴러/드류 고다드 감독)
# *최광희 - 지옥의 묵시록 (1998년作/미국/드라마,전쟁/프란시스 포드 코폴라 감독)
# *정영진 - 그녀의 조각들(2021년作/미국/드라마/코르넬 문드럭초 감독)
# *라이너 – 이웃집에 신이 산다 (2015년作/벨기에,프랑스/코미디,판타지/자코 반 도마엘 감독) 
# *거의없다 - 에어 (2023년作/미국/드라마/벤 애플렉 감독)
# *최광희 - 나라야마 부시코 (1983년作/일본/드라마/이마무라 쇼헤이 감독)
# *전찬일 - 여섯 개의 밤 (2023년作/대한민국/드라마,가족/최창환 감독)
# *라이너 – 카메론 포스트의 잘못된 교육 (2020년作/미국,영국/드라마/디자이리 아카반 감독) 
# *거의없다 - 원티드 (2008년作/미국,독일/액션/티무르 베크맘베토브 감독)
# *최광희 - 류이치 사카모토: 코다 (2018년作/일본/다큐멘터리/스티븐 쉬블 감독)
# *최욱 -  몸값 (2015년作/대한민국/액션/이충현 감독)
# *전찬일 - 틸 (2023년作/미국/드라마/치노늬 추크우 감독)
# *라이너 – 밀양 (2007년作/한국/드라마/이창동 감독) 
# *거의없다 - 사일런트 힐 (2006년作/캐나다,일본,미국,프랑스/공포,스릴러/크리스토프 갱스 감독)
# *최광희 - 위대한  쇼맨 (2017년作/미국/드라마,뮤지컬/마이클 그레이시 감독)
# *정영진 - 허트 로커 (2010년作/미국/전쟁, 액션/캐서린 비글로우 감독)
# *전찬일 - 모나리자와 블러드 문 (2023년作/미국/판타지, 미스터리, 스릴러/애나 릴리 아미푸르 감독)
# *라이너 – 더 레슬러 (2009년作/미국/액션,드라마/대런 아로노프스키 감독) 
# *거의없다 - 차별 (2023년作/대한민국/다큐멘터리/김지운, 김도희 감독)
# *최광희 - 월터의 상상은 현실이 된다 (2017년作/미국/모험,드라마,판타지/벤 스틸러 감독)
# *정영진 - 트라이얼 오브 더 시카고 7 (2020년作/미국/드라마,스릴러/아론 소킨 감독)
# *전찬일 - 이니셰린의 밴시 (2023년作/영국,미국,아일랜드/코미디,드라마/마틴 맥도나 감독)
# *라이너 – 밤쉘: 세상을 바꾼 폭탄선언 (2020년作/미국,캐나다/드라마/제이 로치 감독) 
# *거의없다 - 폴: 600미터 (2022년作/영국,미국/스릴러,액션/스콧 만 감독)
# *정영진 - 빅쇼트 (2016년作/미국/드라마/아담 맥케이 감독)
# *전찬일 - 그대 어이가리 (2023년作/대한민국/드라마/이창렬 감독)
# *라이너 – 동주 (2016년作/대한민국/드라마/이준익 감독) 
# *거의없다 - 그레이 맨(2022년作/미국/액션/앤서니 루소 & 조 루소 감독)
# *전찬일 - 더 웨일 (2023년作/미국/드라마/대런 아로노프스키 감독)
# *라이너 – 마더! (2017년作/미국/드라마,미스터리,스릴러/대런 아로노프스키 감독) 
# *거의없다 - 모두가 대통령의 사람들 (1976년作/미국/드라마,스릴러/알란 파큘라 감독)
# *전찬일 – 타르(2023년, 토드 필드 감독作)
# *라이너 – 스마트폰을 떨어뜨렸을 뿐인데(2023년, 김태준 감독作)
# *최광희 -택시 드라이버(1976년, 마틴 스코세이지 감독作)
# *거의없다 – 록키1(1977년, 존 G. 아빌드센 감독作)
# *전찬일 – 애프터썬(2023년, 샬롯 웰스 감독作)
# *라이너 – 경계선(2019년, 알리 아바시 감독作) 
# *최광희 - 나, 다니엘 블레이크(2016년, 켄 로치 감독作) 
# *거의없다 – 용서받지 못한 자(1993년, 클린트 이스트우드 감독作)



# Failed list

# *거의없다 - 스프린터 (2023년作/한국/드라마/최승연 감독)