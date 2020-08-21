from celery import Celery
import os
import json
from crawler_handler import NewsCrawlerHandler, TwitterCrawlerHandler, InstaCrawlerHandler, GenericCrawlerHandler, RedditCrawlerHandler
from youtube_scrapper.utils import setDriver
from youtube_scrapper.channels import Channel
from youtube_scrapper import Video
from youtube_scrapper.utils import setDriver
from youtube_scrapper.trending import getTrends
import google_scrapper.trends.trends as googleTrends
import time
from data_handler import DataHandler ,LinkedDataHandler
from Feeder import Feeder ,SearchEngine
import uuid
import data_handler
from lively.actionsHandler import Actions

from facebook_scrapper.crawlBook.crawlers import users, pages, groups, search
from facebook_scrapper.crawlBook.utilities.sessionHandler import DriverSession
from linkedin_scrapper import ProfileScraper, CompanyScraper
from selenium.webdriver.chrome.options import Options
import tldextract
import whois
import json
import socket
from ipwhois import IPWhois
from celery.signals import celeryd_init
import serpscrap
import json
import re
from linkedin import linked
#------------------------------------------------------- App init ----------------------------------------------------------
app =Celery("tasks", backend='amqp', broker='amqp://')
#app =Celery("tasks", backend="amqp://" ,broker='pyamqp://mca_broker:rapidev@192.168.18.27/v_mca_broker')
COKIE="AQEDAS6tx2ACzBj1AAABbxfJiXQAAAFw0nROGlEAQE_aYJ8eicWyTAl_HJZlFC2DBYmtLe38Mwuzk5peiD0qUtwCwXhbudahOnLSROoq-AFTbnFGDfpawiUfi9-T5xgOh7hQrP11iTDovnCU4DLRdJom"


#-----------------------------------------------------------> Target Internet Survey --------------------------------------




@app.task()
def target_survey(keywords):
    config = serpscrap.Config()
    config_new = {
    'cachedir': './KBM/cachedir',
    'dir_screenshot': "./KBM/screenshots",
    'clean_cache_after': 24,
    'database_name': './KBM/db',
    'do_caching': True,
    'num_pages_for_keyword': 10,
    'scrape_urls': True,
    'search_engines': ['google', ],
    'dir_screenshot': './KBM/screenshots',
    'google_search_url': 'https://www.google.com/search?',
    'executable_path': './chromedriver',
    'screenshot': False,
    'num_results_per_page': 10,
    'num_pages_for_keyword':2
    }
    config.apply(config_new)
    scrap = serpscrap.SerpScrap()
    scrap.init(config=config.get(), keywords=keywords)
    results = scrap.run()
    return results
    
#-----------------------------------------------------------> FaceBook Crawler <--------------------------------------------
driver=None
def check_driver():
    global driver
    if driver is None:
        driver = DriverSession(headless = True, login = True)
        return driver
    else: 
        return driver
@app.task()
def facebook_smart_search(username, entity_type):
    data = search.smartSearch(check_driver(), entity_type, username = username)
    print(data)
    #data = {"id": data["id"], "full_name":data["name"], "profile_image_url":data["media_directory"]}
    return data
@app.task()
def facebook_user(username, GTR, CTR):
    data = users.User(check_driver(), username = username).getCompleteProfile(downloadPictures = True, downloadVideos=True)
    dh=DataHandler(data={}, GTR=GTR, CTR=CTR)
    dh.dump_json(root="/data/fb/")


@app.task()
def facebook_page(username, GTR, CTR):
    data = pages.Page(check_driver(), username = username).getCompleteProfile(downloadPictures=True, downloadVideos=True)
    dh=DataHandler(data={}, GTR=GTR, CTR=CTR)
    dh.dump_json( root="/data/fb/")

@app.task()
def facebook_group(username, GTR, CTR):
    data = groups.Group(check_driver(), username = username).getCompleteProfile(downloadPictures = True)
    dh=DataHandler(data={}, GTR=GTR, CTR=CTR)
    dh.dump_json( root="/data/fb/")


