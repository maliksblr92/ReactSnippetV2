import scrapy
import itertools
from .data_handler import DataHandler
import datetime
class ZEEspider(scrapy.Spider):
    name="ZEE"
    def __init__(self, headlines=10, GTR="", CTR="", **kwargs):
        self.CTR=CTR
        self.GTR=GTR
        self.number_of_headlines=headlines
        self.start_urls=["https://zeenews.india.com/latest-news"]
        super().__init__(**kwargs)

    def parse(self, response):
        
        heading=response.css(".sec-con-box").xpath(".//h3/a/text()").getall()
        description=response.css(".sec-con-box").xpath(".//p/text()").getall()
        link= response.css(".sec-con-box").xpath(".//h3/a/@href").getall()
        time= response.css(".sec-con-box").xpath(".//span/text()").getall()
        '''**********Filtering data************'''
        headlines=[]
        headlines_no=0
        for h, l, d, t  in itertools.zip_longest(heading, link, description, time):    
            if headlines_no==self.number_of_headlines:
                break
            if h and l is not None:
                headline={"channel":"ZEE",
                        "HeadLine": h, 
                        "Description": d,
                        "Time":t,
                        "Link":"https://zeenews.india.com"+str(l)}
                headlines.append(headline)
                headlines_no=headlines_no+1
        top_headlines={"News": headlines}
     
        #Export Json Data
        export=DataHandler("ZEE",top_headlines,  self.GTR , self.CTR)
        export.dump_json()
