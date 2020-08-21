import json
import requests
import os
import uuid
import pika
import sys
API_ENDPOINT="http://192.168.18.13:5000/"
from publisher import Rabbit_Publisher
class DataHandler:
    def __init__(self, data="" , GTR="", CTR=""):
        self.GTR=GTR
        self.CTR=CTR
        self.data=data

    def dump_json(self):
        self.data["GTR"]=self.GTR
        self.data["CTR"]=self.CTR
        files = [('files', ''),('data', ('data', json.dumps(self.data), 'application/json')),]
        req = requests.post(url=API_ENDPOINT, files=files )

        #pub = Rabbit_Publisher(username='mca',password='rapidev',exchange='control_exchange')
        print(req.text)


class TargetDataHandler:
    def __init__(self, data="", target_type=""):
        self.data=data
        self.data["target_type"]=target_type
    def send_data(self):
        req = requests.post(url=API_ENDPOINT+"receiver", json=self.data )
        print(req.text)