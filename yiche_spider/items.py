# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YicheSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BrandItem(scrapy.Item):
    third_id = scrapy.Field()
    name = scrapy.Field()
    logo = scrapy.Field()
    remote_logo = scrapy.Field()
    pass