@app.task()
def facebook_search(query):
    data = search.facebookSearch(check_driver(), query, "users")
    return data


#------------------------------------------------------------- Generic Crawler ------------------------------------------------


def web_info(doamin):
    domain = whois.query(doamin)
    json_data=json.dumps(domain.__dict__, indent=4, default=str)
    return json_data
def ip_info(domain_name):
    ip_add=socket.gethostbyname(domain_name)
    obj=IPWhois(ip_add)
    results = obj.lookup_whois()
    return results





@app.task()
def generic_crawler_taks(url="", GTR="", CTR="" , links=True,headings=True, paragraphs=True, pictures=False,videos=False, domain=False, ip=False):
     print(url)
     domain_=tldextract.extract(url)
     domain_=domain_.registered_domain

     handler=GenericCrawlerHandler(url=url, domain=domain_, links=links,headings=headings, paragraphs=paragraphs, pictures=pictures,videos=videos )
     handler.run_crawler()
     
     data={}
     if ip:
         ip_details=ip_info(domain_)
         data["ip_information"]=ip_details

     if domain:
         domain_details=web_info(domain_)
         data["domain_information"]=domain_details

     dh=DataHandler(data=data, GTR=GTR, CTR=CTR)
     dh.dump_json(root="/data/generic/")

#--------------------------------------------------------------- News -----------------------------------------------------------
@app.task()
def news_tasks(channel_name, number_of_headlines, GTR, CTR):
    handler=NewsCrawlerHandler(news_name=channel_name , number_of_headlines=number_of_headlines, GTR=GTR, CTR=CTR)
    handler.run_crawler()

@app.task()
def feed_tasks(GTR, CTR):
    data={}
    newsurls = {
        'Google News':'https://news.google.com/news/rss/?hl=en&amp;ned=us&amp;gl=US',
        'Yahoo News':'http://news.yahoo.com/rss/',
        "Aljazeera":'https://www.aljazeera.com/xml/rss/all.xml',
        "BBC World": 'http://feeds.bbci.co.uk/news/world/rss.xml',
        "BuzzFeed": 'https://www.buzzfeed.com/world.xml',
        "Blogs – E-International Relations":"https://www.e-ir.info/category/blogs/feed/",
        "Global Issues News Headlines":"http://www.globalissues.org/news/feed",
        "CNN":'http://rss.cnn.com/rss/edition_world.rss',
        "Washington Post":"http://feeds.washingtonpost.com/rss/world",
        "World news | The Guardian":"https://www.theguardian.com/world/rss", 
        "Times of India":'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms' 
     }
    
    for key,url in newsurls.items():
        fed=Feeder(url=url)
        data[key]=fed.getHeadlines()
    dh=DataHandler(data)
    dh.dump_json("feeds")



#----------------------------------------------------------------------- Twitter -----------------------------------------------
@app.task()
def twitter_user(username, GTR, CTR):
    handler=TwitterCrawlerHandler(user=username,  type_task="USER-C")
    handler.run_crawler()
    dh=data_handler.TweetDataHandler(username, CTR=CTR , GTR=GTR)
    dh.send_profile_data()

@app.task()
def twitter_smart_search(username):
    handler=TwitterCrawlerHandler(user=username,  type_task="USER-S")
    handler.run_crawler()
    with open(f"./data/user/{username}.json", 'r') as json_data:
        data = json.load(json_data)
        data={"id": data["id"], "full_name":data["Full_name"],"profile_image_url":data["profile_image_url"]}
        os.remove(f"./data/user/{username}.json")
        return data
#-------------------------------------------from Home--------------------------------------------
from twisearch import twitterSearch
@app.task()
def twitter_search(query):
    handler=TwitterCrawlerHandler(query=query,  type_task="SEARCH")
    handler.run_crawler()
    result=Tweet_data()
    return result

