import flask
from flask import request, jsonify
from crawler_handler import TwitterCrawlerHandler
from youtube_scrapper.search import smartSearch, searchChannel
import os
import task_queue 
import speedtest
from flask import request, Response
import time
from publisher import Rabbit_Publisher
from Feeder import Feeder,SearchEngine
import whois
import json
from ipwhois import IPWhois
import socket
from cryptography.fernet import Fernet
import datetime
import base64
#--------------------------------------------------------------------- App init ------------------------------------------------------------
MC_KEY=""
CELERY_APP=task_queue.app
app=flask.Flask(__name__)
app.config["DEBUG"]=True
app.secret_key="key_key_key"
HOST="127.0.0.1"
PORT=6000

#--------------------------------------------------------------------- Decorator --------------------------------------------------------------
def token_auth(fun):
    def wrapper_function(*args, **kwargs):
        global MC_KEY
        try:
            token=request.form["token"].encode('ascii')
            ciper_suit=Fernet(MC_KEY)
            key=key=ciper_suit.decrypt(token).decode()
            
            print(key)
            if key==str(datetime.date.today()):
                return fun()
            else:
                return {"Unauthorized client": 401}
        except Exception:
            return {"invalid authenticity token": 402}
    return wrapper_function

#------------------------------------------------------------------ important functions --------------------------------------------------------
def internet_connection():
    servers = []
    threads = None
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads)
    s.results.share()
    results_dict = s.results.dict()
    return results_dict
def web_info(domain):
    domain = whois.query(domain)
    json_data=json.dumps(domain.__dict__, indent=4, default=str)
    print(json_data)
    return json_data
def ip_info(domain_name):
    ip_add=socket.gethostbyname(domain_name)
    obj=IPWhois(ip_add)
    results = obj.lookup_whois()
    return results
#-------------------------------------------------------------- REST API EndPoints ----------------------------------------------#

#-------------------------------------------------------------- Crawler status ------------------------------------------------------
@app.route("/ip", methods=["POST"])
def get_crawler_ip():
    return jsonify({"IP":HOST, "port":PORT})


@app.route("/status", methods=["POST"])
def get_crawler_status():
    global MC_KEY, CELERY_APP
    if MC_KEY=="":
        MC_KEY=Fernet.generate_key()
        print("Connection pooling")
    active_jobs=CELERY_APP.control.inspect().active()
    return jsonify({"active_workers":active_jobs, "mc_key":MC_KEY.decode('ascii')})

#-----------------------------------------------------------> Domain information ---------------------------------------------------
@app.route("/domain", methods=["GET"])
def webinfo_api():
    domain=request.form.get("domain")
    result = web_info(domain)
    return jsonify({"data": result})

#------------------------------------------------------------ IP information --------------------------------------------------
@app.route("/ipinfo", methods=["POST"])
def ipinfo_api():  
    domain=request.form.get("domain")
    result = ip_info(domain)
    return jsonify({"data": result})

#-------------------------------------------------------> Internet Connection information----------------------------------------
@app.route("/internet", methods=["POST"])
def internet_api():  
    result = internet_connection()
    return jsonify({"internet": result})

#----------------------------------------------------------> Generic Web Crawler--------------------------------------------------

@app.route("/generic", methods=['POST'])
def generic_crawler_api():
    if request.method=="POST":
        GTR=request.form.get("GTR", "")
        CTR=request.form.get("CTR", "") 
        url=request.form["url"]
        links=request.form.get("links")
        headings=request.form.get("headings")
        paragraphs=request.form.get("paragraphs")
        pictures=request.form.get("pictures")
        videos=request.form.get("videos")
        domain=request.form.get("domain")
        ip=request.form.get("ip") 
        print(url)
        task_queue.generic_crawler_taks.apply_async(kwargs={"url": url,"GTR": GTR, "CTR":CTR , 
        "links":links, "headings":headings, "paragraphs":paragraphs, "pictures":pictures,
         "videos":videos, "domain":domain, "ip":ip}, queue="generic_queue")
  
        return jsonify({"status":200, "message" :"task submitted"})


