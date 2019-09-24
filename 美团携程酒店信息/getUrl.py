import requests
import json
import pymongo
from su8 import connRedis


def urlGet():
    db.ctrip_url.drop()
    collection = db['ctrip_url']
    url = 'http://114.55.84.165:8081/api/super8/getHotelUrlInfo'
    res = requests.get(url,)
    res.encoding = 'utf-8'
    res = json.loads(res.text.strip('var data='))
    for i in range(1115):
        ctripUrl = res['data'][i]['super8HotelInfo']['ctripUrl']
        elongUrl = res['data'][i]['super8HotelInfo']['elongUrl']
        hotelId = res['data'][i]['super8HotelInfo']['hotelId']
        hotelName = res['data'][i]['super8HotelInfo']['hotelName']
        meituanUrl = res['data'][i]['super8HotelInfo']['meituanUrl']
        collection.insert({"hotelName": hotelName, "hotelId": hotelId, "ctripUrl": ctripUrl, "elongUrl": elongUrl, "meituanUrl": meituanUrl})
        hotelId = res['data'][i]['rivals']
        for j in hotelId:
            hotelName = j["hotelName"]
            hotelId = j["hotelId"]
            ctripUrl = j["ctripUrl"]
            elongUrl = j["elongUrl"]
            meituanUrl = j["meituanUrl"]
            collection.insert({"hotelName": hotelName, "hotelId": hotelId, "ctripUrl": ctripUrl, "elongUrl": elongUrl,
                           "meituanUrl": meituanUrl})


def urlClean():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Connection": "close",
    }
    db.meituan_url.drop()
    meituan = db['meituan_url']
    hotellist = db.ctrip_url.find(no_cursor_timeout=True)
    for hotel in hotellist:
        url = hotel['meituanUrl']
        if url is not None:
            i = 0
            while i < 5:
                try:
                    response = requests.get(url, headers=headers, proxies={'http': conn.randomOneIp('proxy:new_ip_list')}, timeout=3).text
                    break
                except:
                    i += 1
            errorResponse = '<meta http-equiv="refresh" content="0; url=http://www.meituan.com/error/" />'
            if response != errorResponse:
                print("success")
                hotelName = hotel['hotelName']
                hotelId = hotel['hotelId']
                meituan.insert({'hotelName': hotelName, 'hotelId': hotelId, 'hotelUrl': url})


if __name__ == '__main__':
    conn = pymongo.MongoClient('localhost', 27017)
    db = conn.su8
    conn = connRedis.OPRedis()
    # urlGet()
    urlClean()
