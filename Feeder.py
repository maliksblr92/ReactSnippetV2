import feedparser
import re
class Feeder:
    def __init__(self, url):
        self.rss_url =url 
    def parseRSS(self, rss_url ):
        return feedparser.parse( rss_url ) 
    def getHeadlines(self ):
        data=[]
        feed = self.parseRSS( self.rss_url )
        for newsitem in feed['items']:
            cleanr = re.compile('<.*?>')
            desc = re.sub(cleanr, '', newsitem['description'])
            
            feeds={"Title":newsitem['title'],
            "Description":desc,
            "Link": newsitem["link"]}
            data.append(feeds)  
        return data
        
class SearchEngine:
    def __init__(self, url):
        self.rss_url =url 
    def parseRSS(self, rss_url ):
        return feedparser.parse( rss_url ) 
    def getHeadlines(self ):
        data=[]
        feed = self.parseRSS( self.rss_url )
        for newsitem in feed['items']:
            cleanr = re.compile('<.*?>')
            desc = re.sub(cleanr, '', newsitem['description'])
            
            feeds={"Title":newsitem['title'],
            "Description":desc.replace("&nbsp;", " "),
            "Link": newsitem["link"],
            "Published_Date":feed["feed"]["updated"],
            "language":feed["feed"]["language"],
            "source":newsitem["source"] }
            data.append(feeds)  
        return data