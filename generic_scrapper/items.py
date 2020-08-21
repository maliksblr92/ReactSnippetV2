# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class GenericScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    page=scrapy.Field()
    title=scrapy.Field()
    images=scrapy.Field()
    image_urls=scrapy.Field()
    content=scrapy.Field()

    large_headings=scrapy.Field()
    small_headings=scrapy.Field()
    

