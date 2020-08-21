import scrapy
import itertools
from .data_handler import DataHandler
class DawnSpider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    * This crawler Extract the Latest Stories from Dawn News website  
    * Extract data from this link https://www.dawn.com/latest-news 
    '''
    name="dawn_spider"

    def __init__(self, headlines=30, GTR="", CTR="", **kwargs):
        self.number_of_headlines=headlines
        self.CTR=CTR
        self.GTR=GTR
        self.start_urls=["https://www.dawn.com/latest-news"]
        super().__init__(**kwargs)

    def parse(self, response):
        story_title=response.css(".active").xpath(".//h2/a/text()").getall()
        story_description=response.css(".mt-0 *::text").getall()
        story_link=response.css(".active").xpath(".//h2/a/@href").getall()
        story_time=response.css(".timeago").xpath(".//@title").getall()
        
        '''**********Filtering data************'''
        
        stories=[]
        headlines_no=0
        for title, des,time, link in itertools.zip_longest(story_title, story_description,  story_time, story_link):    
            if headlines_no==self.number_of_headlines:
                break
            if title and des and time and link is not None:
                headline={
                    "channel": "Dawn",
                    "HeadLine": title, 
                          "Description": des ,
                          "Time":time,
                          "Link": link}
                stories.append(headline)
                headlines_no=headlines_no+1
        top_headlines={"News": stories}
                
        #Export Json Data
        export=DataHandler("DAWN",top_headlines, self.GTR, self.CTR)
        export.dump_json()
