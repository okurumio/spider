# -*- coding: utf-8 -*-
import pymongo
from byne_tb import config
import requests
import json
import hashlib

client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]  # 获得数据库的句柄
db.authenticate("root", "e19ee8c4")
coll = db["dsManualData5"]  # 店铺数据集合
coll1 = db["dsManualData6"]  # 商品数据集合

headers = {
    "cookie": config.cookie,  # cookies最好是搜索本关键词的cookies
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
}


# md5加密
def Md5(_id):
    sign = hashlib.md5()
    sign.update(_id.encode())
    signs = sign.hexdigest()
    return signs


def start_requests():
    # 只抓淘宝搜索关键词的商品列表数据
    datas = coll.find({"platformType": 2})
    print(datas.count())
    for item in datas:
        if item['page'] * 44 >= item['count']:
            # 满足条件
            continue
        elif item['page'] > 100:
            # 满足条件
            continue
        else:
            get_url(item)


def get_url(item):
    success = False
    while not success:
        url = "https://s.taobao.com/search?ajax=true&q={0}&sort=sale-desc&s={1}".format(item["column"], (item["page"] - 1) * 44)
        x = 0
        while x < 20:
            r = requests.get(url, headers=headers)
            if "rgv587_flag" not in r.text:
                goodsDatas = json.loads(r.text)
                content(goodsDatas, item)
                coll.update({"column": item['column'], 'platformType': 2}, {'$set': {'page': item['page']+1}})
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
    if item['page'] * 44 >= item['count']:
        # 满足条件
        print("已翻至最后一页")
    elif item['page'] >= 100:
        # 满足条件
        print("已翻至最后一页")
    else:
        item["page"] = item["page"] + 1
        print("*" * 50, "翻至第{}页".format(item["page"]))
        get_url(item)


def content(goodsDatas, item):
    # 解析请求成功的response
    goodsList = goodsDatas["mods"]["itemlist"]["data"]["auctions"]
    for goods in goodsList:
        if "tmall.com" in goods["detail_url"]:
            continue
        item['productName'] = goods["raw_title"]  # 商品名称
        item['shopName'] = item['column']  # 店铺名称
        if '套房' in item['productName'] or '短租' in item['productName'] \
                or '民宿' in item['productName'] or '度假村' in item['productName'] or '酒店' in item[
            'productName'] \
                or '公寓' in item['productName'] or '人房' in item['productName'] or '家庭房' in item[
            'productName'] \
                or '客房' in item['productName'] or '旅馆' in item[
            'productName'] \
                or 'Travelodge' in item['productName'] or '宾馆' in item['productName'] or '饭店' in item['productName']:
            continue  # 跳过不抓取的链接
        item['productId'] = goods['nid']  # 商品id
        item['pageUrl'] = "https://item.taobao.com/item.htm?id={}".format(item['productId'])  # 商品url
        item['page_url'] = item['pageUrl']
        item['keyword'] = item['column']
        item.pop('_id')
        _id = item['pageUrl'] + item['keyword']
        item["_id"] = Md5(_id)
        data = {'page': item['page'], 'keyword': item['keyword'], 'productName': item['productName'],
         'productId': item['productId'], 'pageUrl': item['pageUrl'],
         'platform': item['platform'], 'platformType': item['platformType'], 'createTime': item['createTime'],
        '_id': item["_id"], 'brand': ''}
        coll1.save(data)
        print(data)


if __name__ == "__main__":
    start_requests()

# item = {'page': data['page'], 'keyword': data['keyword'], 'productName': data['productName'],
        #  'productId': data['productId'], 'pageUrl': data['pageUrl'],
        #  'platform': data['platform'], 'platformType': data['platformType'], 'createTime': data['createTime'],
        # '_id': data["_id"], 'brand': ''}