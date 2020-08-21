import scrapy
import os
import json
from .data_handler import DataHandler
from .Exportjson import Exportjson
class AuthorSpider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    * This class inherits the 'Spider' class of Scrapy.
    * This crawler Extract the user information from Instagram
    '''
    name="author_spider"
    allowed_domains=["www.instagram.com"]

    def __init__(self, username='',request_id=None, smart_search_flag=True, CTR="", GTR="",  **kwargs):
        self.start_urls = [f"https://www.instagram.com/{username}?__a=1"]
        self.username=username
        self.request_id=request_id
        self.flag=smart_search_flag
        self.CTR=CTR
        self.GTR=GTR
        super().__init__(**kwargs)
        
    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        
        if data is not None and self.flag:
            export=DataHandler(username=self.username, data=data , GTR=self.GTR, CTR=self.CTR)
            export.dump_json()

        if not self.flag:
            print("Almost Done---------------")
            exp=Exportjson("sm", data, "insta")
            exp.make_dir()
            exp.dump_json()     
            



        