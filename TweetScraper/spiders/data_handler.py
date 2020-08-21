import json
import requests
import os
import uuid
import pika
import sys
API_ENDPOINT="http://192.168.18.13:5000/"
class DataHandler:
    def __init__(self, file_name, json_data , request_id=""):
        self.channel_name=file_name
        self.data=json_data
        self.request_id=request_id
    def dump_json(self, target):
        data={"request_id":self.request_id, "data":json.dumps(self.data)}
        req=requests.post(url=API_ENDPOINT+target, data=data)
        print("------------------------", self.data )
        #self.broad_cast_message(req.text)
        
    def broad_cast_message(self, text):
        credientials=pika.credentials.PlainCredentials("ocs", "rapidev")
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='192.168.18.27', credentials=credientials))
        channel = connection.channel()
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        message = text
        channel.basic_publish(exchange='logs', routing_key='', body=message)
        connection.close()

class TargetDataHandler:
    def __init__(self, data="", target_type=""):
        self.data=data
        self.data["target_type"]=target_type
    def send_data(self):
        req = requests.post(url=API_ENDPOINT+"receiver", json=self.data )
        print(self.data)
        print(req.text)