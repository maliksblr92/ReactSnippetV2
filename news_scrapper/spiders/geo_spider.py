import scrapy
import itertools
from .data_handler import DataHandler
class Geospider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    * This crawler Extract Latest news headlines from Geo News Website
    '''
    name="geo_spider"

    def __init__(self, headlines=10, GTR="", CTR="", **kwargs):
        self.number_of_headlines=headlines
        self.CTR=CTR
        self.GTR=GTR
        self.start_urls=["https://www.geo.tv/"]
        print("--------------------->>>>>", headlines)
        super().__init__(**kwargs)
        
    def parse(self, response):
        heading=response.css(".heading").xpath(".//a/@title").getall()
        link=response.css(".heading").xpath(".//a/@href").getall()
        description=response.css(".m_except").xpath(".//p/text()").getall()
     
        '''**********Filtering data************'''
        headlines=[]
        headlines_no=0
        for h, d ,l in itertools.zip_longest(heading, description, link):    
            if headlines_no==self.number_of_headlines:
                break
            if h and d and l is not None:
                headline={"Channel": "GEO",
                        "HeadLine": h, 
                          "Description": d ,
                          "Time": " ",
                          "Link":l}
                headlines.append(headline)
                headlines_no=headlines_no+1
        top_headlines={"News": headlines}
        export=DataHandler("GEO",top_headlines, self.GTR , self.CTR)
        export.dump_json()