#--------------------------------------------------target internet Survey-----------------------------------------------------
@app.route("/tis", methods=['POST', "GET"])
def target_internet_suvery():
    keywords=[request.form.get("email"),
    request.form.get("address"),
    request.form.get("phone"),
    request.form.get("name")]
    keywords = list(filter(None, keywords))
    results=task_queue.target_survey.apply_async(kwargs={"keywords":keywords},ignore_result=False)
    return jsonify({"data" :results.get()})
    
#------------------------------------------------------------keybase managment System-----------------------------------------
@app.route("/keybase", methods=["POST"])
def keybase_system():
    payload=request.get_json()
    results=task_queue.keybase_system.apply_async(kwargs={"payload":payload}, queue="generic_queue")
    return jsonify({"data" :"results.get()"})


#-------------------------------------------------------------> News Crawlers ----------------------------------------------------------
@app.route("/news", methods=["POST"])
def news_api():
    if request.method=="POST":
        channel_name=str(request.form.get("channel_name"))
        channel_name=channel_name.upper()
        print(channel_name)
        GTR=request.form.get("GTR")
        CTR=request.form.get("CTR")  
        number_of_headlines=request.form["number_of_headlines"]
        task_queue.news_tasks.apply_async( kwargs={"channel_name":channel_name,  
                                        "number_of_headlines":number_of_headlines,"GTR": GTR, "CTR":CTR } , queue="news_queue") 
        return jsonify({"status":200, "message" :"task submitted"})

#-------------------------------------------------------------> RSS Feeds ----------------------------------------------------------------

@app.route("/feeds", methods=["GET"])
def feeds():
    GTR=request.form.get("GTR")
    CTR=request.form.get("CTR")
    task_queue.feed_tasks.apply_async(kwargs={"GTR": GTR, "CTR":CTR } ,queue="news_queue")
    return jsonify({"status":200, "message" :"task submitted"})

#------------------------------------------------------------> News Search Engine ---------------------------------------------------------
@app.route("/news_search", methods=['GET'])
def search_engine():
    if request.method =="GET":
        query=str(request.form.get("query"))
        if query!="":
            query=query.replace(" ", "%")
            url="https://news.google.com/rss/search?q="+query+""
            results=SearchEngine(url=url)
            return jsonify({"data" :results.getHeadlines()})
    return  jsonify({"status":404, "message" :"error request"})

#--------------------------------------------------------------> Twitter ------------------------------------------------------------

@app.route("/twitter/smart",methods=['POST'])
def smartsearch():
    if request.method =="POST":
        username=request.form.get("username", None)
        if username is not None: 
            result= task_queue.twitter_smart_search.apply_async(kwargs={"username":username}, ignore_result=False )
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/twitter/target", methods=['POST'])
def twitter_profile():
    if request.method =="POST":
        username=request.form.get("username", None)
        GTR=request.form.get("GTR")
        CTR=request.form.get("CTR")
        if username is not None:
            task_queue.twitter_user.apply_async(kwargs={"username":username, "GTR": GTR, "CTR":CTR }, queue="twitter_queue")
            return jsonify({"status":200, "message" :"task submitted"})
    return  jsonify({"status":404, "message" :"error request"})


@app.route("/twitter/search", methods=['POST'])
def twitter_search():
    if request.method =="POST":
        query=request.form.get("query", None)
        if query is not None: 
            result= task_queue.twitter_search.apply_async(kwargs={"query":query},  ignore_result=False )
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/twitter/targetidentification", methods=['POST'])
def twitter_search_idneitfication():
    if request.method =="POST":
        query=request.form.get("query", None)
        if query is not None: 
            result= task_queue.targetidentification.apply_async(kwargs={"query":query},  ignore_result=False )
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

#------------------------------------------------------------> Twitter Trends <---------------------------------------------------------

@app.route("/twitter/trends/country", methods=["POST"])
def twitter_country_trends():
    if request.method =="POST": 
        country=request.form.get("country", None)            
        task_queue.twitter_country_trends.apply_async(kwargs={"country":country}, queue="twitter_queue")
        return jsonify({"status":200, "message" :"task submitted"})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/twitter/trends/world", methods=["POST"])
def twitter_world_trends():
    if request.method =="POST":          
        task_queue.twitter_world_trends.apply_async(kwargs={}, queue="twitter_queue")
        return jsonify({"status":200, "message" :"task submitted"})
    return  jsonify({"status":404, "message" :"error request"})

#---------------------------------------------------------------> Facebook <-----------------------------------------------------------