from os import listdir
from os.path import isfile, join
def Tweet_data():
    currentdir=os.getcwd()
    tweetfolder="./data/tweet"
    all_tweets={}
    num=0
    tweetfiles = [f for f in listdir(tweetfolder) if isfile(join(tweetfolder, f))]
    for x in tweetfiles:
        with open(join(tweetfolder, x), 'r') as json_data:
            data = json.load(json_data)
            all_tweets[num]=data
            num=num+1
            os.remove(join(tweetfolder, x))
    return all_tweets


@app.task()
def targetidentification(query):
    data = twitterSearch(query=query)
    return data
#--------------------------------------------------------------------- Trends -----------------------------------------------
@app.task()
def twitter_world_trends():
    handler=TwitterCrawlerHandler(query="world",  type_task="TRENDS")
    handler.run_crawler()

@app.task()
def twitter_country_trends(country):
    handler=TwitterCrawlerHandler(query=country, type_task="TRENDS")
    handler.run_crawler()

#------------------------------------------------------------------ LinkedIn -----------------------------------------------------

@app.task()
def linkedin_user(username, GTR, CTR):
    options = Options()
    options.add_argument('--headless')
    with ProfileScraper(cookie=COKIE) as scraper:
        profile = scraper.scrape(user=username)
        data=profile.to_dict()
        dh=LinkedDataHandler(data ,CTR=CTR, GTR=GTR)
        dh.dump_json()

@app.task()
def linkedin_company(username, GTR, CTR):
    options = Options()
    options.add_argument('--headless')
    
    with CompanyScraper(cookie=COKIE) as scraper:
        profile = scraper.scrape(username)
        data=profile.to_dict()
        dh=LinkedDataHandler(data ,CTR=CTR, GTR=GTR)
        dh.dump_json(company=True)

@app.task()
def linkedin_smart_search(username):
    options = Options()
    #options.add_argument('--headless')
    with ProfileScraper(cookie=COKIE, driver_options=options) as scraper:
        profile = scraper.scrape(user=username)
        data=profile.to_dict()
        print(data)
        dh=LinkedDataHandler(data )
        data=dh.send_image_ss()
        return data


@app.task()
def linkedin_search(query):
    print(query)




    driver = linked.setDriver(executable_path = "./chromedriver")
    data=linked.search(driver, query, entityType = "people", depth = 2)
    return data
#--------------------------------------------------------------------- Instagram ----------------------------------------------------
@app.task()
def insta_user(username, category, GTR, CTR):
    handler=InstaCrawlerHandler(username=username, CTR=CTR, GTR=GTR, category=category)
    handler.run_crawler()

@app.task()
def insta_smart_search(username):
    handler=InstaCrawlerHandler(username=username, category="AUTHOR", smart_flag=True)
    handler.run_crawler()
    path=os.getcwd()+"/data/insta/sm.json"
    try:
        with open(path, 'r') as f:
            data=json.load(f)
            data={"id": data["graphql"]["user"]["id"], "full_name":data["graphql"]["user"]["full_name"],"profile_image_url":data["graphql"]["user"]["profile_pic_url_hd"]}
            return data
    except Exception as e:
        print(e)
    finally:
        os.remove(path)
        
@app.task()
def instagram_search(query):
    handler=InstaCrawlerHandler(search_keyword=query )
    handler.run_crawler()
    path=os.getcwd()+f"/data/insta/{query}.json"
    try:
        with open(path, 'r') as f:
            data=json.load(f)
            return data
    except Exception as e:
        print(e)
    finally:
        os.remove(path)


#-----------------------------------------------------------------------Reddit--------------------------------------------------
#-----------------------------------------------------------------------Reddit--------------------------------------------------



from rScraper.rScraper import popularPosts
from rScraper.rScraper import subreddit
from rScraper.rScraper import user
from rScraper import rScraper

@app.task()
def reddit_trends(trends_filter, top_time):

    # handler=RedditCrawlerHandler(trends_filter=trends_filter, top_time=top_time, spider="TRENDS")
    # handler.run_crawler()
    data = popularPosts(category = trends_filter, timePeriod = "All Time")
    data={"trends": data}
    dh=data_handler.TargetDataHandler(data=data, target_type="reddit_trends")
    dh.send_data()


