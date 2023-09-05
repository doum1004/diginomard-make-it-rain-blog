import os
from diginomard_toolkit.wurg_api import WURG
from diginomard_toolkit.utils import ImageUtils

wurg = WURG()
# jsonFilePath = 'C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/blog/wurg/Thailand Cities/article.json'
# jsonData = Utils.readJsonFile(jsonFilePath)
# writeWURGs(getMainHeadings(jsonData))

#path = 'C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/blog/wurg_done/sa21-05b7b1d1/230718-180949__0__ko.json'
#path = path.replace('\\', '/')
# keyword = input('Give keyword : ')
#fillJsonData('__output/blog/wurg/Best Economy news website/230718-183436__0.json')
#searchAll('__output/blog/wurg')

#wurg.writeAllWURGUnderDir('__output/blog/wurg/previous')

keywords = ['Saving Money', 'speaking better', 'stable marriage', 'how to survive in desert island']
wurg.writeWURGs(keywords)

#WURG().runTranslation('__output/blog/wurg_prepare', 'ko')
#WURG().runMarkdown('__output/blog/wurg_prepare')
#runPostProcessUnder('__output/blog/wurg_production/', 'ko', False)


# # traverse all images under the dir
# for root, dirs, files in os.walk('__output/blog/wurg_prepare/'):
#     for file in files:
#         if file.endswith('.jpg') or file.endswith('.png'):
#             ImageUtils.convertItToWebPFile(os.path.join(root, file))
#             #print(os.path.join(root, file))