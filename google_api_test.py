from google_api import GoogleAPI

googleAPI = GoogleAPI()
q = '토니 에르만'
# result = googleAPI.search(f'justwatch {q}', 1)
# print(result[0])
# result = googleAPI.search(f'다음영화 {q}', 1)
# print(result[0])
result = googleAPI.searchImage(f'{q}', 1)
print(result[0])