@app.route("/fb/smart",methods=[ 'POST'])
def facebook_smart_search():
    if request.method =="POST":
        username=request.form.get("username", None)
        entity_type=str(request.form.get("entity_type"))
        entity_type=entity_type.lower()
        result=task_queue.facebook_smart_search.apply_async(kwargs={"username":username, "entity_type":entity_type}, ignore_result=False)
        return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/fb/target",methods=[ 'POST'])
def facebook_profile():
    if request.method =="POST":
        
        username=request.form.get("username", None)
        GTR=request.form.get("GTR")
        CTR=request.form.get("CTR")
        entity_type=request.form.get("entity_type")

        if entity_type=="profile": 
            task_queue.facebook_user.apply_async(kwargs={"username":username, "GTR": GTR, "CTR":CTR}, queue="fb_queue")
            return jsonify({"status":200, "message" :"USER task submitted"})
        if entity_type=="page": 
            task_queue.facebook_page.apply_async(kwargs={"username":username, "GTR": GTR, "CTR":CTR}, queue="fb_queue")
            return jsonify({"status":200, "message" :"PAGE task submitted"})
        if entity_type=="group": 
            task_queue.facebook_group.apply_async(kwargs={"username":username, "GTR": GTR, "CTR":CTR}, queue="fb_queue")
            return jsonify({"status":200, "message" :"GROUP task submitted"})

    return  jsonify({"status":404, "message" :"error request"})

@app.route("/fb/search", methods=['POST'])
def facebook_search():
    if request.method =="POST":
        name=request.form.get("query", None)
 
        result= task_queue.facebook_search.apply_async(kwargs={"query":name},  ignore_result=False)
        return jsonify({"data":result.get()})
        
    return  jsonify({"status":404, "message" :"error request"})

#-------------------------------------------------------------------> Instagram <-----------------------------------------------------------------
@app.route("/insta/target",methods=['POST'])
def insta_profile():
    if request.method =="POST":
        username=request.form.get("username", None)
        category="Author"
        category=category.upper()
        GTR=request.form.get("GTR")
        CTR=request.form.get("CTR")
        if username is not None: 
            print(username, category)
            task_queue.insta_user.apply_async(kwargs={"username":username ,"category": category, "GTR": GTR, "CTR":CTR}, queue="instareddit_queue")
            return jsonify(status=200, message ="task submitted")
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/insta/smart",methods=['POST'])
def insta_smart_search():
    if request.method =="POST":
        username=request.form.get("username", None)
        if username is not None: 
            result=task_queue.insta_smart_search.apply_async(kwargs={"username":username })
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/insta/search", methods=['POST'])
def insta_search():
    if request.method =="POST":
        query=request.form.get("query", None)
        if query is not None: 
            result= task_queue.instagram_search.apply_async(kwargs={"query":query},  ignore_result=False )
            print(result.get())
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

#-------------------------------------------------------------------> Linkedin <------------------------------------------------------------

@app.route("/linkedin/target", methods=['POST'])
def linkedin_profile():
    if request.method =="POST":
        username=request.form.get("username", None)
        Company=request.form.get("company", False)
        GTR=request.form.get("GTR")
        CTR=request.form.get("CTR")
        entity_type=request.form.get("entity_type")
        print(entity_type)
        if entity_type=="company":
            task_queue.linkedin_company.apply_async(kwargs={"username":username,  "GTR": GTR, "CTR":CTR}, queue="linkedin_queue")
        elif entity_type=="profile":
            task_queue.linkedin_user.apply_async(kwargs={"username":username,  "GTR": GTR, "CTR":CTR}, queue="linkedin_queue")
        return jsonify({"status":200, "message" :"task submitted"})
    return  jsonify({"status":404, "message" :"error request"})


@app.route("/linkedin/smart", methods=['POST'])
def linkedin_smart_search():
    if request.method =="POST":
        username=request.form.get("username", None)
        print(username)
        result=task_queue.linkedin_smart_search.apply_async(kwargs={"username":username}, ignore_result=False)
        
        return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/linkedin/search", methods=['POST'])
def linkedin_search():
    if request.method =="POST":
        query=request.form.get("query", None)
        if query is not None: 
            result= task_queue.linkedin_search.apply_async(kwargs={"query":query}, ignore_result=False )
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})


