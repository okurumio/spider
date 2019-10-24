import requests, zlib, base64
import random, re
import json, jsonpath
from pymongo import *
import datetime, time
from bs4 import BeautifulSoup
from su8 import connRedis
from copy import deepcopy


def getTime():
    d1 = datetime.datetime(1970, 1, 1)
    d2 = datetime.datetime.now()
    d3 = int((d2 - d1).total_seconds() * 1000)
    return d3


def url_encode(data, stringify=False):
    if (stringify == True):
        base_data = zlib.compress(data.encode())
        data = base64.b64encode(base_data)
        return data
    else:
        data = json.dumps(data).replace(' ', "")
        return url_encode(data, True)


def url_decode(data):
    """token解码"""
    if isinstance(data, str):
        data = base64.b64decode(data)
        base_data = zlib.decompress(data)
        return base_data


def get_taken(url):
    # 访问酒店链接，从响应体里得到需要的参数信息
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Connection": "close",
    }
    cookies_iuuid = [
        '93AB5D4FEB3D1BFFF9B7727E5ECE71CF13A51383CD6ADB169C43832A6BB41843',
        '8A8E20A923D42E033BC3505E3460BCC25AEA4D933CE3F233B19679BB0EEC89D4',
        'C68174784AF5C11CC2F127774CC8BA60FB5E766509A7DCA8F4ECDFF59B45076F',
        '850C1A14A798DC5834EEF2177EAAA430A8958DBE0813C5FAE858B61834D1F95D'
    ]
    i = 0
    conn = connRedis.OPRedis()
    while i < 5:
        try:
            response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')},timeout=3)
            break
        except:
            i += 1
            response = ''
    if response != '':
        # grade = ''
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        taken = {}
        if soup.select('.fs26.fc3.pull-left.bold') != []:
            taken["name"] = soup.select('.fs26.fc3.pull-left.bold')[0].text
            if re.findall(r'cityId=[0-9]*', response.text) == []:
                return None
            taken["cityId"] = re.findall(r'cityId=[0-9]*', response.text)[0][7:]
            taken["poiId"] = re.findall(r'"poiId":[0-9]*', response.text)[0][8:]
            taken["start"] = re.findall(r'"queryStart":[0-9]*', response.text)[0][13:]
            taken["end"] = re.findall(r'"queryEnd":[0-9]*', response.text)[0][11:]
            taken["?type"] = "1"
            taken["&utm_medium"] = "baiduProgram" # baiduProgram
            taken["version_name"] = "8.7.0"
            taken["uuid"] = cookies_iuuid[random.randint(0, 3)]
            # grade = soup.find(class_='score-color').string
            # if grade is not None:
            #     grade = grade.string
            return taken


def get_tokon(taken):
    # 生成sign的值，并得到_token字典
    sign = '"&userid=2643733635end=%s&poiId=%s&start=%s&type=1&utm_medium=baiduProgram&uuid=%s&version_name=%s"' % (
        taken['end'], taken['poiId'], taken['start'], taken['uuid'], taken['version_name'])
    _tokon = {
        "rId": 100051,
        "ts": getTime(),
        "cts": getTime() + 356,
        "brVD": [1536, 222],
        "brR": [[1536, 864], [1536, 824], 24, 24],
        "bI": ["%s" % url, ""],
        "mT": [],
        "kT": [],
        "aT": [],
        "tT": [],
        "sign": url_encode(sign).decode()
    }
    return _tokon


def get_idPriceDict(room_type_list, name, hotelId, start_day, end_date):
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
        item['price'] = getPrice(start_day, end_date, poiId, goodsId, partnerId, roomId)
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
    return hotel_list


def get_mergelist(room_type_list, name, hotelId, start_day, end_date):
    item = {}
    hotel_list = []
    item['hotel_name'] = name
    # item['grade'] = grade
    for room_type in room_type_list:
        room_name = room_type['roomCellName']
        aggregateGoods = room_type['aggregateGoods']
        for aggregateGood in aggregateGoods:
            item['room_type'] = room_name + aggregateGood['aggregateGoodName']
            poiId = aggregateGood['prepayGood']['goodsRoomModel']['poiId']
            goodsId = aggregateGood['prepayGood']['goodsRoomModel']['goodsId']
            partnerId = aggregateGood['prepayGood']['goodsRoomModel']['partnerId']
            roomId = aggregateGood['prepayGood']['goodsRoomModel']['roomId']
            item['price'] = getPrice(start_day, end_date, poiId, goodsId, partnerId, roomId)
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
    return hotel_list


