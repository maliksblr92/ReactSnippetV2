from datetime import datetime
import requests
import json

def get(query):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
    }
    try:
        r = requests.get(query, headers = headers)
    except requests.exceptions.RequestException as rExcep:
        print("Failed: ", rExcep)
        return ''
    if r.status_code == 200:
        return r.text
    else:
        print(r.status_code)
        return ''

def preprocessCodes(code):
    return "_".join(code.lower().split())

def scriptToJSON(script):
    return "{" + "}".join(script.partition("{")[2].split("}")[:-1]) + "}"

def datetimeFromTimestamp(timestamp):
    try:
        if timestamp:
            return datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    return ''

def posts(soup):
    posts = []
    script = soup.find('script', id = 'data')
    if script:
        script = scriptToJSON(script.text)
    else:
        return posts
    script = json.loads(script)
    try:
        allPosts = script["posts"]["models"]
    except (KeyError, TypeError):
        print("Major Error")
        return []
    for p in allPosts.values():
        post = {
            "poster": {
                "author_id": "",
                "username": "",
                "link": ""
            },
            "post_id": "",
            "post_link": "",
            "is_posted_by_moderator": False,
            "timestamp": "",
            "subreddit": {
                "id": "",
                "name": "",
                "link": "",
            },
            "categories": [],
            "is_promoted": False,
            "text": "",
            "media": "",
            "statistics": {
                "upvote_ratio": 0,
                "num_comments": 0,
                "num_crossposts": 0,
                "score": 0
            }
        }
        post["post_id"] = p.get("postId", '')
        post["poster"]["author_id"] = p.get('authorId', '')
        post["poster"]["username"] = p.get('author', '')
        if post["poster"]["username"] != "":
            post["poster"]["link"] = 'https://www.reddit.com/user/' + post["poster"]["username"]
        post["text"] = p.get('title', '')
        post["statistics"]["num_comments"] = p.get('numComments', 0)
        post["statistics"]["num_crossposts"] = p.get('numCrossposts', 0)
        post["statistics"]["score"] = p.get('score', 0)
        post["statistics"]["upvote_ratio"] = p.get('upvoteRatio', 0)
        post["categories"] = p.get('contentCategories', [])
        if post["categories"] is None:
            post["categories"] = []
        post["post_link"] = p.get('permalink', '')
        if p.get('distinguishType') == 'moderator':
            post["is_posted_by_moderator"] = True
        try:
            if p["belongsTo"]["type"] == 'subreddit':
                post["subreddit"]["id"] = p["belongsTo"]["id"]
                post["subreddit"]["name"] = post["post_link"].partition("/r/")[2].partition("/")[0]
                post["subreddit"]["link"] = "".join(post["post_link"].partition(f'/r/{post["subreddit"]["name"]}')[:-1])
            elif p["belongsTo"]["type"] == 'profile':
                post["is_promoted"] = True
            post["media"] = p["media"]["content"]
        except (KeyError, TypeError):
            pass
        ti = p.get('created')
        if ti:
            ti = round(ti/1000)
            post["timestamp"] = datetimeFromTimestamp(ti)
        posts.append(post)
    return posts
