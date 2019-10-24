import re
from pymongo import *
import requests
import json
import datetime
import time
import threading
from bs4 import BeautifulSoup
from copy import deepcopy
from su8 import connRedis


class ctrip:
    def __init__(self, start_date, end_date, hotel_name, ordUrl, hotel_Id, hotelId):
        # 构造请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16G77 NebulaSDK/1.8.100112 Nebula WK PSDType(0) AlipayDefined(nt:WIFI,ws:375|603|2.0) AliApp(AP/10.1.72.6003) AlipayClient/10.1.72.6003 Language/zh-Hans Region/CN',
            'Referer': 'https://2017081708237081.hybrid.alipay-eco.com/2017081708237081/0.2.1904232103.32/index.html#pages/hotel/detail/index?__appxPageId=123&id={}&inday={}&outday={}'.format(hotel_Id, start_date, end_date),
            'Content-Type': 'application/json',
        }
        self.hotel_name = hotel_name
        # 酒店房间信息接口
        self.url = "https://m.ctrip.com/restapi/soa2/14605/getaroomlist"
        self.start_date = start_date
        self.ordUrl = ordUrl
        self.hotel_id = hotel_Id
        self.hotelId = hotelId
        # 上传参数    入住日期    退房日期    酒店id
        self.json = {"hotelId": self.hotel_id,
        "checkinDate": start_date,
        "checkoutDate": end_date,
        "head": {"auth": "E37FB103EE47FE89F413E6B9BF56DE1994CC1D293BAEDCA953EC7F9940C2D9F8"}  # 登录状态
        }
        # 链接mongo 数据库
        client = MongoClient('localhost', 27017)
        db_name = 'su8'
        self.db = client[db_name]
        self.conn = connRedis.OPRedis()  # 链接代理
        self.hotel_list = []

    def get_data(self):
        """
        发送请求 获取 json 数据
        :param hotelId: 酒店Id
        :return:
        """
        # 发送post 请求获取酒店信息
        global data
        i = 0
        # 设置超时链接　请求5次数据
        while i < 5:
            try:
                # print(self.json)
                r = requests.post(self.url, json=self.json, headers=self.headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')}, timeout=5)
                # print(r.text)
                data = json.loads(r.text)
                break
            except:
                i += 1
                print("酒店: {}请求超时,重新请求, 请求链接:{}".format(self.hotel_name, self.url))
                data = {'ResponseStatus': {'Ack': False}}
        errorCode = data['ResponseStatus']['Ack']
        if errorCode == 'Success':
            if len(data['baseRoomList']):
                roomList = data['baseRoomList']
                # grade = self.getGrade()
                for room in roomList:
                    # 酒店名  房型
                    item = {'hotel_name': self.hotel_name,} # 'ordUrl': self.ordUrl
                    if self.hotel_name[:2] == "速8":
                        item['hotel_id'] = int(self.hotelId)
                        item['rival_id'] = int('0')
                    else:
                        item['hotel_id'] = int('0')
                        item['rival_id'] = int(self.hotelId)
                    rpList = room['subRoomList']
                    for rp in rpList:
                        if rp['name'] == "(钟点房)":
                            item['room_type'] = room['name']+'(钟点房)'
                        elif rp['hourInfoName'] != '':
                            item['room_type'] = room['name']+'('+rp['hourInfoName']+')'
                        else:
                            item['room_type'] = room['name']
                        prod_name = ''  # 产品名称
                        for r in rp['promotionTagList']:
                            try:
                                if r['name'] == '每日特惠':
                                    prod_name += "(" + r['name'] + ")"
                            except:
                                # 无产品名称
                                continue
                        if prod_name == '':
                            prod_name = rp['breakfast'] + rp['bed'] + str(rp['maxNum']) + '人'
                        else:
                            prod_name = rp['breakfast'] + rp['bed'] + str(rp['maxNum']) + '人'+ prod_name
                        item['prod_name'] = prod_name
                        item['price'] = rp['price']  # 酒店价格
                        item['rebate'] = rp['refundAmount']+rp['minusAmount']  # 优惠价格
                        item['channel'] = "携程"  # 渠道来源
                        for r in rp['serviceTagList']:
                            try:
                                if r['name'] == '代理':
                                    item['channel'] = r['name']
                            except:
                                # 无渠道来源
                                continue
                        item['can_book'] = rp['status']  # 房态　1:预订　else:满房
                        item['breakfast'] = rp['breakfast']
                        item['crawlDate'] = str(datetime.date.today())
                        item['crawlTime'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        item['source'] = 'Ctrip-携程'  # 数据来源
                        item['arrDate'] = self.start_date
                        # item['grade'] = float(grade)
                        self.clean_data(item)
                # 当前日期酒店数据抓取完毕　更新为1
                self.db.hotelUrl.update({'ctrip.hotel_id': self.hotel_id}, {'$set': {'ctrip.{}'.format(self.start_date): 1}}, multi=True)
            else:
                print(self.hotel_name, self.ordUrl, '无客房信息')
                self.db.hotelUrl.update({'ctrip.hotel_id': self.hotel_id}, {'$set': {'ctrip.{}'.format(self.start_date): 2}}, multi=True)

        else:
            print(self.hotel_name, self.ordUrl, '无店铺信息')
            self.db.hotelUrl.update({'ctrip.hotel_id': self.hotel_id}, {'$set': {'ctrip.{}'.format(self.start_date): 2}},
                                    multi=True)

    def clean_data(self, item):
        if item['can_book'] == 1:
            item['can_book'] = '预订'
        else:
            item['can_book'] = '房满'
        self.save_data(item)

    def save_data(self, item):
        print(item)
        self.hotel_list.append(deepcopy(item))

    def __del__(self):
        url = 'http://114.55.84.165:8081/api/super8/saveHotelData'
        headers = {'Content-Type': 'application/json'}

        if len(self.hotel_list) != 0:
            r = requests.post(url,headers=headers, json=self.hotel_list)
            self.db.hotel_data.insert(self.hotel_list)
            # print(self.hotel_list)
            print(r.text)

    def getGrade(self):
        url = 'https://hotels.ctrip.com/hotel/{}.html'.format(self.hotel_id)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        }
        response = requests.get(url, headers=headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        grade = soup.find(class_='score')
        if grade is not None:
            grade = grade.string
        else:
            grade = ''
        return grade


def getTime(i):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=i)
    enday = datetime.timedelta(days=i + 1)
    start_day = str(today + oneday)
    end_date = str(today + enday)
    return start_day, end_date


def db():
    client = MongoClient('localhost', 27017)
    db_name = 'su8'
    db = client[db_name]
    return db


def run():
    for i in range(1, 4):
        start_day, end_date = getTime(i)
        hotelList = db().ctrip_url.find()
        j = 0
        for hotel in hotelList:
            j += 1
            print(j)
            if hotel['ctripUrl'] is not None:
                hotel_name = hotel['hotelName']
                ordUrl = re.sub(r'\?(.*)?$', '', hotel['ctripUrl'])
                hotel_id = ''.join(re.findall(r"\d+", ordUrl))
                hotelId = hotel['hotelId']
                print(start_day, end_date, hotel_name, hotel_id, ordUrl)
                a = ctrip(start_day, end_date, hotel_name, ordUrl, hotel_id, hotelId)
                a.get_data()
        hotelList.close()


if __name__ == '__main__':
    # t1 = threading.Thread(target=run, args=(1, 'thread1',))
    # t2 = threading.Thread(target=run, args=(2, 'thread2',))
    # t3 = threading.Thread(target=run, args=(3, 'thread3',))
    # t1.start()
    # t2.start()
    # t3.start()
    run()
