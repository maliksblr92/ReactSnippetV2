import json
import requests
import os
import uuid
import pika
import sys
import zipfile
import shutil
from publisher import Rabbit_Publisher
from os import listdir
from os.path import isfile, join

API_ENDPOINT="http://192.168.18.13:5000/"
ROOT=os.getcwd()

#------------------------------------------------------------------ General Purpose Data Handle ---------------------------
class DataHandler:
    def __init__(self, data="" , GTR="", CTR=""):
        self.GTR=GTR
        self.CTR=CTR
        self.data=data
        self.data["GTR"]=self.GTR
        self.data["CTR"]= self.CTR
    def send_data(self):
        files = [('files', ''),('data', ('data', json.dumps(self.data), 'application/json')),]
        req = requests.post(url=API_ENDPOINT, files=files )
        print(req.text)

    def dump_json(self,  root=""):
        zipf = zipfile.ZipFile(f'{self.CTR}.zip', 'w', zipfile.ZIP_DEFLATED)
        self.zipdir("."+root, zipf)
        zipf.close()
        try: 
                
            files = [('files', (self.CTR, open(ROOT+"/"+ self.CTR+".zip", 'rb'), 'application/octet')),('data', ('data', json.dumps(self.data), 'application/json')),]
            req = requests.post(url=API_ENDPOINT, files=files )
            #pub = Rabbit_Publisher(username='mca',password='rapidev',exchange='control_exchange')
            os.remove(f"{self.CTR}.zip")
            self.cleandir(ROOT+""+root)
        except Exception as e:
            print(e)
 
    
    def zipdir(self, path, ziph):
        os.chdir(path)
        for root, dirs, files in os.walk('.'):
            for file in files:
                ziph.write(os.path.join(root, file))
        os.chdir(ROOT)
    
    def cleandir(self, path):
        dirs=os.listdir(path)
        for dir in dirs:
            shutil.rmtree(path+"/"+dir)
            print(dir)

#--------------------------------------------------------------linkedin-------------------------------------------------
class LinkedDataHandler:
    def __init__(self, data, CTR="" , GTR=""):
        self.CTR=CTR
        self.GTR=GTR
        self.data=data

    def dump_json(self,  send_zip=False , smart_search=False, company=False):
        self.data["GTR"]=self.GTR
        self.data["CTR"]= self.CTR
        print("----->>>>>>>>>>>>>>>", self.data)
        if company:
            files = [('files', ''),('data', ('data', json.dumps(self.data), 'application/json')),]
            req = requests.post(url=API_ENDPOINT, files=files )
            print(req.text)
            return 
        else:
            img=self.data["personal_info"]["image"]
            files = [('files', (img, open(img, 'rb'), 'application/octet')),('data', ('data', json.dumps(self.data), 'application/json')),]
            req = requests.post(url=API_ENDPOINT, files=files )
        os.remove({img})
        
    def send_image_ss(self):
        self.data["GTR"]="smart_search"
        self.data["CTR"]=self.data["personal_info"]["name"]
        files = [('files', ("profile_image", open(self.data["personal_info"]["image"], 'rb'), 'application/octet')),
        ('data', ('data', json.dumps(self.data), 'application/json')),]
        req = requests.post(url=API_ENDPOINT, files=files)
        response_data=req.json()["filepath"]

        data={"id": "No profile Id in Linkedin", "full_name":self.data["personal_info"]["name"],
        "profile_image_url":response_data}
        print(req.json())
        os.remove(self.data["personal_info"]["image"])

        return data

import twint
class TweetDataHandler:
    def __init__(self, username, CTR="" , GTR=""):
        self.CTR=CTR
        self.GTR=GTR
        self.username=username
    def tweeter_followrs(self):
        c = twint.Config()
        c.Username = self.username
        c.User_full = True
        c.Store_object = True
        twint.run.Followers(c)
        return twint.output.users_list


    def send_profile_data(self ):
        root="./data/user"
        data={}
        with open(f"{root}/{self.username}.json", 'r') as json_data:
            profile_info = json.load(json_data)
            tweets=self.Tweet_data()
            data={"CTR":self.CTR, "GTR":self.GTR, "profile":profile_info, "tweets":tweets, "followers":self.tweeter_followrs()}
            files = [('files', ""),('data', ('data', json.dumps(data), 'application/json')),]
            req = requests.post(url=API_ENDPOINT, files=files )

        os.remove(f"{root}/{self.username}.json")

    def Tweet_data(self):
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

class TargetDataHandler:
    def __init__(self, data="", target_type=""):
        self.data=data
        self.data["target_type"]=target_type
    def send_data(self):
        req = requests.post(url=API_ENDPOINT+"receiver", json=self.data )
        print(req.text)