@app.task()
def reddit_subreddit(username, GTR, CTR):
    data = subreddit(subreddit = username, category = "hot")
    dh=DataHandler(data=data, GTR=GTR, CTR=CTR)
    dh.send_data()
    # handler=RedditCrawlerHandler(username=username, CTR=CTR, GTR=GTR, spider="SUBREDDIT")
    # handler.run_crawler()

@app.task()
def reddit_user(username, GTR, CTR):
    # handler=RedditCrawlerHandler(username=username, CTR=CTR, GTR=GTR, spider="USER")
    # handler.run_crawler()
    data= user(username = username, category = "top", timePeriod = "This Month")
    dh=DataHandler(data=data, GTR=GTR, CTR=CTR)
    dh.send_data()
#------------------------------------------------FROM hoME  

@app.task()
def User_reddit_search(username):
    # handler=RedditCrawlerHandler(username=username, spider="SUBREDDIT_SEARCH")
    # handler.run_crawler()
    # path=os.getcwd()+"/data/reddit/data.json"
    # try:
    #     with open(path, 'r') as f:
    #         data=json.load(f)
    #         return data
    # except Exception as e:
    #     print(e)
    # finally:
    #     os.remove(path)
    results = rScraper.search(username, entityType = "communities")
    return results
## other variant
## results = search("westworld", entityType = "posts")

@app.task()
def Subreddit_reddit_search(username):
    # handler=RedditCrawlerHandler(username=username, spider="USER_SEARCH")
    # handler.run_crawler()
    # path=os.getcwd()+"/data/reddit/data.json"
    # try:
    #     with open(path, 'r') as f:
    #         data=json.load(f)
    #         return data
    # except Exception as e:
    #     print(e)
    # finally:
    #     os.remove(path)
    results = rScraper.search(username, entityType = "posts")
    return results


#--------------------------------------------------------- youtube -------------------------------------------------------

@app.task()
def youtube_target(channel_id='', GTR="", CTR=""):
    # set driver and url
    driver = setDriver(executable_path = './chromedriver', headless = True, maximize = True)
    url = f"https://www.youtube.com/channel/{channel_id}"

    # start scraping
    data = Channel(driver, url = url).getCompleteProfile()
    for videos in data["videos"]["new"]:
        match=re.search(r"youtube\.com/.*v=([^&]*)", videos["link"])
        if match:
            id=match.group(1)
            video_data=Video.video_scrapper(driver,id)
            print(id)
            data[id]=video_data
    driver.close()
    dh=DataHandler(data=data, GTR=GTR, CTR=CTR)
    dh.send_data()

@app.task()
def youtube_trends():
    driver = setDriver(executable_path = './chromedriver', headless = True, maximize = True)
    data = getTrends(driver)
    driver.close()
    data={"trends": data}
    dh=data_handler.TargetDataHandler(data=data, target_type="youtube_trends")
    dh.send_data()
#-------------------------------------------------keybase management system----------------------------------------------
@app.task()
def keybase_system(payload):
    keywords=payload["keywords"]
    print(keywords)
    CTR=payload["CTR"]
    GTR=payload["GTR"]

    config = serpscrap.Config()
    config_new = {
    'cachedir': './KBM/cachedir',
    'dir_screenshot': "./KBM/screenshots",
    'clean_cache_after': 24,
    'database_name': './KBM/db',
    'do_caching': True,
    'num_pages_for_keyword': 10,
    'scrape_urls': True,
    'search_engines': ['google', ],
    'dir_screenshot': './KBM/screenshots',
    'google_search_url': 'https://www.google.com/search?',
    'executable_path': './chromedriver',
    'screenshot': False,
    'num_results_per_page': 10,
    'num_pages_for_keyword':2
    }
    config.apply(config_new)
    scrap = serpscrap.SerpScrap()
    scrap.init(config=config.get(), keywords=keywords)
    results = scrap.run()
    data={"data":results}
    
    dh=DataHandler(data=data, GTR=GTR, CTR=CTR)
    dh.send_data()

