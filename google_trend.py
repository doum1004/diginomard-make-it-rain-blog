import pandas as pd
from pytrends.request import TrendReq


class GoogleTrend:
    COUNTRIES = ['south_korea', 'united_states', 'canada']
    pytrends = TrendReq()
    country = ''
    def __init__(self, country_index):
        self.country = self.COUNTRIES[country_index]
        pass

    def getTrandKeywords(self, q):
        trending_keywords = []
        if not q is None:
            self.pytrends.build_payload(kw_list=[q])
            related_queries = self.pytrends.related_queries()
            #pytrends.suggestions('chicken')
            if q in related_queries and 'top' in related_queries[q] and related_queries[q]['top'] is not None:
                trending_keywords = related_queries[q]['top']['query'].values.tolist()
        return trending_keywords

    def getTrends(self, nbTrends = 10):
        df = self.pytrends.trending_searches(pn=self.country)
        trends = df.head(nbTrends)[0]
        return trends
    
    def getTrendAndKeywords(self):
        trends = self.getTrends()
        trending_keywords = []
        for trend in trends:
            trending_keywords.append(self.getTrandKeywords(trend))
        return trends, trending_keywords