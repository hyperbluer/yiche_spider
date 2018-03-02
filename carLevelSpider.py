# -*- coding:utf-8 -*-
from __future__ import division
import MySQLdb
import urllib2
import math
import json

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
    page_size = 100

    def __init__(self):
        self.conn = MySQLdb.connect(
            host=MYSQL_CONFIG['host'],
            db=MYSQL_CONFIG['dbname'],
            user=MYSQL_CONFIG['user'],
            passwd=MYSQL_CONFIG['passwd'],
            port=MYSQL_CONFIG['port'],
            charset=MYSQL_CONFIG['charset'])
        self.cursor = self.conn.cursor();

    def parse(self):
        i = 0
        level_list = self.get_level_list()
        for level in level_list:
            count = self.parse_page(level[0], 1)
            i += int(count)

        print '记录数：' + str(i)

    def parse_page(self, level_id, current_page):
        start_url = self.parse_start_url % (level_id, current_page, self.page_size)
        request = urllib2.Request(start_url)
        request.add_header('user-agent', self.custom_settings['DEFAULT_REQUEST_HEADERS']['user-agent'])
        response = urllib2.urlopen(request)
        result = response.read()
        if not result:
            return None

        result = json.loads(result)
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

    def get_level_list(self):
        sql = 'SELECT level_id FROM base_yiche_car_level'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result


if __name__ == '__main__':
    spider = CarLevelSpider()
    spider.parse()