@app.task()
def google_trends_daily(country):

    chromeDirectory = "./chromedriver"

    driver = googleTrends.setDriver(chromeDirectory, headless = True)
    # for daily
    dailytrends=googleTrends.getDailySearchTrends(driver, country = country)
    data={"trends": dailytrends}
    driver.close()
    dh=data_handler.TargetDataHandler(data=data, target_type="google_trends")
    dh.send_data()

@app.task()
def google_trends_realtime(country):

    chromeDirectory = "./chromedriver"
    driver = googleTrends.setDriver(chromeDirectory, headless = True)
    # for realtime results
    trends=googleTrends.getRealtimeTrends(driver, country = country, category = "all")
    driver.close()
    data={"trends": trends}
    dh=data_handler.TargetDataHandler(data=data, target_type="google_trends")
    dh.send_data()

#--------------------------------------------------------------------- Twitter Searching Tools --------------------------------



#----------------------------------------------------------------- Avatar API End point ------------------------------------

#---------------------------------------------------------------- Post ---------------------------------------------------

@app.task()
def avtar_post(data):
    loginCredentials={
        "email":data["email"],
        "password":data["password"]}

    act = Actions(site = data["social_media"],loginCredentials=loginCredentials, submit = False)
    act.post(text = data["text"], media = data["media"])

#---------------------------------------------------------------- comment ---------------------------------------------------
@app.task()
def avtar_comment(data):
    loginCredentials={
        "email":data["email"],
        "password":data["password"]}
    
    print(data)

    act = Actions(site = data["social_media"], loginCredentials=loginCredentials, submit = False)
    act.comment(post_link = data["target_post"], text = data["text"])

#---------------------------------------------------------------- Reaction ---------------------------------------------------

@app.task()
def avtar_Reaction(data):
    loginCredentials={data["social_media"]:{
        "email":data["email"],
        "password":data["password"]}}
    act = Actions(site = data["social_media"], loginCredentials=loginCredentials, submit = False)
    act.react(post_link= data["target_post"], reaction = data["reaction"])

#---------------------------------------------------------------- share ---------------------------------------------------
@app.task()
def avatar_share(data):
    loginCredentials={data["social_media"]:{
        "email":data["email"],
        "password":data["password"]}}
    act = Actions(site = data["social_media"], loginCredentials=loginCredentials, submit = False)
    act.share(post_link= data["target_post"], sub_text =data["text"])

#-------------------------------------------------------- tools ---------------------------------------------------------------

from di_ekaf.fake import generate_fake_id
from acad_patents.academics_and_patents import scholar
from darker.dark_search import DarkSearch
from acad_patents.academics_and_patents import patents
from ip_logger.logger import IpLogger
from res.image_search import reverse_search

@app.task()
def fake_person_generator( nationality, gender, age):
    result = generate_fake_id(name_set = nationality, country = nationality, gender = gender, age = age)
    return result

@app.task()
def darkweb(query=""):
    results = DarkSearch(timeout = 8).searchDarkWeb(query)
    return results

@app.task()
def scholar_(query=""):
    results = scholar(query)
    return results


@app.task()
def patents_(query=""):
    results = patents(query)
    return results


import requests
@app.task()
def ip_shortend_url(url=""):
    #log = IpLogger(headless = True, timeout = 10) 
    #result=log.create_payload(url)
    #log.log_driver.close()
    result=requests.post("http://majidahmed.pythonanywhere.com/create", data = {'url': url})
    return result.json()


@app.task()
def ip_tracking(code="", start_date="", end_date="", GTR="", CTR=""):
    #log = IpLogger(headless = True, timeout = 10)
    #data=log.track_code(code = code, start_date = start_date, end_date = end_date)
    #log.log_driver.close()
    result=requests.get(f"http://majidahmed.pythonanywhere.com/track/{code}")
    return result.json()


@app.task()
def image_rever_lookup(url=""):
    results = reverse_search(url = url)
    return results
