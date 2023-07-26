from diginomard_toolkit.google_api import GoogleSearch, GoogleTranslateion, GoogleVoiceService

def test_GoogleSearch():
    googleSearch = GoogleSearch()
    q = '이케아 추천 top 5'
    # result = googleSearch.search(f'{q}', 10, 'snippet')
    # print(result)
    #result = googleSearch.search(f'justwatch {q}', 1)
    # print(result[0])
    # result = googleSearch.search(f'다음영화 {q}', 1)
    # print(result[0])
    result = googleSearch.searchImage(f'{q}', 1)
    print(result[0])
    # Example usage

def test_GoogleVoiceService():
    text_to_speak = '''
    죽기 전에 알아야 할 것들"의 특별한 코너에 오신 것을 환영합니다!
    오늘은 활기찬 한국음악의 세 가지 핵심 사실을 알아보겠습니다.
    '''
    GoogleVoiceService().textToSpeech(text_to_speak)

def test_GoogleTranslation():
    text_to_translate = '''
    {"topic": "How to Wake Up Early", "title": "3 Essential Tips for Waking Up Early", "uuid": "6b3dc93e", "intro": {"content": "Waking up early can be challenging, but with the right strategies, it becomes easier to start your day ahead of schedule. This article will provide you with three valuable insights on how to wake up early.", "images": ["images/How_to_Wake_Up_Early_Image_1.jpg"]}, "main": [{"heading": "1. Establish a Consistent Sleep Routine", "tag": "", "detail": {"content": "Maintaining a regular sleep schedule is key to waking up early. Try to go to bed and wake up at the same time every day, even on weekends. This helps regulate your body's internal clock, making it easier to fall asleep and wake up early.", "images": ["images/1._Establish_a_Consistent_Sleep_Routine_Image_1.jpg", "images/1._Establish_a_Consistent_Sleep_Routine_Image_2.jpg", "images/1._Establish_a_Consistent_Sleep_Routine_Image_3.jpg", "images/1._Establish_a_Consistent_Sleep_Routine_Image_4.jpg", "images/1._Establish_a_Consistent_Sleep_Routine_Image_5.jpg"]}}, {"heading": "2. Create a Morning Ritual", "tag": "", "detail": {"content": "Having a morning routine can make waking up early more enjoyable. Plan activities such as stretching, meditating, or reading a book that you find relaxing. This will give you something to look forward to and make waking up early feel more purposeful.", "images": ["images/2._Create_a_Morning_Ritual_Image_1.jpg", "images/2._Create_a_Morning_Ritual_Image_2.jpg", "images/2._Create_a_Morning_Ritual_Image_3.jpg", "images/2._Create_a_Morning_Ritual_Image_4.jpg", "images/2._Create_a_Morning_Ritual_Image_5.jpg"]}}, {"heading": "3. Optimize your Sleep Environment", "tag": "", "detail": {"content": "Make sure your bedroom is conducive to a good night's sleep. Keep the room dark, quiet, and at a cool temperature. Invest in comfortable bedding and ensure that your mattress and pillows are suitable for your preferences. Creating a relaxing sleep environment will help you wake up feeling refreshed and energized.", "images": ["images/3._Optimize_your_Sleep_Environment_Image_1.jpg", "images/3._Optimize_your_Sleep_Environment_Image_2.jpg", "images/3._Optimize_your_Sleep_Environment_Image_3.png", "images/3._Optimize_your_Sleep_Environment_Image_4.jpg", "images/3._Optimize_your_Sleep_Environment_Image_5.jpg"]}}], "conclusion": {"content": "By following these three tips, you can train your body to wake up early and start your day with energy and productivity. Remember, consistency is key, so be patient and give yourself time to adjust to the new routine. Once waking up early becomes a habit, you will experience the numerous benefits it brings to your overall well-being.", "images": ["images/How_to_Wake_Up_Early_Image_2.jpg", "images/How_to_Wake_Up_Early_Image_3.jpg", "images/How_to_Wake_Up_Early_Image_4.jpg", "images/How_to_Wake_Up_Early_Image_5.jpg"]}}
    '''
    translated = GoogleTranslateion().translate(text_to_translate, 'ko')
    print(translated)