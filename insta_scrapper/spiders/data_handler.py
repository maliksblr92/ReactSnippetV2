import json
import requests
import os
import uuid
import pika
import sys
from .insta import insta_followers

API_ENDPOINT="http://192.168.18.13:5000/"
from publisher import Rabbit_Publisher
class DataHandler:
    def __init__(self, username="", data="" , GTR="", CTR=""):
        self.GTR=GTR
        self.CTR=CTR
        self.data=data
        self.username = username

    def dump_json(self):
        print(self.data)
        self.data["followers"] = insta_followers(username = self.username)
        self.data["GTR"]=self.GTR
        self.data["CTR"]=self.CTR
        files = [('files', ''),('data', ('data', json.dumps(self.data), 'application/json')),]
        req = requests.post(url=API_ENDPOINT, files=files )

        #pub = Rabbit_Publisher(username='mca',password='rapidev',exchange='control_exchange')
        print(req.text)