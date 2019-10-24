# -*- coding: utf-8 -*-
import pymongo
import requests
import json
from byne_tb import config

client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate("root", "e19ee8c4")
coll = db["dsManualData5"]

headers = {
    "cookie": config.cookie,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
}


def start_requests():
    #只抓淘宝搜索关键词的数据
    datas = coll.find({'count': {'$exists': False}, "platformType": 2})
    print(datas.count())
    for data in datas:
        keyword = data['column']
        success = False
        while not success:
            url = "https://s.taobao.com/search?ajax=true&q={}&sort=sale-desc&s=0".format(keyword)
            x = 0
            while x < 20:
                r = requests.get(url, headers=headers)
                # print(r.text)
                if "rgv587_flag" not in r.text:
                    goodsDatas = json.loads(r.text)
                    content(goodsDatas, data)
                    success = True
                    break
                else:
                    x = x + 1
                    print(x)
            if success:
                break
            else:
                print("cookie失效，更换关键词搜素的cookie")
                config.cookie = input("输入关键词搜素更换的cookie")


def content(goodsDatas, data):
    # 解析请求成功的response
    page_num = goodsDatas["mods"]["pager"]["data"]["totalPage"]  # 最大页码
    limit = goodsDatas["mods"]["pager"]["data"]["pageSize"]  # 每页显示的数量
    count = int(page_num) * int(limit)  # 商品总数
    data['count'] = count
    data['page'] = 1  # 初始默认为第一页
    data['shopId'] = data['column']
    coll.update({'_id': data['_id']}, {'$set': {'count': data['count'], 'page': data['page'], 'shopId': data['shopId']}})
    print(data)


if __name__ == "__main__":
    start_requests()