def getPrice(starttime, endtime, poiId, goodsId, partnerId, roomId):
    conn = connRedis.OPRedis()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    url = 'https://hotel.meituan.com/buy/?ci={}&co={}&bizType=1&poiId={}&goodsId={}&partnerId={}&roomId={}'.format(starttime, endtime, poiId, goodsId, partnerId, roomId)
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=3, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}).text
            pattern = re.compile('window.__INITIAL_STATE__=(.*);')
            a = pattern.findall(response)
            data = json.loads(a[0])
            break
        except:
            print('重新获取价格')
    price = data['product']['goodsDetail']['sellPrice']
    return price


def spider(data_url, taken, hotelId, start_day, end_date):
    conn = connRedis.OPRedis()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        "Connection": "close",
        'Cookie': '_lxsdk_cuid=16c741eec0743-0825c4778187ad-7373e61-100200-16c741eec08c8; iuuid=1A20860165EF079A6A4BE8C172F8167C7F0F48F3BD83C562BBD0AB6757B294EC; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk=1A20860165EF079A6A4BE8C172F8167C7F0F48F3BD83C562BBD0AB6757B294EC; mtcdn=K; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; lsu=; __utma=74597006.1522365605.1565753550.1565753550.1565753550.1; __utmz=74597006.1565753550.1.1.utmcsr=csdn.net|utmccn=(referral)|utmcmd=referral|utmcct=/link/; a2h=1; latlng=40.032556,116.305586,1565754410475; i_extend=C_b1Gimthomepagecategory120__xhotelhomepage__yselect__zday; uuid=77fab03e4e50451da595.1565835057.1.0.0; IJSESSIONID=cbp27d7jnvkdjy8546psfco1; _lxsdk_s=16c946c25b7-d3c-379-aad%7C%7C13',
        'Host': 'ihotel.meituan.com',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 swan/2.9.0 swan-baiduboxapp/11.12.0.18 baiduboxapp/11.12.0.18 (Baidu; P2 12.4)',
    }
    i = 0
    while i < 5:
        try:
            response = requests.get(url=data_url, headers=headers, proxies={'http': conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
            break
        except:
            i += 1
    response = json.loads(response.text)
    name = taken['name']
    print(response['goodsList'])
    if response['goodsList'] is None:
        room_type_list = jsonpath.jsonpath(response, '$.mergeList.data')[0]
        return get_mergelist(room_type_list, name, hotelId, start_day, end_date)
    else:
        room_type_list = jsonpath.jsonpath(response, '$.goodsList.data')[0]
        return get_idPriceDict(room_type_list, name, hotelId, start_day, end_date)


def upload(hotel_list):
    url = 'http://114.55.84.165:8081/api/super8/saveHotelData'
    headers2 = {'Content-Type': 'application/json',
                'Connection': 'close'}
    r = requests.post(url, headers=headers2, json=hotel_list)
    print(r.text)


def database():
    client = MongoClient('localhost', 27017)
    db_name = 'su8'
    db = client[db_name]
    return db


def get_crawtime(i):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=i)
    enday = datetime.timedelta(days=i + 1)
    start_day = str(today + oneday)
    end_date = str(today + enday)
    return start_day, end_date


if __name__ == '__main__':
    db = database()
    urlList = db.meituan_url.find(no_cursor_timeout=True)
    for i in range(1, 2):
        start_day, end_date = get_crawtime(i)
        j = 0
        for hotel in urlList:
            j += 1
            print(j)
            hotelId = int(hotel['hotelId'])
            ordUrl = re.sub(r'\?(.*)?$', '', hotel['hotelUrl'])
            hotel_id = ''.join(re.findall(r"\d+", ordUrl))
            if hotel_id != '':
                url = 'https://hotel.meituan.com/{id}/?ci={starttime}&co={endtime}'.format(id=hotel_id, starttime=start_day, endtime=end_date)
                print(url)
                taken = get_taken(url)
                if taken is not None:
                    _tokon = get_tokon(taken)
                    __token = url_encode(_tokon).decode()
                    data_url = "http://ihotel.meituan.com/productapi/v2/prepayList?&_token=" + __token + "&userid=2643733635&type=1&utm_medium=baiduProgram&version_name=8.7.0&poiId=" + \
                               taken["poiId"] + "&start=" + taken["start"] + "&end=" + taken["end"] + "&uuid=" + taken["uuid"]
                    print(data_url)
                    hotel_list = spider(data_url, taken, hotelId, start_day, end_date)  # 爬虫主程序
                    if len(hotel_list) != 0:
                        print(hotel_list)
                        upload(hotel_list)
                        db.meituan_data.insert(hotel_list)
