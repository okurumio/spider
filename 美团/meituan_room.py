import threading
import requests, zlib, base64
import random, re
import json, jsonpath
from pymongo import *
import datetime, time
from su8 import connRedis
from copy import deepcopy


class MeiTuan(threading.Thread):
    def __init__(self, day, thread_id):
        threading.Thread.__init__(self)
        self.day = day
        self.thread_id = thread_id
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "Connection": "close",
        }
        self.conn = connRedis.OPRedis()
        self.taken = None
        # 隧道服务器
        self.tunnel_host = ""
        self.tunnel_port = ""
        # 隧道id和密码
        self.tid = ""
        self.password = ""
        self.proxies = {
            "http": "http://%s:%s@%s:%s/" % (self.tid, self.password, self.tunnel_host, self.tunnel_port),
            "https": "http://%s:%s@%s:%s/" % (self.tid, self.password, self.tunnel_host, self.tunnel_port)
        }

    @staticmethod
    def getTime():
        d1 = datetime.datetime(1970, 1, 1)
        d2 = datetime.datetime.now()
        d3 = int((d2 - d1).total_seconds() * 1000)
        return d3

    def url_encode(self, data, stringify=False):
        if (stringify == True):
            base_data = zlib.compress(data.encode())
            data = base64.b64encode(base_data)
            return data
        else:
            data = json.dumps(data).replace(' ', "")
            return self.url_encode(data, True)

    @staticmethod
    def url_decode(data):
        """token解码"""
        if isinstance(data, str):
            data = base64.b64decode(data)
            base_data = zlib.decompress(data)
            return base_data

    def get_uuid(self):
        conn = connRedis.OPRedis()
        url='https://bj.meituan.com/'
        headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        }
        session = requests.session()
        while 1:
            try:
                session.get(url, headers=headers, timeout=2, proxies={'https': conn.randomOneIp('proxy:new_ip_list')})
                html_set_cookie = requests.utils.dict_from_cookiejar(session.cookies)
                return html_set_cookie['iuuid']
            except:
                pass

    def get_taken(self, url):
        i = 0
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(days=1)
        start = int(start_time.timestamp() * 1000)
        end = int(end_time.timestamp() * 1000)
        while i < 5:
            try:
                response = requests.get(url, headers=self.headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
                break
            except:
                i += 1
                response = ''
        if response != '':
            response.encoding = 'utf-8'
            pattern = re.compile('window.__INITIAL_STATE__=(.*);')
            a = pattern.findall(response.text)
            data = json.loads(a[0])
            poiData = data['poiData']
            taken = {}
            taken["name"] = poiData['name']
            # print(taken['name'])
            try:
                taken["cityId"] = poiData['cityId']
            except:
                qualificationInfo = data['poiExt']['qualificationInfo']['qualificationURL']
                taken["cityId"] = re.findall(r'cityId=(\d*)', qualificationInfo)[0]
            taken["poiId"] = poiData['poiid']
            taken["start"] = start
            taken["end"] = end
            taken["?type"] = "1"
            taken["&utm_medium"] = "baiduProgram"
            taken["version_name"] = "8.7.0"
            taken["uuid"] = self.get_uuid()
            return taken

    def get_tokon(self):
        time = int(datetime.datetime.now().timestamp() * 1000)
        # 生成sign的值，并得到_token字典
        sign = 'antiRepCityId=1&antiRepLocateCityId=1&antiRepPlatform=Android&end={}&fromOffline=false&lat=40.032038&lng=116.305609&mtShareId=&openId=odPDr0N6p3m8MAZM-h960Y7BAejU&' \
               'poiId={}' \
               '&programName=hotel&propagateData=undefined&sdkVersion=8.7.0&start={}&type=1' \
               '&utm_medium=WEIXINPROGRAM&uuid={}' \
               '&version_name=10.14.800&wechatVersion=7.0.8'.format(self.taken['end'], self.taken['poiId'], self.taken['start'], self.taken["uuid"])
        _tokon = {
            "rId": 100038,
            "ts": time,
            "cts": time + 13,
            "brVD": [360, 574],
            "brR": [[720, 1148], [720, 1148], 24, 24],
            "bI": ["pages/poi/poi",
                   "pages/list/index"],
            "mT": [],
            "kT": [],
            "aT": [],
            "tT": [],
            "sign": self.url_encode(sign).decode()
        }
        return _tokon

    def get_infotoken(self, uuid):
        time = int(datetime.datetime.now().timestamp() * 1000)
        # 将sign进行加密（微信接口）
        sign='antiRepCityId=1&antiRepLocateCityId=1&antiRepPlatform=Android&end={}&fromOffline=false&lat=40.032038&lng=116.305609&mtShareId=&openId=odPDr0N6p3m8MAZM-h960Y7BAejU&' \
             'poiId={}' \
             '&programName=hotel&propagateData=undefined&sdkVersion=8.7.0&start={}&type=1' \
             '&utm_medium=WEIXINPROGRAM&uuid={}' \
             '&version_name=10.14.800&wechatVersion=7.0.8'.format(self.taken['end'], self.taken['poiId'], self.taken['start'], uuid)

        _tokon = {
            "rId": 100039,
            "ts": time,
            "cts": time+13,
            "brVD": [360,574],
            "brR": [[720,1148],[720,1148],24,24],
            "bI": ["pages/poi/poi",
                   "pages/list/index"],
            "mT": [],
            "kT": [],
            "aT": [],
            "tT": [],
            "sign": self.url_encode(sign).decode()
        }
        return _tokon

    def get_idPriceDict(self, room_type_list, name, hotelId, start_day, end_date):
        item = {}
        hotel_list = []
        item['hotel_name'] = name
        # item['grade'] = grade
        for room_type in room_type_list:
            item['room_type'] = room_type['goodsName']
            poiId = room_type['goodsRoomModel']['poiId']
            goodsId = room_type['goodsRoomModel']['goodsId']
            partnerId = room_type['goodsRoomModel']['partnerId']
            roomId = room_type['goodsRoomModel']['roomId']
            paraExtInfos = room_type['paraExtInfos']
            avprice = room_type['averagePrice']
            item['price'] = self.getPrice(paraExtInfos, poiId, goodsId, partnerId, roomId, avprice)
            item['rebate'] = '0'
            if name[:4] == "速8酒店":
                item['hotel_id'] = int(hotelId)
                item['rival_id'] = int('0')
            else:
                item['hotel_id'] = int('0')
                item['rival_id'] = int(hotelId)
            item['source'] = "Meituan-美团"
            if room_type['tagName'] != '1':
                item['channel'] = room_type['tagName']
            else:
                item['channel'] = "美团"
            if item['channel'] is None:
                item['channel'] = "美团"
            item['crawlDate'] = str(datetime.date.today())
            item['crawlTime'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            item['breakfast'] = room_type['breakfast']
            content = room_type['goodsBookInfos'][0]['content']
            prod1 = ''
            for c in content:
                prod1 += c['targetName']
            prod = str(item['room_type'])
            p1 = re.compile(r'[[](.*?)[]]', re.S)  # 最小匹配
            prod = re.findall(p1, prod)
            if prod == []:
                item['prod_name'] = prod1
            else:
                item['prod_name'] = prod1 + str(prod)
            can_book = room_type['fullRoomDesc']
            if can_book == "满房":
                item['can_book'] = room_type['fullRoomDesc']
            else:
                item['can_book'] = '预订'
            item['arrDate'] = start_day
            print(item)
            hotel_list.append(deepcopy(item))
        if len(hotel_list) != 0:
            print(hotel_list)
            self.upload(hotel_list)
            self.database().meituan_data.insert(hotel_list)

    def get_mergelist(self, room_type_list, name, hotelId, start_day, end_date):
        item = {}
        hotel_list = []
        item['hotel_name'] = name
        for room_type in room_type_list:
            room_name = room_type['roomCellName']
            aggregateGoods = room_type['aggregateGoods']
            for aggregateGood in aggregateGoods:
                item['room_type'] = room_name + aggregateGood['aggregateGoodName']
                poiId = aggregateGood['prepayGood']['goodsRoomModel']['poiId']
                goodsId = aggregateGood['prepayGood']['goodsRoomModel']['goodsId']
                partnerId = aggregateGood['prepayGood']['goodsRoomModel']['partnerId']
                roomId = aggregateGood['prepayGood']['goodsRoomModel']['roomId']
                paraExtInfos = aggregateGood['prepayGood']['paraExtInfos']
                avprice = aggregateGood['prepayGood']['averagePrice']
                item['price'] = self.getPrice(paraExtInfos, poiId, goodsId, partnerId, roomId, avprice)
                item['rebate'] = '0'
                if name[:4] == "速8酒店":
                    item['hotel_id'] = int(hotelId)
                    item['rival_id'] = int('0')
                else:
                    item['hotel_id'] = int('0')
                    item['rival_id'] = int(hotelId)
                item['source'] = "Meituan-美团"
                if aggregateGood['prepayGood']['tagName'] != '1':
                    item['channel'] = aggregateGood['prepayGood']['tagName']
                else:
                    item['channel'] = "美团"
                if item['channel'] is None:
                    item['channel'] = "美团"
                item['crawlDate'] = str(datetime.date.today())
                item['crawlTime'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                item['breakfast'] = aggregateGood['prepayGood']['breakfast']
                content = aggregateGood['prepayGood']['goodsBookInfos'][0]['content']
                prod1 = ''
                for c in content:
                    prod1 += c['targetName']
                prod = str(item['room_type'])
                p1 = re.compile(r'[[](.*?)[]]', re.S)  # 最小匹配
                prod = re.findall(p1, prod)
                if prod == []:
                    item['prod_name'] = prod1
                else:
                    item['prod_name'] = prod1 + str(prod)
                can_book = aggregateGood['prepayGood']['fullRoomDesc']
                if can_book == "满房":
                    item['can_book'] = aggregateGood['prepayGood']['fullRoomDesc']
                else:
                    item['can_book'] = '预订'
                item['arrDate'] = start_day
                print(item)
                hotel_list.append(deepcopy(item))
        if len(hotel_list) != 0:
            print(hotel_list)
            self.upload(hotel_list)
            self.database().meituan_data.insert(hotel_list)

    def get_cookie(self):
        item = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Referer': 'https://bj.meituan.com/'
        }
        url = 'https://i.meituan.com'
        while 1:
            try:
                response = requests.get(url, proxies=self.proxies, headers=headers, timeout=5)
                break
            except:
                pass
        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        for i in cookies:
            item[i] = cookies[i]
        return item

    def getPrice(self, paraExtInfos, poiId, goodsId, partnerId, roomId, averagePrice):
        # 获取房间的token
        cookies = [
            '_lxsdk_cuid=16e152bc9ffc8-0a20f5888339d2-5373e62-100200-16e152bca00c8; iuuid=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; _hc.v=e30873cc-c29b-660a-be71-2aa3c59beff6.1572488944; __utmz=74597006.1573197642.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); wm_order_channel=mtib; utm_source=60030; IJSESSIONID=1kxlxjtx67dbty97akhm4z868; uuid=f1f10f58b2bf4ab58b5d.1574389747.1.0.0',
            '__mta=140828301.1574392900264.1574392900264.1574392900264.1; hotel_city_id=1; hotel_city_info=%7B%22id%22%3A1%2C%22name%22%3A%22%E5%8C%97%E4%BA%AC%22%2C%22pinyin%22%3A%22beijing%22%7D; IJSESSIONID=1r5s36ug6s0ch1i4swi1zmrebt; iuuid=EA07BD4DD1505FFE82AC2E88100D97D78C10B9ECBB29422F234458842CD4A6DF; latlng=40.024116%2C116.287429%2C1574392967083; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk_cuid=16e9121280790-0788a1ac14cc37-5373e62-100200-16e91212808a9; _lxsdk=EA07BD4DD1505FFE82AC2E88100D97D78C10B9ECBB29422F234458842CD4A6DF; uuid=21e40ba4b2f9441cbb6f.1574392967.1.0.0; _lxsdk_s=16e91212466-20a-791-77d%7C%7C3',
            '__mta=107238845.1574392979892.1574392979892.1574393002079.2; hotel_city_id=1; hotel_city_info=%7B%22id%22%3A1%2C%22name%22%3A%22%E5%8C%97%E4%BA%AC%22%2C%22pinyin%22%3A%22beijing%22%7D; IJSESSIONID=rbpegd3mu6vilt2vbq70oy0r; iuuid=FE9DB3A58AD40C90B4AC9E61C6C56355287A2038BC74162F3FE25B57EC7EDAFF; latlng=40.024116%2C116.287429%2C1574393046585; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk_cuid=16e91225f047f-093d03c3e12f4c-5373e62-100200-16e91225f055c; _lxsdk=FE9DB3A58AD40C90B4AC9E61C6C56355287A2038BC74162F3FE25B57EC7EDAFF; uuid=6257a5d777b448e3a866.1574393047.1.0.0; _lxsdk_s=16e91225a39-a6f-56e-7ae%7C%7C5',
            '_lxsdk_cuid=16e152bc9ffc8-0a20f5888339d2-5373e62-100200-16e152bca00c8; iuuid=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; _hc.v=e30873cc-c29b-660a-be71-2aa3c59beff6.1572488944; __utmz=74597006.1573197642.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); wm_order_channel=mtib; utm_source=60030; uuid=5ce08a0d824b48dba6ee.1573441385.1.0.0; IJSESSIONID=kc14zxvbjz6uyxuur37rlaei; _lxsdk_s=16e63bf8dca-715-ce6-8cc%7C%7C4',

        ]
        cookie = self.get_cookie()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'ihotel.meituan.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': '_lxsdk_cuid=16e152bc9ffc8-0a20f5888339d2-5373e62-100200-16e152bca00c8; wm_order_channel=default; iuuid={}; ci={}; cityname={}; _lxsdk=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; mtcdn=K; IJSESSIONID={}; uuid={}; ndr=i.meituan.com; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic'.format(cookie['iuuid'], cookie['ci'], cookie['cityname'], cookie['IJSESSIONID'], cookie['iuuid']),
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
        }
        while True:
            uuid = self.get_uuid()
            infotoken = self.get_infotoken(uuid)
            infourl = 'https://ihotel.meituan.com/productapi/v2/prepayGoodDetail?userid=&' \
                      '_token={}&checkInDate={}&checkOutDate={}&noPersistent=0&abTest=a&cityId=undefined&clientType=WEIXINPROGRAM&clientVersion=9.14.800&utm_medium=WEIXINPROGRAM&version_name=9.14.800&uuid={}&' \
                      'goodsId={}&goodsType=1' \
                      '&partnerId={}' \
                      '&poiId={}' \
                      '&roomId={}&userId=&utm_campaign=AgroupBentry%253DMTHotel_scene%253D1089&openId=odPDr0N6p3m8MAZM-h960Y7BAejU&antiRepPlatform=Android&wechatVersion=7.0.8&sdkVersion=8.7.0&antiRepCityId=1&antiRepLocateCityId=1&lat=40.032038&lng=116.305609&programName=hotel&fromOffline=false' \
                      '&paraExtInfos={}'.format(infotoken, self.taken["start"], self.taken["end"], self.taken["uuid"], goodsId, partnerId, poiId, roomId, paraExtInfos)
            while 1:
                try:
                    rep = requests.get(url=infourl, headers=headers, proxies=self.proxies, timeout=3)
                    # print(rep.status_code)
                    infodata = json.loads(rep.text)
                    price = infodata['goodsBaseInfo']['sellPrice']
                    break
                except:
                    print('--------')
            if int(str(averagePrice)[:3]) != int(price):
                return price
            else:
                pass
                # print("ip:" + str(proxies) + "价格错误")

    def spider(self, data_url, taken, hotelId, start_day, end_date):
        cookie = self.get_cookie()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'ihotel.meituan.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            # 'Cookie': cookies[random.randint(0, 3)],
            'Cookie': '_lxsdk_cuid=16e152bc9ffc8-0a20f5888339d2-5373e62-100200-16e152bca00c8; wm_order_channel=default; iuuid={}; ci={}; cityname={}; _lxsdk=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; mtcdn=K; IJSESSIONID={}; uuid={}; ndr=i.meituan.com; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic'.format(cookie['iuuid'], cookie['ci'], cookie['cityname'], cookie['IJSESSIONID'], cookie['iuuid']),
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        }
        i = 0
        while i < 8:
            try:
                response = requests.get(url=data_url, headers=headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
                # print(response.status_code)
                data = json.loads(response.text)
                break
            except:
                i += 1
        if response.status_code == 200:
            print('getlist:success')
            name = taken['name']
            if data['goodsList'] is None:
                room_type_list = jsonpath.jsonpath(data, '$.mergeList.data')[0]
                return self.get_mergelist(room_type_list, name, hotelId, start_day, end_date)
            else:
                room_type_list = jsonpath.jsonpath(data, '$.goodsList.data')[0]
                return self.get_idPriceDict(room_type_list, name, hotelId, start_day, end_date)
        else:
            return []

    def upload(self, hotel_list):
        url = 'http://114.55.84.165:8081/api/super8/saveHotelData'
        headers2 = {'Content-Type': 'application/json',
                    'Connection': 'close'}
        r = requests.post(url, headers=headers2, json=hotel_list)
        print(r.text)

    def database(self):
        client = MongoClient('localhost', 27017)
        db_name = 'su8'
        db = client[db_name]
        return db

    def get_crawtime(self, i):
        today = datetime.date.today()
        oneday = datetime.timedelta(days=i)
        enday = datetime.timedelta(days=i + 1)
        start_day = str(today + oneday)
        end_date = str(today + enday)
        return start_day, end_date

    def run(self):
        i = self.day
        db = self.database()
        urlList = db.meituan_url.find(no_cursor_timeout=True)
        start_day, end_date = self.get_crawtime(i)
        j = 0
        for hotel in urlList:
            j += 1
            print(self.thread_id + str(j))
            hotelId = int(hotel['hotelId'])
            ordUrl = re.sub(r'\?(.*)?$', '', hotel['hotelUrl'])
            hotel_id = ''.join(re.findall(r"\d+", ordUrl))
            if hotel_id != '':
                url = 'https://hotel.meituan.com/{id}/?ci={starttime}&co={endtime}'.format(id=hotel_id, starttime=start_day, endtime=end_date)
                self.taken = self.get_taken(url)
                if self.taken is not None:
                    _tokon = self.get_tokon()
                    token = self.url_encode(_tokon).decode()
                    data_url = 'https://ihotel.meituan.com/productapi/v2/prepayList?&_token={}&end={}&start={}&poiId={}&uuid={}&type=1&utm_medium=baiduProgram&version_name=8.7.0'.format(
                        token, self.taken["end"], self.taken["start"], self.taken["poiId"], self.taken["uuid"])
                    # print(data_url)
                    hotel_list = self.spider(data_url, self.taken, hotelId, start_day, end_date)  # 爬虫主程序


if __name__ == '__main__':
    t1 = MeiTuan(1, 'thread1')
    t2 = MeiTuan(2, 'thread2')
    t3 = MeiTuan(3, 'thread3')
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
