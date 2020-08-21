import scrapy
import itertools
from .data_handler import DataHandler
class BBCspider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    * This crawler Extract Latest news headlines from BBC News Website
    * The Home page of BBC news containt max 12-15 latest stories
    * This Crawler Extract max 10  latest Headline wiht Description and Time
    '''
    
    name="bbc_spider"
    def __init__(self, headlines=10, GTR="", CTR="", **kwargs):
        if headlines >10:
            headlines=10
        self.number_of_headlines=headlines
        self.CTR=CTR
        self.GTR=GTR
        self.start_urls=["https://www.bbc.com/news"]
        super().__init__(**kwargs)

    def parse(self, response):
        heading=response.css(".nw-c-top-stories--international").xpath(".//h3/text()").getall()
        description=response.css(".nw-c-top-stories--international").xpath(".//p/text()").getall()
        time=response.css(".nw-c-top-stories--international").xpath(".//time/@datetime").getall()
        
        '''**********Filtering data************'''

        headlines=[]
        headlines_no=0
        for h, d ,t in itertools.zip_longest(heading, description, time):    
            if headlines_no==self.number_of_headlines:
                break
            if h and d and t is not None:
                headline={"Channel":"BBC",
                        "HeadLine": h, 
                          "Description": d ,
                          "Time":t,
                          "Link":" "}
                headlines.append(headline)
                headlines_no=headlines_no+1
        top_headlines={"News": headlines}
        
        #Export Json Data
        export=DataHandler("BBC",top_headlines, self.GTR , self.CTR)
        export.dump_json()
