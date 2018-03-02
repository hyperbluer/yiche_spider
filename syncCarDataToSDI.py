# -*- coding: utf-8 -*-

import MySQLdb
import pypinyin
from pypinyin.constants import Style
import time
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
# 开发线
# MYSQL_CONFIG = {
#     'host': '116.205.13.101',
#     'dbname': 'database',
#     'user': 'root',
#     'passwd': 'QVmGZw5dC9nnQ3Lt',
#     'port': 3309,
#     'charset': 'utf8',
# }

COUNTER_CODE_CONFIG = {
    'brand': 'BRAD',
    'factory': 'FACT',
    'car': 'CARR',
    'car_version': 'VERS',
}


class SyncCarDataToSDI(object):
    def __init__(self):
        self.conn = MySQLdb.connect(
            host=MYSQL_CONFIG['host'],
            db=MYSQL_CONFIG['dbname'],
            user=MYSQL_CONFIG['user'],
            passwd=MYSQL_CONFIG['passwd'],
            port=MYSQL_CONFIG['port'],
            charset=MYSQL_CONFIG['charset'])
        self.cursor = self.conn.cursor()

    # 同步品牌
    def sync_car_brand(self):
        # 遍历所有易车车辆品牌
        sql = 'SELECT third_id, `name`, initial, logo FROM base_yiche_car_brand'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        i = 0
        for row in result:
            # 检测数据库是否已经同步过此数据
            check_sql = 'SELECT count(*) AS c FROM base_car_brand WHERE third_id = %s AND is_sync_third = 2' % row[0]
            self.cursor.execute(check_sql)
            check_result = self.cursor.fetchone()
            if check_result and check_result[0]:
                continue

            # 首字母处理
            initial = None
            if not row[2]:
                initial = (pypinyin.lazy_pinyin(row[1], style=Style.FIRST_LETTER)[0]).upper()[0:1]

            logo = row[3]
            logo = logo.replace('full/', '/car_brand/')

            # 写入增量数据
            insert_sql = 'INSERT INTO base_car_brand (brand_code, third_id, `name`, first_char, logo, is_sync_third, updated_time) VALUES (%s, %s, %s, %s, %s, 2, %s)'
            params = (self.get_counter_code(COUNTER_CODE_CONFIG['brand']), row[0], row[1], initial, logo, int(time.time()))
            self.cursor.execute(insert_sql, params)

            i += 1
        self.conn.commit()

        print '记录数：' + str(i)

    # 同步车型
    def sync_car(self):
        # 遍历所有车型
        sql = 'SELECT third_id, `name`, en_name, brand_third_id, factory_third_id, factory_name FROM base_yiche_car'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        i = 0
        for row in result:
            # 查询品牌code
            brand_sql = 'SELECT brand_code FROM base_car_brand WHERE third_id = %s AND is_sync_third = 2' % row[3]
            self.cursor.execute(brand_sql)
            brand_result = self.cursor.fetchone()
            if not brand_result or not brand_result[0]:
                continue

            # 查询厂商
            factory_sql = 'SELECT factory_code FROM base_car_factory WHERE third_id = %s AND is_sync_third = 2' % row[4]
            self.cursor.execute(factory_sql)
            factory_result = self.cursor.fetchone()
            if not factory_result or not factory_result[0]:
                # 写入厂商增量数据
                factory_code = self.get_counter_code(COUNTER_CODE_CONFIG['factory'])
                insert_sql = 'INSERT INTO base_car_factory (brand_code, factory_code, `name`, third_id, is_sync_third, updated_time) VALUES (%s, %s, %s, %s, 2, %s)'
                params = (brand_result[0], factory_code, row[5], row[4],
                          int(time.time()))
                self.cursor.execute(insert_sql, params)
            else:
                factory_code = factory_result[0]

            # 查询车名
            car_sql = 'SELECT id, car_code, factory_code FROM base_car WHERE third_id = %s AND is_sync_third = 2' % row[0]
            self.cursor.execute(car_sql)
            car_result = self.cursor.fetchone()
            if car_result and car_result[0]:
                if not car_result[2]:
                    update_sql = 'UPDATE base_car SET factory_code = "%s" WHERE id= %s' % (factory_code, car_result[0])
                    self.cursor.execute(update_sql)
                continue

            # 写入增量数据
            insert_sql = 'INSERT INTO base_car (brand_code, factory_code, car_code, `name`, name_alias, third_id, price_level, size_level, is_sync_third, updated_time) VALUES (%s, %s, %s, %s, %s, %s, 0, 0, 2, %s)'
            params = (brand_result[0], factory_code, self.get_counter_code(COUNTER_CODE_CONFIG['car']), row[1], row[2], row[0], int(time.time()))
            self.cursor.execute(insert_sql, params)

            i += 1
        self.conn.commit()

        print '记录数：' + str(i)

    # 同步车款
    def sync_car_version(self):
        # 遍历所有车型
        sql = 'SELECT car_third_id, third_id, `name`, refer_price, year_type, sale_state  FROM base_yiche_car_version'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        i = 0
        for row in result:
            # 检测数据库是否已经同步过此数据
            check_sql = 'SELECT count(*) AS c FROM base_car_version WHERE third_id = %s AND is_sync_third = 2' % row[1]
            self.cursor.execute(check_sql)
            check_result = self.cursor.fetchone()
            if check_result and check_result[0]:
                continue

            # 查询车型code
            car_sql = 'SELECT brand_code,car_code FROM base_car WHERE third_id = %s AND is_sync_third = 2' % row[0]
            self.cursor.execute(car_sql)
            car_result = self.cursor.fetchone()
            if not car_result or not car_result[1]:
                continue

            # 处理年款字段，去掉款字
            year_type = None
            if row[4]:
                year_type = (row[4])[0:4]

            # 写入增量数据
            insert_sql = 'INSERT INTO base_car_version (brand_code, car_code, version_code, `name`, price, yeartype, salestate, third_id, is_sync_third, updated_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 2, %s)'
            params = (car_result[0], car_result[1], self.get_counter_code(COUNTER_CODE_CONFIG['car_version']), row[2], row[3], year_type, row[5], row[1], int(time.time()))
            self.cursor.execute(insert_sql, params)

            i += 1
        self.conn.commit()

        print '记录数：' + str(i)

    # 同步车型参数
    def sync_car_version_attr(self):
        i = 0
        # 清空表内容
        sql = 'TRUNCATE TABLE base_car_version_attr'
        self.cursor.execute(sql)
        self.conn.commit()

        group_dict = self.get_params_group_dict()
        for k, v in group_dict.items():
            sql = 'SELECT count(*) AS c FROM base_car_version_attr WHERE attr = "%s"' % k
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            if result and result[0]:
                continue
            else:
                # 写入增量数据
                insert_sql = 'INSERT INTO base_car_version_attr (attr, `name`, p_attr_id, `type`, relat_product) VALUES (%s, %s, %s, %s, %s)'
                params = (k, v, 0, 2, 0)
                self.cursor.execute(insert_sql, params)
                self.conn.commit()
            i += 1

        params_dict = self.get_params_dict()
        for k, v in params_dict.items():
            group_k = k.split('.')[0]
            item_k = k.split('.')[1]
            sql = 'SELECT id FROM base_car_version_attr WHERE attr = "%s"' % group_k
            self.cursor.execute(sql)
            group_result = self.cursor.fetchone()
            p_attr_id = group_result[0]
            sql = 'SELECT id FROM base_car_version_attr WHERE attr = "%s"' % item_k
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            if result and result[0]:
                continue
            else:
                # 写入增量数据
                insert_sql = 'INSERT INTO base_car_version_attr (attr, `name`, p_attr_id, `type`, relat_product) VALUES (%s, %s, %s, %s, %s)'
                params = (item_k, v, p_attr_id, 2, 1)
                self.cursor.execute(insert_sql, params)
                self.conn.commit()
            i += 1

        print '记录数：' + str(i)

    # 同步车型参数值
    def sync_car_version_attr_data(self):
        i = 0
        # 获取一级参数列表
        sql = 'SELECT id,attr FROM base_car_version_attr WHERE p_attr_id = 0'
        self.cursor.execute(sql)
        attr_top_result = self.cursor.fetchall()
        tmp = {}
        for row in attr_top_result:
            tmp[row[0]] = row[1]
        attr_top_result = tmp

        #获取二级参数列表
        sql = 'SELECT id,attr,p_attr_id FROM base_car_version_attr WHERE p_attr_id > 0'
        self.cursor.execute(sql)
        attr_sub_result = self.cursor.fetchall()
        attr_sub_result = list(attr_sub_result)
        for row in attr_sub_result:
            k = attr_sub_result.index(row)
            row = list(row)
            row.append(attr_top_result[row[2]])
            attr_sub_result[k] = row

        # 遍历所有车型
        sql = 'SELECT version_code,third_id FROM base_car_version WHERE is_sync_third = 2 ORDER BY id ASC'
        self.cursor.execute(sql)
        version_result = self.cursor.fetchall()
        for version in version_result:
            # 判断库中是否有此车款参数值数据
            # sql = 'SELECT count(*) AS c FROM base_car_version_attr_data WHERE version_code = "%s"' % version[0]
            # self.cursor.execute(sql)
            # result = self.cursor.fetchone()
            # if result and result[0]:
            #     continue

            # 每插入10000条数据休眠1秒
            # if not (i % 10000):
            #     time.sleep(1)

            sql = 'SELECT car_version_third_id, content FROM base_yiche_car_version_attr WHERE car_version_third_id = %d' % version[1]
            self.cursor.execute(sql)
            version_attr_result = self.cursor.fetchone()
            if version_attr_result and version_attr_result[0]:
                dict_data = json.loads(version_attr_result[1])
                sql = 'INSERT INTO base_car_version_attr_data (version_code, attr_id, `data`) VALUES (%s, %s, %s)'
                attr_data_list = []
                for attr in attr_sub_result:
                    if attr[3] in dict_data.keys() and attr[1] in dict_data[attr[3]].keys():
                        attr_data = [version[0], attr[0], dict_data[attr[3]][attr[1]]]
                        attr_data_list.append(attr_data)
                        i += 1
                self.cursor.executemany(sql, attr_data_list)
                self.conn.commit()
            else:
                continue

        print '记录数：' + str(i)

    # 设置车辆价格级别
    def set_car_price_level(self):
        i = 0
        # 获取车辆价格区间列表
        sql = 'SELECT price_level,price_min FROM base_car_price_level ORDER BY price_min DESC'
        self.cursor.execute(sql)
        level_result = self.cursor.fetchall()

        sql = 'SELECT id, car_code FROM base_car WHERE is_sync_third = 2 ORDER BY id ASC'
        self.cursor.execute(sql)
        car_result = self.cursor.fetchall()
        for car in car_result:
            sql = 'SELECT max(price) FROM base_car_version WHERE car_code = "%s"' % car[1]
            self.cursor.execute(sql)
            version_result = self.cursor.fetchone()
            max_price = 0
            if version_result and version_result[0]:
                max_price = version_result[0]

            price_level = 1
            for level in level_result:
                if (float(max_price) > int(level[1])):
                    price_level = int(level[0])
                    break

            sql = 'UPDATE base_car SET price_level = %d WHERE id = %d' % (int(price_level), int(car[0]))
            self.cursor.execute(sql)
            self.conn.commit()
            i += 1
        print '记录数：' + str(i)

    # 设置车辆面积级别
    def set_car_size_level(self):
        sql = 'UPDATE base_car SET size_level = 1'
        self.cursor.execute(sql)
        self.conn.commit()
        # sql = 'SELECT id base_car_version_attr WHERE attr = "seatnumber"'
        # self.cursor.execute(sql)
        # attr_result = self.cursor.fetchone()
        # if not attr_result or not attr_result[0]:
        #     print '未找到座位数参数'
        #     return
        #
        # sql = 'SELECT version_id base_car_version_attr_data WHERE attr_id = %d' % int(attr_result[0])

    # 获取自动累加器
    def get_counter_code(self, name):
        name = name.upper()
        sql = 'SELECT count FROM base_counter_codes WHERE name = "%s"' % name
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result:
            sql = 'UPDATE base_counter_codes SET `count` = `count` + 1 WHERE name = "%s"' % name
            self.cursor.execute(sql)
            self.conn.commit()
            return name + str(result[0]+1).zfill(7)
        else:
            sql = 'INSERT INTO base_counter_codes (name, `count`) VALUES (%s, %s)'
            params = (name, 1)
            self.cursor.execute(sql, params)
            self.conn.commit()
            return name + str(1).zfill(7)

    @staticmethod
    def get_params_group_dict():
        group_dict = {
            'base': '基础',
            'body': '车身',
            'engine': '动力',
            'gearbox': '变速箱',
            'chassisbrake': '底盘制动',
            'safe': '安全配置',
            'doormirror': '门窗/后视镜',
            'wheel': '车轮',
            'light': '灯光',
            'internalconfig': '内部配置',
            'seat': '座椅',
            'entcom': '信息娱乐',
            'aircondrefrigerator': '空调/冰箱',
        }
        return group_dict

    @staticmethod
    def get_params_dict():
        params_dict = {
            'base.price': '厂商指导价',
            'base.warrantypolicy': '保修政策',
            'base.maxspeed': '最高车速',
            'base.comfuelconsumption': '混合工况油耗',
            'base.officialaccelerationtime100': '0-100km/h加速时间',
            # 车身
            'body.len': '长',
            'body.width': '宽',
            'body.height': '高',
            'body.wheelbase': '轴距',
            'body.weight': '整备质量',
            'body.seatnumber': '座位数',
            'body.luggagevolume': '行李厢容积',
            'body.fueltankcapacity': '油箱容积',
            'body.color': '车身颜色',
            'body.inductionluggage': '电动行李厢',
            'body.roofluggagerack': '车顶行李箱架',
            'body.sportpackage': '运动外观套件',
            # 动力
            'engine.displacementml': '排气量',
            'engine.displacement': '排量',
            'engine.maxpower': '最大功率',
            'engine.maxhorsepower': '最大马力',
            'engine.maxpowerspeed': '最大功率转速',
            'engine.maxtorque': '最大扭矩',
            'engine.maxtorquespeed': '最大扭矩转速',
            'engine.cylinderarrangetype': '缸体形式',
            'engine.cylindernum': '气缸数',
            'engine.intakeform': '进气形式',
            'engine.fuelmethod': '供油方式',
            'engine.fuelgrade': '燃油标号',
            'engine.startstopsystem': '发动机启停',
            'engine.environmentalstandards': '环保标准',
            # 变速箱
            'gearbox.gearbox': '变速箱类型',
            'gearbox.levelnumber': '挡位个数',
            # 底盘制动
            'chassisbrake.drivemode': '驱动方式',
            'chassisbrake.frontsuspensiontype': '前悬架类型',
            'chassisbrake.rearsuspensiontype': '后悬架类型',
            'chassisbrake.adjustablesuspension': '可调悬架',
            'chassisbrake.frontbraketype': '前轮制动器类型',
            'chassisbrake.rearbraketype': '后轮制动器类型',
            'chassisbrake.parkingbraketype': '驻车制动类型',
            'chassisbrake.bodystructure': '车体结构',
            'chassisbrake.centerdifferentiallock': '限滑差速器/差速锁',
            # 安全配置
            'safe.abs': '防抱死制动(ABS)',
            'safe.ebd': '制动力分配(EBD/CBC等)',
            'safe.brakeassist': '制动辅助(BA/EBA/BAS等)',
            'safe.tractioncontrol': '牵引力控制(ARS/TCS/TRC等)',
            'safe.esp': '车身稳定控制(ESP/DSC/VSC等)',
            'safe.airbagdrivingposition': '主驾驶安全气囊',
            'safe.airbagfrontpassenger': '副驾驶安全气囊',
            'safe.airbagfrontside': '前侧气囊',
            'safe.airbagrearside': '后侧气囊',
            'safe.aircurtainside': '侧安全气帘',
            'safe.airbagknee': '膝部气囊',
            'safe.airbagseatbelt': '安全带气囊',
            'safe.airbagrearcenter': '后排中央气囊',
            'safe.tirepressuremonitoring': '胎压监测',
            'safe.zeropressurecontinued': '零胎压续行轮胎',
            'safe.isointerface': '后排儿童座椅接口(ISO FIX/LATCH)',
            'safe.centrallocking': '中控锁',
            'safe.intelligentkey': '智能钥匙',
            # 行车辅助
            'safe.cruisecontrol': '定速巡航',
            'safe.ldws': '车道保持',
            'safe.auxiliary': '并线辅助',
            'safe.activebraking': '碰撞报警/主动刹车',
            'safe.fatiguereminding': '疲劳提醒',
            'safe.automaticparkingintoplace': '自动泊车',
            'safe.pilotedparking': '遥控泊车',
            'safe.autopilotauxiliary': '自动驾驶辅助',
            'safe.automaticparking': '自动驻车',
            'safe.hillstartassist': '上坡辅助',
            'safe.hilldescent': '陡坡缓降',
            'safe.nightvisionsystem': '夜视系统',
            'safe.vgrs': '可变齿比转向',
            'safe.frontparkingradar': '前倒车雷达',
            'safe.reversingradar': '后倒车雷达',
            'safe.reverseimage': '倒车影像',
            'safe.drivemode': '驾驶模式选择',
            # 门窗/后视镜
            'doormirror.skylightstype': '天窗类型',
            'doormirror.frontelectricwindow': '前电动车窗',
            'doormirror.rearelectricwindow': '后电动车窗',
            'doormirror.externalmirroradjustment': '外后视镜电动调节',
            'doormirror.rearviewmirrorantiglare': '内后视镜自动防眩目',
            'doormirror.flowmediummirror': '流媒体后视镜',
            'doormirror.externalmirrorantiglare': '外后视镜自动防眩目',
            'doormirror.privacyglass': '隐私玻璃',
            'doormirror.rearwindowsunshade': '后遮阳帘',
            'doormirror.rearsidesunshade': '后排侧遮阳帘',
            'doormirror.frontwiper': '前雨刷器',
            'doormirror.rearwiper': '后雨刷器',
            'doormirror.electricpulldoor': '电吸门',
            # 车轮
            'wheel.fronttiresize': '前轮胎规格',
            'wheel.reartiresize': '后轮胎规格',
            'wheel.sparetiretype': '备胎',
            # 灯光
            'light.headlighttype': '前大灯',
            'light.daytimerunninglight': '	LED日间行车灯',
            'light.headlightautomaticopen': '自动大灯',
            'light.frontfoglight': '前雾灯',
            'light.headlightfunction': '大灯功能',
            # 内部配置
            'internalconfig.material': '内饰材质',
            'internalconfig.interiorairlight': '车内氛围灯',
            'internalconfig.sunvisormirror': '遮阳板化妆镜',
            'internalconfig.steeringwheelmaterial': '方向盘材质',
            'internalconfig.steeringwheelmultifunction': '多功能方向盘',
            'internalconfig.steeringwheeladjustment': '方向盘调节',
            'internalconfig.steeringwheelheating': '方向盘加热',
            'internalconfig.steeringwheelexchange': '方向盘换挡',
            # 座椅
            'seat.seatmaterial': '座椅材质',
            'seat.sportseat': '运动风格座椅',
            'seat.driverseatelectricadjustment': '主座椅电动调节',
            'seat.auxiliaryseatelectricadjustmentmode': '副座椅电动调节',
            'seat.driverseatadjustmentmode': '主座椅调节方式',
            'seat.auxiliaryseatadjustmentmode': '副座椅调节方式',
            'seat.secondrowseatadjustmentectricmode': '第二排座椅电动调节',
            'seat.secondrowseatadjustmentmode': '第二排座椅调节方式',
            'seat.frontcenterarmrest': '前排中央扶手',
            'seat.rearseatcenterarmrest': '后座中央扶手',
            'seat.thirdrowseat': '第三排座椅',
            'seat.seatdownmode': '座椅放倒方式',
            'seat.rearcupholder': '后排杯架',
            # 信息娱乐
            'entcom.consolelcdscreen': '中控彩色液晶屏',
            'entcom.alllcdpanels': '全液晶仪表盘',
            'entcom.computerscreen': '行车电脑显示屏',
            'entcom.huddisplay': '中控彩色液晶屏',
            'entcom.gps': 'GPS导航',
            'entcom.locationservice': '智能互联定位',
            'entcom.voicecontrol': '语音控制',
            'entcom.internetos': '手机互联(Carplay&Android)',
            'entcom.wirelesscharging': '手机无线充电',
            'entcom.gesturecontrol': '手势控制系统',
            'entcom.cddvd': 'CD/DVD',
            'entcom.bluetooth': '蓝牙/WIFI连接',
            'entcom.externalinterface': '外接接口',
            'entcom.cartv': '车载电视',
            'entcom.audiobrand': '音响品牌',
            'entcom.speakernum': '扬声器数量',
            'entcom.rearlcdscreen': '后排液晶屏/娱乐系统',
            'entcom.supplyvoltage': '车载220V电源',
            # 空调/冰箱
            'aircondrefrigerator.frontairconditioning': '前排空调',
            'aircondrefrigerator.rearairconditioning': '后排空调',
            'aircondrefrigerator.airconditioning': '香氛系统',
            'aircondrefrigerator.airpurifyingdevice': '空气净化',
            'aircondrefrigerator.carrefrigerator': '车载冰箱',
        }
        return params_dict


if __name__ == '__main__':
    sync = SyncCarDataToSDI()
    print '1、同步品牌开始'
    #sync.sync_car_brand()
    print '1、同步品牌结束'

    print '2、同步车型开始'
    #sync.sync_car()
    print '2、同步车型结束'

    print '3、同步车款开始'
    #sync.sync_car_version()
    print '3、同步车款结束'

    print '4、同步车款参数开始'
    #sync.sync_car_version_attr()
    print '4、同步车款参数结束'

    print '5、同步车款参数值开始'
    sync.sync_car_version_attr_data()
    print '5、同步车款参数值结束'

    print '6、设置车名价格所属区间开始'
    #sync.set_car_price_level()
    print '6、设置车名价格所属区间结束'

    print '7、设置车名面积所属区间开始'
    #sync.set_car_size_level()
    print '7、设置车名面积所属区间结束'
