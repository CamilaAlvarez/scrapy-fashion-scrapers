# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FashionScrapperItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    details = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    categories = scrapy.Field()