#--------------------------------------------------------------- Reddit --------------------------------------------------------------

@app.route("/reddit/trends", methods=['POST'])
def reddit_trends():
    if request.method =="POST":
        trends_filter=request.form.get("trends_filter", None)
        top_time=request.form.get("top_time", None)

        task_queue.reddit_trends.apply_async(kwargs={"trends_filter":trends_filter, "top_time": top_time}, queue="instareddit_queue")
        return jsonify({"status":200, "message" :"task submitted"})
    return  jsonify({"status":404, "message" :"error request"})

from rScraper.rScraper import smartSearch as rsmartSearch
@app.route("/reddit/smart", methods=['POST'])
def reddit_smart_search():
    if request.method =="POST":
        username=request.form.get("username", None)
        user = rsmartSearch(username = username)
        return jsonify({"data":user})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/reddit/target", methods=['POST'])
def reddit_targets():
    if request.method =="POST":
        username=request.form.get("username", None)
        entity_type=request.form.get("entity_type")
        GTR=request.form.get("GTR")
        CTR=request.form.get("CTR")
        if entity_type=="subreddit":
            task_queue.reddit_subreddit.apply_async(kwargs={"username":username,  "GTR": GTR, "CTR":CTR}, queue="instareddit_queue")
        elif entity_type=="profile": 
            task_queue.reddit_user.apply_async(kwargs={"username":username,  "GTR": GTR, "CTR":CTR}, queue="instareddit_queue")
        return jsonify({"status":200, "message" :"task submitted"})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/reddit/search", methods=['POST'])
def reddit_search():
    if request.method =="POST":
        username=request.form.get("username", None)
        subreddit=request.form.get("subreddit", False)
        if subreddit:
            result=task_queue.Subreddit_reddit_search.apply_async(kwargs={"username":username},ignore_result=False)
            return jsonify({"data":result.get()})
        else: 
            result=task_queue.User_reddit_search.apply_async(kwargs={"username":username}, ignore_result=False)
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})


#----------------------------------------------------------- Youtube ------------------------------------------------------

@app.route("/youtube/target", methods=["POST"])
def youtube_target():
    channel_id=request.form.get("channel_id")
    GTR=request.form.get("GTR")
    CTR=request.form.get("CTR")
    results=task_queue.youtube_target.apply_async(kwargs={"channel_id":channel_id, "GTR": GTR, "CTR":CTR}, queue="youtube_queue")
    return jsonify({"status":200, "message" :results.get()})

@app.route("/youtube/smart", methods=["POST"])
def youtube_smart_search():
    channel_id=request.form.get("channel_id")
    url = f"https://www.youtube.com/channel/{channel_id}"
    data = smartSearch(url)
    return jsonify({"data":data})

@app.route("/youtube/trends", methods=["POST"])
def youtube_trends():
    task_queue.youtube_trends.apply_async(kwargs={}, queue="youtube_queue")
    return jsonify({"status":200, "message" :"task submitted"})

@app.route("/youtube/search", methods=["POST"])
def youtube_search():
    query=request.form.get("query", None)
    data = searchChannel(query)
    return jsonify({"data":data})


#----------------------------------------------------------Google Trends -------------------------------------------------

@app.route("/google/trends", methods=["POST"])
def google_trends():
    country=request.form.get("country")
    realtime=request.form.get("realtime", False)
    print(country)
    if realtime:
        task_queue.google_trends_realtime.apply_async(kwargs={ "country": country}, queue="youtube_queue")
    else:
        task_queue.google_trends_daily.apply_async(kwargs={ "country": country}, queue="youtube_queue")
        
    return jsonify({"status":200, "message" :"task submitted"})


#----------------------------------------------------------------- Avatar API End point -----------------------------------
#---------------------------------------------------------------- Post ---------------------------------------------------

@app.route("/avatar/post", methods=["POST"])
def avatar_post():
    data={
    "text":request.form.get("text"),
    "media":request.form.get("media"),
    "email":request.form.get("email"),
    "password":request.form.get("password"),
    "social_media":request.form.get("social_media")}
    task_queue.avtar_post.apply_async(kwargs={"data":data}, queue="avatar_queue")
    return jsonify({"status":200, "message" :"task submitted"})

#---------------------------------------------------------------- comment ---------------------------------------------------

