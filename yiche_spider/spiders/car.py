# -*- coding: utf-8 -*-
import scrapy
import json
import re
import hashlib
from yiche_spider import items


class CarSpider(scrapy.Spider):
    name = 'car'
    allowed_domains = ['bitauto.com']
    start_urls = ['http://api.car.bitauto.com/CarInfo/getlefttreejson.ashx?tagtype=baojia&pagetype=&objid=']
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS" : {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'accept-language': 'zh-CN,zh;q=0.8',
            'referer': 'https://www.baidu.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3251.0 Safari/537.36',
        }
    }
    base_url = 'http://price.bitauto.com/'
    base_api_url = 'http://api.car.bitauto.com/'
    base_brand_logo_img_path = 'http://image.bitautoimg.com/bt/car/default/images/logo/masterbrand/png/100/m_%s_100.png'
    base_car_list_url = base_api_url+'CarInfo/MasterBrandToSerialNew.aspx?type=5&pid=%s&rt=serial&serias=m&key=serial_%s_5_m&include=1'
    base_car_version_list_url = base_api_url+'CarInfo/MasterBrandToSerialNew.aspx?type=5&pid=%s&rt=cartype&serias=m&key=cartype_%s_5_m&include=1'

    def parse(self, response):
        result = re.findall(r'type:\"(.*?)\",id:(.*?),name:\"(.*?)\",url:\"(.*?)\",cur', response.body)
        for brand in result:
            id = brand[1]
            name = brand[2]
            logo_image = self.base_brand_logo_img_path % id

            # 保存品牌入库
            item = items.BrandItem()
            item['third_id'] = id
            item['name'] = name
            item['remote_logo'] = logo_image
            # item['remote_logo'] = hashlib.sha1(item['remote_logo']).hexdigest()
            yield item

            # url = self.base_url + brand[3]
            url = self.base_car_list_url % (id, id)
            # print url
            yield scrapy.Request(url, callback=self.parse_car_data)
            # break

    # 解析车型json串
    def parse_car_data(self, response):
        data = response.body
        dict_data = json.loads(data[data.find('{'):], strict=False)
        for k in dict_data:
            # 保存品牌车型入库
            item = items.CarItem()
            item['third_id'] = dict_data[k]['id']
            item['name'] = dict_data[k]['name']
            item['show_name'] = dict_data[k]['showName']
            item['en_name'] = dict_data[k]['urlSpell']
            item['brand_third_id'] = dict_data[k]['pid']
            item['factory_third_id'] = dict_data[k]['goid']
            item['factory_name'] = dict_data[k]['goname']
            yield item

            url = self.base_car_version_list_url % (item['third_id'], item['third_id'])
            # print url
            yield scrapy.Request(url, callback=self.parse_car_version_data)
            # break

    # 解析车款json串
    def parse_car_version_data(self, response):
        data = response.body
        dict_data = json.loads(data[data.find('{'):], strict=False)
        for k in dict_data:
            # 保存车款入库
            item = items.CarVersionItem()
            item['car_third_id'] = dict_data[k]['pid']
            item['third_id'] = dict_data[k]['id']
            item['name'] = dict_data[k]['name']
            item['refer_price'] = dict_data[k]['referprice']
            item['sale_state'] = dict_data[k]['salestate']
            item['year_type'] = dict_data[k]['goname']
            item['tt'] = dict_data[k]['tt']
            yield item

            # yield scrapy.Request(url, callback=self.parse_car_version_attr_data)
            # break

    # 解析品牌页，提取品牌下所有车型
    def parse_brand_page(self, response):
        # print response.body
        page_xpath = '//div[@id="c_result"]//div[contains(@class, "img-info-layout-vertical")]/div[@class="img"]/a/attribute::href'
        result = response.xpath(page_xpath)
        for car in result:
            url = self.base_url + car.extract()
            yield scrapy.Request(url, callback=self.parse_car_page)
            break

    # 解析车型页，提取车型下所有车款
    def parse_car_page(self, response):
        # 获取车的几项指标
        car_name = response.xpath('//div[@class="crumbs-txt"]/strong[last()]/text()').extract()
        factory_name = response.xpath('//div[@class="crumbs-txt"]//a[last()]/text()').extract()
        car_image = response.xpath('//div[contains(@class, "card-layout")]//div[@class="img"]/a/img/attribute::src').extract()
        car_price = response.xpath('//div[contains(@class, "card-layout")]//div[@class="desc"]//div[@class="col-xs-4"][last()]/h5/text()').extract()
        car_params_url = response.xpath('//div[contains(@class, "card-layout")]/div[contains(@class, "section-header")]/div[@class="more"]//a[1]/@href')

        # todo 保存车型入库

        # 获取车款列表
        car_version_list = response.xpath('//div[contains(@class, "card-layout")]//div[@class="drop-layer"]//a')
        for car_version in car_version_list:
            car_version_page_url = self.base_url + car_version.xpath('@href').extract()[0]
            car_version_name = self.base_url + car_version.xpath('text()').extract()[0]
            # todo 保存车款入库

        yield scrapy.Request(car_params_url, callback=self.parse_car_version_attr_page)

    def parse_car_version_attr_page(self, response):
        pass

    @staticmethod
    def parse_jsonp(jsonp):
        try:
            return json.loads(re.search('^[^(]*?\((.*)\)[^)]*$', jsonp).group(1))
        except:
            raise ValueError('Invalid Input')

