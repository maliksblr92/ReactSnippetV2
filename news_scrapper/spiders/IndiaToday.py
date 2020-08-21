import scrapy
import itertools
import datetime
from .data_handler import DataHandler
class IndiaTodayspider(scrapy.Spider): 
    name="IndiaToday"
    def __init__(self, headlines=100, GTR="",CTR="", **kwargs):
        self.CTR=CTR
        self.GTR=GTR
        self.number_of_headlines=headlines
        self.t=str(datetime.datetime.now())
        self.start_urls=["https://www.indiatoday.in/news.html"]
        super().__init__(**kwargs)

    def parse(self, response):
        #heading=response.css("a").xpath(".//text()").getall()
        #link=response.css("a").xpath(".//@href").getall()
        top_headlines=response.css(".news-page-feature").xpath(".//a/@title").getall()
        top_headlines_link=response.css(".news-page-feature").xpath(".//a/@href").getall()
        india=response.css(".section-ordering").xpath(".//a/text()").getall()
        india_link=response.css(".section-ordering").xpath(".//a/@href").getall()
        heading=top_headlines+india
        link=top_headlines_link+india_link

        '''**********Filtering data************'''
        headlines=[]
        headlines_no=0
        for h, l in itertools.zip_longest(heading, link ):    
            if headlines_no==self.number_of_headlines:
                break
            if h and l is not None:
                headline={
                        "Channel": "India Today",
                         "HeadLine": h, 
                          "Description": "" ,
                          "Time":self.t,
                          "Link":"https://www.indiatoday.in"+l}
                headlines.append(headline)
                headlines_no=headlines_no+1
        top_headlines={"News": headlines}
        
        #Export Json Data
        export=DataHandler("INDIATODAY",top_headlines,  self.GTR , self.CTR)
        export.dump_json()
