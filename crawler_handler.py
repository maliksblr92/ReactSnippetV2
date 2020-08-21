from scrapy.utils.log import configure_logging
from news_scrapper.spiders import  dawn_scrapper, ary_spider, geo_spider, bbc_spider , ABP, NDTV, IndiaToday ,ZEE
from insta_scrapper.spiders import author_spider,post_spider,search_spider
from TweetScraper.spiders import TweetCrawler ,user , trendings
from generic_scrapper import settings as generic_crawler_settings
from generic_scrapper.spiders import generic_spider
from reddier_scrapper.spiders import TrendingSubreddit, Users, Subreddit

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from TweetScraper import settings as twitter_crawler_settings
from reddier_scrapper import settings as reddit_crawler_settings
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from billiard import Process, Queue
from twisted.internet import reactor

import json
import os

class NewsCrawlerHandler:
    def __init__(self, news_name, number_of_headlines, GTR, CTR):
        self.news_name=news_name
        self.number=number_of_headlines
        self.CTR=CTR
        self.GTR=GTR

    def run_crawler(self):
        def que(q):
            settings_=Settings()
            settings_.setmodule(reddit_crawler_settings)
            try:
                process =CrawlerRunner()
                if self.news_name=="DAWN":
                    d=process.crawl(dawn_scrapper.DawnSpider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                elif self.news_name=="BBC":
                    d=process.crawl(bbc_spider.BBCspider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                elif self.news_name=="GEO":
                    d=process.crawl(geo_spider.Geospider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                elif self.news_name=="ARY":
                    d=process.crawl(ary_spider.ArySpider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                elif self.news_name=="ABP":
                    d=process.crawl(ABP.ABPspider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                elif self.news_name=="NDTV":
                    d=process.crawl(NDTV.NDTVspider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                elif self.news_name=="ZEE":
                    d=process.crawl(ZEE.ZEEspider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                elif self.news_name=="INDIATODAY":
                    d=process.crawl(IndiaToday.IndiaTodayspider, headlines=self.number, GTR=self.GTR , CTR=self.CTR)
                else:
                    raise Exception("The Input News Name Crawler is Not in our List.. try Dawn")
                d.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None) 
            except Exception as e:
                q.put(e)    
        q=Queue()
        p=Process(target=que, args=(q,))
        p.start()
        result=q.get()
        p.join()
        if result is not None:
            raise result
        
class TwitterCrawlerHandler:
    def __init__(self, user=None, query="", top_tweet=False, request_id=None, type_task=""):
        self.user=user
        self.query=query
        self.top_tweet=top_tweet
        self.request_id=request_id
        self.Task_type=type_task

    def run_crawler(self):
        def que(q):
            settings_=Settings()
            settings_.setmodule(twitter_crawler_settings)
            try:
                runner =CrawlerRunner(settings_)
                if self.Task_type=="USER-C":
                    d=runner.crawl(user.TwitterUserScraper, profile=self.user , request_id=self.request_id)
                    d=runner.crawl(TweetCrawler.TweetScraper, query="from:"+self.user)

                elif self.Task_type=="USER-S":
                    d=runner.crawl(user.TwitterUserScraper, profile=self.user , request_id=self.request_id)
                elif self.Task_type=="SEARCH":
                    d=runner.crawl(TweetCrawler.TweetScraper, query=self.query)
            
                elif self.Task_type=="TRENDS":
                    d=runner.crawl(trendings.twitterTrends, country=self.query)
                
                
                d.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None) 
            except Exception as e:
                q.put(e)    
        q=Queue()
        p=Process(target=que, args=(q,))
        p.start()
        result=q.get()
        p.join()
        if result is not None:
            raise result


    
class InstaCrawlerHandler:
    def __init__(self, username=None, search_keyword=None, category=None,   smart_flag=False, CTR="", GTR=""):
        self.username=username
        self.search_keyword=search_keyword
        self.category=category
        self.CTR=CTR
        self.GTR=GTR
        self.smart_search_flag=smart_flag
    def run_crawler(self):  
        def que(q):
            try:
                runner = CrawlerRunner(get_project_settings())
                if self.username is not None:
                    if self.smart_search_flag:
                        d=runner.crawl(author_spider.AuthorSpider, username=self.username, smart_search_flag=False)
                    elif self.category=="AUTHOR":
                        d=runner.crawl(author_spider.AuthorSpider, username=self.username, GTR=self.GTR, CTR=self.CTR)
                    elif self.category=="POST":
                        d=runner.crawl(post_spider.PostSpider,username=self.username)
                elif self.search_keyword is not None:
                    d=runner.crawl(search_spider.SearchSpider, search=self.search_keyword)
                else:
                    raise Exception("The Input to Insta Crawler is Not Correct.. ", self.search_keyword)
                d.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None)
            except Exception as e:
                q.put(e)    
        q=Queue()
        p=Process(target=que, args=(q,))
        p.start()
        result=q.get()
        p.join()
        if result is not None:
            raise result




class GenericCrawlerHandler:
    def __init__(self, url, domain,links=True, headings=True, paragraphs=True, pictures=False,videos=False):
        self.url=url
        self.domain=domain
        self.links=links
        self.headings=headings
        self.paragraphs=paragraphs
        self.pictures=pictures
        self.videos=videos
    def run_crawler(self):
        def que(q):
            settings_=Settings()
            settings_.setmodule(generic_crawler_settings)
            try:
                print(self.url, self.domain)
                runner =CrawlerRunner(settings_)
                d=runner.crawl(generic_spider.GenericSpider, url=self.url, domain=self.domain, links=self.links,
                 headings=self.headings, paragraphs=self.paragraphs, pictures=self.pictures,videos=self.videos)
                d.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None) 
            except Exception as e:
                q.put(e)    
        q=Queue()
        p=Process(target=que, args=(q,))
        p.start()
        result=q.get()
        p.join()
        if result is not None:
            raise result
        return "Done"



class RedditCrawlerHandler:
    def __init__(self, username="", trends_filter="", top_time="", CTR="", GTR="", spider=""):
        self.username=username
        self.trends_filter=trends_filter
        self.top_time=top_time
        self.GTR=GTR
        self.CTR=CTR
        self.spider=spider

    def run_crawler(self):
        def que(q):
            settings_=Settings()
            settings_.setmodule(reddit_crawler_settings)
            try:
                runner =CrawlerRunner()
                if self.spider=="TRENDS":
                    d=runner.crawl(TrendingSubreddit.TrendingSubreddit ,trends_filter=self.trends_filter, top_time=self.top_time)
                elif self.spider=="SUBREDDIT":
                    d=runner.crawl(Subreddit.Subreddit , username=self.username,  GTR=self.GTR, CTR=self.CTR)
                elif self.spider=="USER":
                    d=runner.crawl(Users.Users , username=self.username ,GTR=self.GTR, CTR=self.CTR)
                elif self.spider=="SUBREDDIT_SEARCH":
                    d=runner.crawl(Subreddit.Subreddit , q=self.username, search=True)
                elif self.spider=="USER_SEARCH":
                    d=runner.crawl(Users.Users , username=self.username, search=True)

                d.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None) 
            except Exception as e:
                q.put(e)    
        q=Queue()
        p=Process(target=que, args=(q,))
        p.start()
        result=q.get()
        p.join()
        if result is not None:
            raise result
