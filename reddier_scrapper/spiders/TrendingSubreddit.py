from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy import http
from scrapy.shell import inspect_response  # for debugging
import re
import json
import time
import logging
from .Exportjson import Exportjson
logger = logging.getLogger(__name__)
from data_handler import TargetDataHandler 
class TrendingSubreddit(CrawlSpider):
    name = 'TrendingSubreddit'
    allowed_domains = ['reddit.com']
    def __init__(self, trends_filter="", top_time="day"):
        self.trends_filter=trends_filter
        if trends_filter=="top":
            self.url=f"https://www.reddit.com/r/subreddit/top/.json?t={top_time}"
        else:
            self.url = f'https://www.reddit.com/r/subreddit/{trends_filter}/.json'

    def start_requests(self):
        url = self.url 
        yield http.Request(url, callback=self.parse_page)
    
    def parse_page(self, response):
        data=json.loads(response.body_as_unicode())
        data={"trends": data}
        print(data)
        dh=TargetDataHandler(data=data, target_type="twitter_trends")
        dh.send_data()
        