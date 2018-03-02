# -*- coding:utf-8 -*-
from __future__ import division
import MySQLdb
import urllib2
import math
import json
from lxml import etree

# 本地
MYSQL_CONFIG = {
    'host': 'localhost',
    'dbname': 'car',
    'user': 'root',
    'passwd': '123456',
    'port': 3306,
    'charset': 'utf8',
}


class CarLevelSpider(object):
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'accept-language': 'zh-CN,zh;q=0.8',
            'referer': 'https://www.baidu.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3251.0 Safari/537.36',
        }
    }
    parse_start_url = 'http://select.car.yiche.com/api/selectcartool/searchresult?external=Car.m&l=%s&page=%s&pagesize=%s'
    parse_car_url = 'http://car.m.yiche.com/%s'
    page_size = 100

    def __init__(self):
        self.conn = MySQLdb.connect(
            host=MYSQL_CONFIG['host'],
            db=MYSQL_CONFIG['dbname'],
            user=MYSQL_CONFIG['user'],
            passwd=MYSQL_CONFIG['passwd'],
            port=MYSQL_CONFIG['port'],
            charset=MYSQL_CONFIG['charset'])
        self.cursor = self.conn.cursor()

    def parse(self):
        i = 0
        level_list = self.get_level_list()
        for level in level_list:
            count = self.parse_page(level[0], 1)
            i += int(count)

        i += self.parse_offline_car()

        print '记录数：' + str(i)

    # 解析易车网在售的车级别车型json数据
    def parse_page(self, level_id, current_page):
        start_url = self.parse_start_url % (level_id, current_page, self.page_size)
        request = urllib2.Request(start_url)
        request.add_header('user-agent', self.custom_settings['DEFAULT_REQUEST_HEADERS']['user-agent'])
        response = urllib2.urlopen(request)
        html = response.read()
        if not html:
            return None

        result = json.loads(html)
        if not result['Count']:
            return None

        for row in result['ResList']:
            try:
                sql = 'INSERT INTO base_yiche_car2level (car_third_id, level_id) VALUES (%s, %s)'
                params = (row['SerialId'], level_id)
                self.cursor.execute(sql, params)
                self.conn.commit()
            except MySQLdb.DatabaseError:
                continue

        total_page = int(math.ceil(result['Count'] / self.page_size))
        if current_page < total_page:
            current_page += 1
            self.parse_page(level_id, current_page)

        return result['Count']

    # 解析易车网停售的车型，从车介绍页面文字获取车所在级别
    def parse_offline_car(self):
        i = 0
        sql = 'SELECT a.third_id, a.en_name FROM base_yiche_car a WHERE NOT EXISTS (SELECT * FROM base_yiche_car2level b WHERE a.third_id = b.car_third_id) AND a.en_name > ""'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if not result:
            return None

        level_list = self.get_level_list()
        for car in result:
            car_url = self.parse_car_url % car[1]
            request = urllib2.Request(car_url)
            request.add_header('user-agent', self.custom_settings['DEFAULT_REQUEST_HEADERS']['user-agent'])
            response = urllib2.urlopen(request)
            html = response.read()
            if not html:
                continue

            selector = etree.HTML(html)
            result = selector.xpath('//div[@class="car-price"]/dl[2]/dd/text()')
            if not result:
                continue
            level_name = ((result[0]).split(u'第'))[0]
            # 转换特殊文字
            if level_name == u'中大型SUV':
                level_name = u'大型SUV'
            elif level_name == u'卡车':
                level_name = u'皮卡'

            for level in level_list:
                if level[1] == level_name:
                    try:
                        sql = 'INSERT INTO base_yiche_car2level (car_third_id, level_id) VALUES (%s, %s)'
                        params = (car[0], level[0])
                        self.cursor.execute(sql, params)
                        self.conn.commit()

                        i += 1

                        # 若此级别有上级，则同时将此车与上级的关联入库
                        if level[2]:
                            sql = 'INSERT INTO base_yiche_car2level (car_third_id, level_id) VALUES (%s, %s)'
                            params = (car[0], level[2])
                            self.cursor.execute(sql, params)
                            self.conn.commit()
                            i += 1
                    except MySQLdb.DatabaseError:
                        pass

                    break

        return i

    def get_level_list(self):
        sql = 'SELECT level_id, level_name, parent_level_id FROM base_yiche_car_level'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result


if __name__ == '__main__':
    spider = CarLevelSpider()
    spider.parse()
