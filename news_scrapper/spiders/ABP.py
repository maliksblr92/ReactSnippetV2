import scrapy
import itertools
from .data_handler import DataHandler
import datetime
class ABPspider(scrapy.Spider):
    name="ABP"
    def __init__(self, headlines=10, GTR="", CTR="", **kwargs):
        self.number_of_headlines=headlines
        self.CTR=CTR
        self.GTR=GTR
        self.start_urls=["https://news.abplive.com/latest-news"]
        super().__init__(**kwargs)

    def parse(self, response):
        heading1=response.css(".other_news").xpath(".//text()").getall()
        heading2=response.css(".news_content").xpath(".//text()").getall()
        heading=heading1+heading2
        l1=response.css(".other_news").xpath(".//@href").getall()
        l2=response.css(".news_content").xpath(".//@href").getall()
        link=l1+l2
        '''**********Filtering data************'''
        headlines=[]
        headlines_no=0
        for h, l  in itertools.zip_longest(heading, link ):    
            if headlines_no==self.number_of_headlines:
                break
            if headlines_no%2==0:
                if h and l is not None:
                    headline={"Channel":"ABP",
                            "HeadLine": h, 
                            "Description": "" ,
                            "Time":str(datetime.datetime.now()),
                            "Link":l}
                    headlines.append(headline)
            headlines_no=headlines_no+1
        top_headlines={"News": headlines}
        
        export=DataHandler("ABP",top_headlines, self.GTR, self.CTR )
        export.dump_json()
