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
    initial = scrapy.Field()
    logo = scrapy.Field()
    remote_logo = scrapy.Field()


class CarItem(scrapy.Item):
    third_id = scrapy.Field()
    name = scrapy.Field()
    show_name = scrapy.Field()
    en_name = scrapy.Field()
    brand_third_id = scrapy.Field()
    factory_third_id = scrapy.Field()
    factory_name = scrapy.Field()


class CarVersionItem(scrapy.Item):
    car_third_id = scrapy.Field()
    third_id = scrapy.Field()
    name = scrapy.Field()
    refer_price = scrapy.Field()
    year_type = scrapy.Field()
    sale_state = scrapy.Field()
    tt = scrapy.Field()


class CarVersionAttrItem(scrapy.Item):
    car_version_third_id = scrapy.Field()
    content = scrapy.Field()
