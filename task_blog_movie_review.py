import os
import time
from diginomard_toolkit.google_api import GoogleSearch
from diginomard_toolkit.google_trend import GoogleTrend
from diginomard_toolkit.news import News
from diginomard_toolkit.ai_openai import OpenAI
from diginomard_toolkit.ai_openai_embed import OpenAIEmbedding
from diginomard_toolkit.prompts import PromptGenerator
from diginomard_toolkit.utils import Preference, SaveUtils, Utils, FileUtils
from diginomard_toolkit.wiki import Wiki

googleSearch = GoogleSearch()
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

def getMovieBlogPost(text, keyword):
    print(f'len({len(text)}) {text[:50]}')
    if len(text) < 100:
        return
    input('Continue ? ')
    openai = OpenAI()
    while len(text) > Preference.maxToken:
        text = openai.getSummary(text)
    prompts = PromptGenerator.getMovieBlogPostPrompts(text)
    resultEng = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
    print(resultEng)
    
    prompts = PromptGenerator.getTranslatePrompts(resultEng)
    resultKor = openai.chatMessageContents(prompts[0], prompts[1], prompts[2], keyword = keyword)
    print(resultKor)

    # add additional info
    links = "\n\n\n\n"
    images = googleSearch.searchImage(f'{q}', 5)
    links += "\n".join(images)
    link = googleSearch.search(f'justwatch {q}', 1)
    links += "\n" + link[0]
    resultEng += links
    resultKor += links

    saveUtils = SaveUtils('__output/blog/movie')
    saveUtils.saveData(q, resultEng)
    saveUtils.saveData(q, resultKor)
    
    return resultKor


q = '용쟁호투'
text = searchWiki(q)
post = getMovieBlogPost(text, q)

# *정영진 - 마다가스카의 펭귄 (2014년作/미국/애니메이션/에릭 다넬, 시몬 J.스미스 감독)
# *장규성 – 리바운드 (2023년作/한국/드라마/장항준 감독) 
# *라이너 – 슬픔의 삼각형 (2023년作/스웨덴,미국/코미디/루벤 외스틀룬드 감독) 
# *거의없다 - 맥베스의 비극 (2022년作/미국/드라마/조엘 코엔 감독)
# *최광희 - 더 폴 : 오디어스와 환상의 문 (2008년作/인도,영국,미국/모험/타셈 싱 감독)
# *전찬일 – 구름에 가린 별 (1960년作/인도/드라마/리트윅 가탁 감독) 
# *라이너 – 신 고질라 (2016년作/일본/드라마,액션,SF/안노 히데아키, 히구치 신지 감독) 
# *거의없다 - 앙코르(Walk the Line) (2005년作/미국/로맨스,멜로,드라마/제임스 맨골드 감독)
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