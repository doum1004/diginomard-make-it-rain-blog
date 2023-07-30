from diginomard_toolkit.wurg_api import WURG

# jsonFilePath = 'C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/blog/wurg/Thailand Cities/article.json'
# jsonData = Utils.readJsonFile(jsonFilePath)
# writeWURGs(getMainHeadings(jsonData))

#path = 'C:/Workspace/Personal/diginomard-make-it-rain-blog/__output/blog/wurg_done/sa21-05b7b1d1/230718-180949__0__ko.json'
#path = path.replace('\\', '/')
#keyword = input('Give keyword : ')
#fillJsonData('__output/blog/wurg/Best Economy news website/230718-183436__0.json')
#searchAll('__output/blog/wurg')

# keywords = ['Vietnam Cities']
# writeWURGs(keywords)

#WURG().runTranslation('__output/blog/wurg_production', 'ko')
WURG().runMarkdown('__output/blog/wurg_production')
#runPostProcessUnder('__output/blog/wurg_production/', 'ko', False)