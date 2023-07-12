from diginomard_toolkit.google_api import GoogleSearch, GoogleVoiceService

def test_GoogleSearch():
    googleSearch = GoogleSearch()
    q = '이케아 추천 top 5'
    result = googleSearch.search(f'{q}', 10, 'snippet')
    print(result)
    #result = googleSearch.search(f'justwatch {q}', 1)
    # print(result[0])
    # result = googleSearch.search(f'다음영화 {q}', 1)
    # print(result[0])
    # result = googleSearch.searchImage(f'{q}', 1)
    # print(result[0])
    # Example usage

def test_GoogleVoiceService():
    text_to_speak = '''
    죽기 전에 알아야 할 것들"의 특별한 코너에 오신 것을 환영합니다!
    오늘은 활기찬 한국음악의 세 가지 핵심 사실을 알아보겠습니다.
    '''
    GoogleVoiceService().textToSpeech(text_to_speak)

test_GoogleVoiceService()