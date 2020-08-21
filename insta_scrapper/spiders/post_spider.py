import scrapy
import os
import json
from .Exportjson import Exportjson
class PostSpider(scrapy.Spider):
    '''
    DESCRIPTION:
    ------------
    * This class inherits the 'Spider' class of Scrapy.
    * this Crawler load the Json file from user Dirctory
    * First you need to extract the User profile then Run this crawler
    '''
    name="post_spider"
    allowed_domains=["www.instagram.com"]
    def __init__(self,username ,**kwargs):
        self.post_name=[]
        self.count=0
        self.username=username
        list_of_urls=[]
        self.currentdir=os.getcwd()
        self.mainfolder="crawler/Insta_crawler"
        self.path=f"{self.currentdir}/{self.mainfolder}/{self.username}/{self.username}.json"
        try:
            with open(self.path) as json_data:
                data = json.load(json_data)
                post_shorcuts =self.extract_shortcut_code(data)
                if post_shorcuts is None:
                    #if there is no shorcuts in json file of user it means
                    # the account is private or account have no post 
                    print("************************ The Account is Private ****************")
                for shortcut in post_shorcuts:
                     list_of_urls.append(f"https://www.instagram.com/p/{shortcut}?__a=1")
                     self.post_name.append(shortcut)
                json_data.close
        except Exception as e:
            print(e)
        self.start_urls=list_of_urls
        super().__init__(**kwargs)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        #print("----> Error ",data)
        file_name=self.post_name[self.count]
        file_n=Exportjson(file_name,data, folder_name="Posts")
        file_n.make_dir()
        file_n.dump_json()
        self.count=self.count+1

    def extract_shortcut_code(self, data):
       shortcuts=[]
       for edges in data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]:
           shortcuts.append(edges["node"]["shortcode"])
          
       return shortcuts
