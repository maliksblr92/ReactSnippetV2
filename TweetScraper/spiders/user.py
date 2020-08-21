from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy import http
from scrapy.shell import inspect_response  # for debugging
import re
import json
import time
import logging
from .data_handler import DataHandler
logger = logging.getLogger(__name__)
class TwitterUserScraper(CrawlSpider):
    name = 'TwitterUserScraper'
    allowed_domains = ['twitter.com']

    def __init__(self, profile="", request_id=""):
        self.request_id=request_id
        self.user=profile
        self.url = f"https://twitter.com/{profile}"
    def start_requests(self):
        url = self.url 
        yield http.Request(url, callback=self.parse_page)
    def parse_page(self, response):
        Id=response.css(".stream-item-header").xpath("./a/@data-user-id").get()
        profileimage = response.css(".ProfileAvatar-image").attrib['src']
        full_name=response.css(".ProfileHeaderCard-nameLink").xpath("./text()").get()
        
        tweets=response.css(".ProfileNav-item--tweets").xpath("./a/@title").get()
        Following=response.css(".ProfileNav-item--following").xpath("./a/@title").get()
        followers=response.css(".ProfileNav-item--followers").xpath("./a/@title").get()
        Likes=response.css(".ProfileNav-item--favorites").xpath("./a/@title").get()

        moments=response.css(".ProfileNav-item--moments").xpath("./a/@title").get()
        lists=response.css(".ProfileNav-item--lists").xpath("./a/@title").get()

        bio=response.css(".ProfileHeaderCard-bio").xpath("./text()").get()
        location=response.css(".ProfileHeaderCard-locationText").xpath("./text()").get()
        website=response.css(".ProfileHeaderCard-urlText").xpath("./a/@title").get()
        join_date=response.css(".ProfileHeaderCard-joinDateText").xpath("./text()").get()
        data={"id":Id,
            "profile_image_url":profileimage,
            "Full_name":full_name,
            "bio_data":bio,
            "location":location,
            "website":website,
            "join_date":join_date,
            "Tweets":tweets,
            "Following":Following,
            "Followers":followers,
            "Likes":Likes,
            "Lists": lists,
            "moments": moments}

        with open(f'./data/user/{self.user}.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
