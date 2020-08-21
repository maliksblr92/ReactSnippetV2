from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy import http
from .data_handler import TargetDataHandler
from scrapy.shell import inspect_response  # for debugging
import re
import json
import time
import datetime
import logging
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

from datetime import datetime

logger = logging.getLogger(__name__)
class twitterTrends(CrawlSpider):
    name = 'twitterTrends'
    #allowed_domains = ['trends24.in']

    def __init__(self, country=None, request_id=None):
        self.country=country
        self.request_id=request_id
        if country !="world":
            self.url=f"https://trends24.in/{country}/"
        else:
            self.url = "https://trends24.in"
    def start_requests(self):
        print("Crawler is running.....................1", self.country)
        url = self.url 
        yield http.Request(url, callback=self.parse_page)
        
    def parse_page(self, response):
        print("Crawler is running....................2.")
        trend_cards=response.xpath("//div[@class='trend-card']")
        trends=[]
        tagcheck=""
        for card in trend_cards:
            timestamp=card.xpath(".//h5/@data-timestamp").get()
            time=str(datetime.fromtimestamp(float(timestamp)))
            trend_card_list=card.xpath(".//ol/li")
            print("card Length", len(trend_card_list))
            for crad_list in trend_card_list:
                tag=crad_list.xpath(".//a/text()").get()
                tweetcount=crad_list.xpath(".//span/text()").get()

                tagcheck=tag
                data={"date_time":time, "tag":tag, "tweet_count": tweetcount }
                trends.append(data)
            break
        dicdata={}
        if self.country is not None:
            dicdata={self.country:trends}
        else:
            dicdata={"worldwide": trends}
        data={"trends": dicdata}
        dh=TargetDataHandler(data=data, target_type="google_trends")
        dh.send_data()
        dh=TargetDataHandler(data=data, target_type="twitter_trends")
        dh.send_data()
