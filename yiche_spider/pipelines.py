# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
from yiche_spider import items


class YicheSpiderPipeline(object):
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    @classmethod
    def from_settings(cls, settings):
        conn = MySQLdb.connect(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset=settings['MYSQL_CHARSET'])
        cursor = conn.cursor()
        return cls(conn, cursor)

    def process_item(self, item, spider):
        try:
            if isinstance(item, items.BrandItem):
                # 品牌数据入库
                sql = 'INSERT INTO base_yiche_car_brand (third_id, `name`, remote_logo, logo) VALUES (%s, %s, %s, %s)'
                params = (item['third_id'], item['name'], item['remote_logo'], item['logo'])
                self.cursor.execute(sql, params)
                self.conn.commit()
            elif isinstance(item, items.CarItem):
                # 车型数据入库
                sql = 'INSERT INTO base_yiche_car (third_id, `name`, show_name, en_name, brand_third_id, factory_third_id, factory_name) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                params = (item['third_id'], item['name'], item['show_name'], item['en_name'], item['brand_third_id'],
                          item['factory_third_id'], item['factory_name'])
                self.cursor.execute(sql, params)
                self.conn.commit()
            elif isinstance(item, items.CarVersionItem):
                # 车款数据入库
                sql = 'INSERT INTO base_yiche_car_version (third_id, `name`, car_third_id, refer_price, year_type, sale_state, tt) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                params = (item['third_id'], item['name'], item['car_third_id'], item['refer_price'], item['year_type'],
                          item['sale_state'], item['tt'])
                self.cursor.execute(sql, params)
                self.conn.commit()
            elif isinstance(item, items.CarVersionAttrItem):
                # 车款配置数据入库
                sql = 'INSERT INTO base_yiche_car_version_attr (car_version_third_id, content) VALUES (%s, %s)'
                params = (item['car_version_third_id'], item['content'])
                self.cursor.execute(sql, params)
                self.conn.commit()
            elif isinstance(item, items.CarWmiItem):
                # 车款配置数据入库
                sql = 'INSERT INTO base_car_wmi (wmi, brand_name, company_name, reg_address, car_style, batch_number) VALUES (%s, %s, %s, %s, %s, %s)'
                params = (item['wmi'], item['brand_name'], item['company_name'], item['reg_address'], item['car_style'], item['batch_number'])
                self.cursor.execute(sql, params)
                self.conn.commit()
            else:
                pass
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        return item


# 车辆品牌异步入库
class BrandPipelineAsync(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        '''1、@classmethod声明一个类方法，而对于平常我们见到的叫做实例方法。
           2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
           3、可以通过类来调用，就像C.f()，相当于java中的静态方法'''
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset=settings['MYSQL_CHARSET'],
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams) # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool) # 相当于dbpool付给了这个类，self中可以得到

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.__conditional_insert, item)
        query.addErrback(self._handle_error, item, spider)
        return item

    def __conditional_insert(self, conn, item):
        sql = 'INSERT INTO base_yiche_car_brand (third_id, `name`, remote_logo, logo) VALUES (%s, %s, %s, %s)'
        params = (item['third_id'], item['name'], item['remote_logo'], item['logo'])
        conn.execute(sql, params)

    def _handle_error(self, failue, item, spider):
        print failue


# 图片文件下载
class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'remote_logo' in item:
            yield scrapy.Request(item['remote_logo'])

    def item_completed(self, results, item, info):
        if 'remote_logo' in item:
            image_paths = [x['path'] for ok, x in results if ok]
            if not image_paths:
                raise DropItem("Item contains no images")
            item['logo'] = image_paths[0]
        return item
