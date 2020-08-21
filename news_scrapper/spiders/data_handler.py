'''
    DESCRIPTION:
    ------------
    * The purpose of this class is create a folder for news scrapper
    * Export the json file to Folder
'''
import json
import requests
import os
import uuid
import pika
import sys
API_ENDPOINT="http://192.168.18.13:5000/news_receiver"
class DataHandler:
    def __init__(self, file_name, json_data, GTR, CTR):
        self.channel_name=file_name
        self.CTR=CTR
        self.GTR=GTR
        self.data=json_data
    def dump_json(self):
        data={"GTR":self.GTR,"CTR":self.CTR,"channel_name": self.channel_name,"data":json.dumps(self.data)}
        req=requests.post(url=API_ENDPOINT, json=data)
        print("------------------------", req.text)
#         self.broad_cast_message(req.text)
        
#     def broad_cast_message(self, text):
#         credientials=pika.credentials.PlainCredentials("ocs", "rapidev")
#         connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host='192.168.18.27', credentials=credientials))
#         channel = connection.channel()
#         channel.exchange_declare(exchange='logs', exchange_type='fanout')
#         message = text
#         channel.basic_publish(exchange='logs', routing_key='', body=message)
#         connection.close()
