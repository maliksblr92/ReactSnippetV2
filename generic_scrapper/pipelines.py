# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import json

class GenericScrapperPipeline(object):
    def open_spider(self, spider):
        self.file=open('./data/generic/data/data.json', "w")
        header='{"data": ['
        self.file.write(header)

    def close_spider(self, spider):
        footer='{}]}'
        self.file.write(footer)
        self.file.close()
    
    def process_item(self, item, spider):
        line=json.dumps(dict(item))+ ","
        self.file.write(line)
        return item
    



class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item
