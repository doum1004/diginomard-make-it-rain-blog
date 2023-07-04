from youtube_loader import YoutubeLoader

youtubeLoader = YoutubeLoader()
url = input('Get URL : ')
if url == '':
    url = 'https://www.youtube.com/watch?v=3-hTgRO093Q'
youtubeLoader.getYoutubeScript(url, 'en')
#getYoutube(url)