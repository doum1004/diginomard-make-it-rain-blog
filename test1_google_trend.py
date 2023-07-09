from diginomard_toolkit.google_trend import GoogleTrend

googleTrend = GoogleTrend(0)
trends, keywords = googleTrend.getTrendAndKeywords()
print(trends)
print(keywords)