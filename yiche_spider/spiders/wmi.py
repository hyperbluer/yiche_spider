# -*- coding: utf-8 -*-
import scrapy
from yiche_spider import items
import re

class WmiSpider(scrapy.Spider):
    name = 'wmi'
    allowed_domains = ['cvtsc.org.cn']
    start_urls = ['http://www.cvtsc.org.cn/cvtsc/vin/index.htm']
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'accept-language': 'zh-CN,zh;q=0.8',
            'referer': 'https://www.baidu.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3251.0 Safari/537.36',
        }
    }

    def parse(self, response):
        list_page_selector = response.xpath('//div[@class="channel_news_list_m"]/div[@class="c1-body"]//div[@class="c1-bline"]//a')
        for page_selector in list_page_selector:
            page_title = page_selector.xpath('@title').extract()[0]
            page_url = page_selector.xpath('@href').extract()[0]
            if not page_title.startswith(u'关于公布世界制造厂识别代号'):
                continue

            yield scrapy.Request(page_url, callback=self.parse_page_data)

        # 执行分页遍历
        next_page_selector = response.xpath('//div[@class="pagination"]//a[3]')
        next_page_url = next_page_selector.xpath('@href').extract()[0]
        if next_page_url:
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_page_data(self, response):
        news_title = response.xpath('//div[@id="news_title"]').extract()[0]
        batch_number_result = re.findall(u'第(.*)批', news_title)
        news_content_selector = response.xpath('//div[@id="news_content"]')
        table_selector = news_content_selector.xpath('.//table[@class="MsoNormalTable"][1]')
        if table_selector:
            # 若有table，则附件数据在当前页
            item_list_selector = table_selector.xpath('tbody//tr')
            for item_selector in item_list_selector:
                try:
                    item = items.CarWmiItem()
                    company_name = item_selector.xpath('td[2]//span/text()').extract()
                    item['company_name'] = ''.join(company_name)
                    reg_address = item_selector.xpath('td[3]//span/text()').extract()
                    item['reg_address'] = ''.join(reg_address)
                    item['wmi'] = item_selector.xpath('td[4]//span/text()').extract()[0]
                    item['brand_name'] = item_selector.xpath('td[5]//span/text()').extract()[0]
                    car_style = item_selector.xpath('td[6]//span/text()').extract()
                    item['car_style'] = ''.join(car_style)
                    item['batch_number'] = batch_number_result[0]
                    yield item
                except:
                    continue
        else:
            # 若无table，则需检索链接地址采集附件数据
            page_link_selector = news_content_selector.xpath('.//a')
            for link_selector in page_link_selector:
                link_text = link_selector.xpath('text()').extract()
                link_url = None
                if link_text and u'获准的车辆生产企业世界制造厂识别代号' in link_text[0]:
                    link_url = link_selector.xpath('@href').extract()[0]
                else:
                    link_text_2 = link_selector.xpath('.//span').extract()
                    if link_text_2 and u'附件1' in link_text_2[0]:
                        link_url = link_selector.xpath('@href').extract()[0]
                    elif link_text_2 and u'获准的车辆生产企业世界制造厂识别代号' in link_text_2[0]:
                        link_url = link_selector.xpath('@href').extract()[0]
                if link_url:
                    page_url = 'http://www.'+self.allowed_domains[0] + link_url
                    yield scrapy.Request(page_url, callback=self.parse_page_2_data)
                    break

    def parse_page_2_data(self, response):
        news_title = response.xpath('//div[@id="news_title"]').extract()[0]
        batch_number_result = re.findall(u'第(.*)批', news_title)
        news_content_selector = response.xpath('//div[@id="news_content"]')
        table_selector = news_content_selector.xpath('.//table')
        if table_selector:
            # 若有table，则附件数据在当前页
            item_list_selector = table_selector.xpath('.//tbody//tr')
            for item_selector in item_list_selector:
                try:
                    item = items.CarWmiItem()
                    company_name = item_selector.xpath('td[2]//div/text()').extract()
                    if company_name:
                        item['company_name'] = item_selector.xpath('td[2]//div/text()').extract()[0]
                        item['reg_address'] = item_selector.xpath('td[3]//div/text()').extract()[0]
                        item['wmi'] = item_selector.xpath('td[4]//div/text()').extract()[0]
                        brand_name = item_selector.xpath('td[5]//div/text()').extract()
                        if brand_name:
                            item['brand_name'] = brand_name[0]
                        else:
                            item['brand_name'] = item_selector.xpath('td[5]//span/text()').extract()[0]
                        car_style = item_selector.xpath('td[6]//span/text()').extract()
                        item['car_style'] = ''.join(car_style)
                        item['batch_number'] = batch_number_result[0]
                    else:
                        company_name = item_selector.xpath('td[2]//span/text()').extract()
                        item['company_name'] = ''.join(company_name)
                        reg_address = item_selector.xpath('td[3]//span/text()').extract()
                        item['reg_address'] = ''.join(reg_address)
                        item['wmi'] = item_selector.xpath('td[4]//span/text()').extract()[0]
                        item['brand_name'] = item_selector.xpath('td[5]//span/text()').extract()[0]
                        car_style = item_selector.xpath('td[6]//span/text()').extract()
                        item['car_style'] = ''.join(car_style)
                        item['batch_number'] = batch_number_result[0]
                    yield item
                except:
                    continue
