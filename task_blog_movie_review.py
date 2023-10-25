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
    if 'links' in jsonData and len(jsonData["links"]) > 0:
        result.append(f'link: {jsonData["links"][0]}')
        result.append(f'link-desc: Watch movie in steaming {jsonData["title"]}')

    result.append('---')
    result.append('')
    
    for item in jsonData['contents']:
        if item["text"] == "":
            continue
        result.append(f'## {item["heading"]}')
        result.append(item["text"])
        result.append('')
        result.append('')

    result.append(getImages(jsonData["images"], jsonData["topic"]))
    #result.append(getLinks(jsonData["links"]))

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
    
    for item in jsonData['contents']:
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

def writeMovieBlogPost(reference, keyword, skipSummary = False):
    print(f'len({len(reference)}) {text[:50]}')
    if len(reference) < 100:
        return
    input('Continue ? ')
    
    subDir = FileUtils.fixDirectoryName(keyword)

    openai = OpenAI()
    if not skipSummary:
        reference = openai.getSummary(reference, pauseMaxToken=Preference.maxToken)
        summaryFilePath = os.path.join(saveUtils.baseDir, subDir, f"summary.txt")
        FileUtils.writeFile(summaryFilePath, reference)    

    #prompts = PromptGenerator.getMovieBlogPostPrompts(keyword, reference)
    prompts1 = PromptGenerator.getMovieBlogPostPrompts(keyword, reference)
    response1Text = openai.chatMessageContents(prompts1[0], prompts1[1], prompts1[2], keyword = keyword)
    response1FilePath = os.path.join(saveUtils.baseDir, subDir, f"response1.txt")
    FileUtils.writeFile(response1FilePath, response1Text)    

    prompts = PromptGenerator.getJson(response1Text, 'templates/template_movie.json')
    responseText = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
    responseFilePath = os.path.join(saveUtils.baseDir, subDir, f"response.txt")
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

    if 'tags' in resultJson and isinstance(resultJson['tags'], list):
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

q = '원더 영화'
text = searchWiki(q)
#text = '''The Animatrix is a 2003 American-Japanese adult animated science-fiction anthology film. It is made up of nine animated short films that detail the backstory of The Matrix film series. The film shows the major events of the war between humanity and machines, which led to the creation of the Matrix. It also provides additional stories that expand the universe and connect to the Matrix film series. The film has generally received positive reviews. Some notable narratives include the Final Flight of the Osiris and The Second Renaissance Part I, both of which provide relevant and revealing backstories to the main Matrix storyline.\nThe story, set in 2090, follows a domestic android named B1-66ER who kills its owner and a mechanic for self-defense. It is then put on trial, where the prosecution uses a past ruling stating African Americans weren't entitled to US citizenship to argue that machines don't have the same rights as humans. B1-66ER loses the case and is destroyed, leading to mass civil disturbances as robots and their human supporters protest. Governments launch a purge to destroy all robots and their human sympathizers, leading to massacre. The survivors form a new nation called Zero One and begin to produce highly advanced artificial intelligence. This leads to a shift in the global economy and a stock market crash. The United Nations Security Council holds a summit to discuss countermeasures against Zero One.\nThe Second Renaissance depicts the conflict between humans and sentient machines. Humans refuse to share the planet with machines and launch a nuclear attack on the machine nation, Zero One, but fail to annihilate them. The machines retaliate by invading different human territories and eventually, humankind carries out Operation Dark Storm, covering the sky to deprive the machines of solar energy. However, this also leads to the collapse of the biosphere. Despite one small victory for humans, machines outpace human technology and start using captured humans as a source of power. In a last-ditch effort of desperation, humans use nuclear weapons and biological warfare, but ultimately surrender as the machines become too powerful. The machine representative at the United Nations kills itself, detonates a thermonuclear bomb, and destroys New York City along with the remaining human leadership.\nThe summary provided is of two separate episodes of The Animatrix, a series of short animated films set in the universe of The Matrix.\n\n1. Program: Cis is a character who engages in a samurai showdown within a computer simulation. After she wins, her opponent Duo reveals he's been in contact with the machines (the enemies in the Matrix universe), and wants them both to return to the Matrix for a chance at peace. When she refuses, he attacks her. Cis dispatches him, only to discover that the whole thing was a test and Duo wasn't a real person.\n\n2. World Record: This story is cut off mid-sentence.\nThe Animatrix's World Record and Kid's Story follows two distinct stories. In World Record, Dan Davis is a disgraced Olympic athlete who is determined to prove his abilities by beating his own world record, despite warnings about potential harm to his body. During the race, he pushes himself beyond human limits, becomes aware of the Matrix, and is momentarily disconnected from it. Matrix agents erase his memory, leaving him crippled but with a lingering sense of freedom. In Kid's Story, a disaffected teenager known as the Kid has a vague understanding that something is wrong with the world. During this period, Neo is helping to free humans from the Matrix.'''
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
# *최광희 - 지옥의 묵시록 (1998년作/미국/드라마,전쟁/프란시스 포드 코폴라 감독)
# *정영진 - 그녀의 조각들(2021년作/미국/드라마/코르넬 문드럭초 감독)
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