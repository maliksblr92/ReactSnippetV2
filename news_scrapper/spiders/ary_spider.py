import scrapy
import itertools
from .data_handler import DataHandler
class ArySpider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    * This crawler Extract the Latest Stories from ARY News
    *  website https://arynews.tv/en/latest-news/   
    '''
    name="ary_spider"
    def __init__(self, headlines=30, GTR="", CTR="", **kwargs):
        self.CTR=CTR
        self.GTR=GTR
        self.number_of_headlines=headlines
        self.start_urls=["https://arynews.tv/en/latest-news/"]
        super().__init__(**kwargs)

    def parse(self, response):
        title=response.css(".clearfix").xpath(".//h2/a/text()").getall()
        link=response.css(".clearfix").xpath(".//h2/a/@href").getall()
        
        '''**********Filtering data************'''
        stories=[]
        headlines_no=0
        for t, l in itertools.zip_longest(title,link):    
            if headlines_no==self.number_of_headlines:
                break
            if t and l is not None:
                headline={"channel": "ARY",
                    "HeadLine": t.replace("\n", " "),
                        "Description":" ",
                        "Time":" ",
                        "Link": l}
                stories.append(headline)
                headlines_no=headlines_no+1
        top_headlines={"News": stories}
        #Export Json Data
        export=DataHandler("ARY",top_headlines,  GTR=self.GTR , CTR=self.CTR)
        export.dump_json()

   
