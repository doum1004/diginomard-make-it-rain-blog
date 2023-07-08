from google_api import GoogleAPI

googleAPI = GoogleAPI()
result = googleAPI.search('wikipedia 브래드피트')
print(result)
result = googleAPI.searchImage('브래드피트')
print(result)
result = googleAPI.searchImage2('브래드피트')
print(result)