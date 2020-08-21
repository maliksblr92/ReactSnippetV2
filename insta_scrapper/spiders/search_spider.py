import scrapy
import os
import json
from .Exportjson import Exportjson
class SearchSpider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    * This class inherits the 'Spider' class of Scrapy.
    * This Crawler Extract the data of keyword and save into the keyword.json in SearchResults Folder
    '''
   
    name="search_spider"
    allowed_domains=["www.instagram.com"]

    def __init__(self, search='', **kwargs):
        self.start_urls = [f"https://www.instagram.com/web/search/topsearch/?context=blended&query={search}"]
        self.json_file_name=search
        super().__init__(**kwargs)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        if data is not None:
            file_n=Exportjson(self.json_file_name, data, "insta")
            file_n.make_dir()
            file_n.dump_json()
        