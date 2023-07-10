from diginomard_toolkit.youtube_loader import YoutubeLoader

youtubeLoader = YoutubeLoader()
def test_YoutubeLoader():
    url = 'https://youtu.be/JD-b-Zl7yso'
    if url == '':
        url = input('Get URL : ')
    youtubeLoader.getYoutubeScript(url, 'en')
    #getYoutube(url)