from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy import http
from scrapy.shell import inspect_response 
import re
import json
from .Exportjson import Exportjson
from .data_handler import DataHandler

class Subreddit(CrawlSpider):
    name = 'Subreddit'
    allowed_domains = ['reddit.com']
    def __init__(self, username="", search=False, q="", CTR="", GTR=""):
        self.username=username
        self.search=search
        self.CTR=CTR
        self.GTR=GTR
        if search:
            print(q)
            self.url = f'https://www.reddit.com/search.json?q={q}'
        else: 
            self.url = f'https://www.reddit.com/r/{username}/.json'
        

    def start_requests(self):
        url = self.url 
        yield http.Request(url, callback=self.parse_page)
    
    def parse_page(self, response):
        data=json.loads(response.body_as_unicode())
        if self.search:
            exp=Exportjson("data", data)
            exp.make_dir()
            exp.dump_json()  
        else: 
            export=DataHandler(data=data , GTR=self.GTR, CTR=self.CTR)
            export.dump_json()   
        