@app.route("/avatar/comment", methods=["POST"])
def avatar_comment():
    data={
    "text":request.form.get("text"),
    "email":request.form.get("email"),
    "password":request.form.get("password"),
    "social_media":request.form.get("social_media"),
    "target_post":request.form.get("target_post")}
    task_queue.avtar_comment.apply_async(kwargs={"data":data}, queue="avatar_queue")
    return jsonify({"status":200, "message" :"task submitted"})

#---------------------------------------------------------------- Like ---------------------------------------------------

@app.route("/avatar/reaction", methods=["POST"])
def avatar_like():
    data={"social_media":request.form.get("social_media"),
        "target_post":request.form.get("target_post"),
        "email":request.form.get("email"),
        "password":request.form.get("password"),
        "reaction":request.form.get("reaction"),}
    task_queue.avtar_Reaction.apply_async(kwargs={"data":data}, queue="avatar_queue")
    return jsonify({"status":200, "message" :"task submitted"})

#---------------------------------------------------------------- share ---------------------------------------------------

@app.route("/avatar/share", methods=["POST"])
def avatar_share():
    data={
    "text":request.form.get("text"),
    "social_media":request.form.get("social_media"),
    "email":request.form.get("email"),
    "password":request.form.get("password"),
    "target_post":request.form.get("target_post")}
    task_queue.avatar_share.apply_async(kwargs={"data":data}, queue="avatar_queue")
    return jsonify({"status":200, "message" :"task submitted"})



#---------------------------------------------------------------tools ----------------------------------------------------
@app.route("/fakeperson", methods=["POST"])
def fake_person_generator():
    nationality=request.form.get("nationality")
    gender=request.form.get("gender")
    age=request.form.get("age")
    result=task_queue.fake_person_generator.apply_async(kwargs={"nationality":nationality, "gender":gender, "age":age}, ignore_result=False)
    return jsonify({"data":result.get()})

@app.route("/darkweb", methods=["POST"])
def darkweb():
    if request.method =="POST":
        query=request.form.get("query", None)
        if query is not None: 
            result= task_queue.darkweb.apply_async(kwargs={"query":query}, ignore_result=False )
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/scholar", methods=["POST"])
def scholar():
    if request.method =="POST":
        query=request.form.get("query", None)
        if query is not None: 
            result= task_queue.scholar_.apply_async(kwargs={"query":query}, ignore_result=False )
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/patents", methods=["POST"])
def patents():
    if request.method =="POST":
        query=request.form.get("query", None)
        if query is not None: 
            result= task_queue.patents_.apply_async(kwargs={"query":query}, ignore_result=False )
            return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/ip_shortend_url", methods=["POST"])
def ip_shortend_url():
    if request.method =="POST":
        url=request.form.get("url", None)
        result= task_queue.ip_shortend_url.apply_async(kwargs={"url":url}, ignore_result=False )
        return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})

@app.route("/ip_tracking", methods=["POST"])
def ip_tracking():
    if request.method =="POST":
        code=request.form.get("code", None)
        start_date=request.form.get("start_date", None)
        end_date=request.form.get("end_date", None)
        result= task_queue.ip_tracking.apply_async(kwargs={"code":code, "start_date":start_date, 
            "end_date":end_date}, ignore_result=False )
        return jsonify({"data":result.get()})
    return  jsonify({"status":404, "message" :"error request"})


from werkzeug.utils import secure_filename

@app.route("/imagereverse", methods=["POST"])
def image_rever_looku():
    url=json.load(request.files["data"])
    try:
        files=request.files["files"]
        file_name = files.filename or ''
        if file_name !="":
            files.save(secure_filename(file_name))
            path=os.getcwd()+"/"+secure_filename(file_name)
            result= task_queue.image_rever_lookup.apply_async(kwargs={"url":path}, ignore_result=False )
            return jsonify({"data":result.get()})
    except:
        if  url is not None:
            path=url["url"]
            print(path)
            result= task_queue.image_rever_lookup.apply_async(kwargs={"url":path}, ignore_result=False )
            return jsonify({"data":result.get()})
        return  jsonify({"status":404, "message" :"error request"})









#-------------------------------->>>>>>>> App Run <<<<<<<<<<<<<<<<<<-------------------#
app.run(host=HOST, port=PORT)
