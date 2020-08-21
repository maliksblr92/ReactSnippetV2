import scrapy
import itertools
from .data_handler import DataHandler
import datetime
class NDTVspider(scrapy.Spider):
    name="NDTV"
    def __init__(self, headlines=100, GTR="", CTR="", **kwargs):
        self.CTR=CTR
        self.GTR=GTR
        self.number_of_headlines=headlines
        self.start_urls=["https://www.ndtv.com"]
        
        super().__init__(**kwargs)
        self.t=str(datetime.datetime.now())
    def parse(self, response):
        heading=response.css(".item-title").xpath(".//text()").getall()
        link=response.css(".item-title").xpath(".//@href").getall()
        #link=link[:28]
        #heading=heading[:28]
        print(self.t)
       
        '''**********Filtering data************'''
        headlines=[]
        headlines_no=0
        for h, l in itertools.zip_longest(heading, link):    
            if headlines_no==self.number_of_headlines:
                break
            if h and l is not None:
                headline={
                          "Channel": "NDTV",
                          "HeadLine": h, 
                          "Description": "" ,
                          "Time":self.t,
                          "Link":l}
                headlines.append(headline)
                headlines_no=headlines_no+1
        top_headlines={"News": headlines}
        
        #Export Json Data
        export=DataHandler("NDTV",top_headlines,  self.GTR , self.CTR)
        export.dump_json()
