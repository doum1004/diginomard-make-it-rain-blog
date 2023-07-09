from diginomard_toolkit.youtube_loader import YoutubeLoader

youtubeLoader = YoutubeLoader()
def test_YoutubeLoader():
    url = input('Get URL : ')
    if url == '':
        url = 'https://www.youtube.com/watch?v=3-hTgRO093Q'
    youtubeLoader.getYoutubeScript(url, 'en')
    #getYoutube(url)