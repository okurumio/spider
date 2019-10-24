# -*- coding: utf-8 -*-
import pymongo
from urllib import parse as parse_url
import requests
from scrapy import Selector
import time
from fake_useragent import UserAgent
from byne_tb import config
import random


client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate("root", "e19ee8c4")
coll = db["dsManualData5"]


def shop_info():
    datas = coll.find({"count": {"$exists": False}, "platformType": 2, "type": 1})
    print("*" * 30, datas.count())
    for data in datas:
        print(data)
        url = data["url"]
        res = requests.get(url)
        sel = Selector(text=res.text)
        shop_id = sel.css("div#LineZing::attr(shopid)").extract_first()
        data_widgetid = sel.css('div[data-title="宝贝列表"]::attr(data-widgetid)').extract_first()
        data["shopId"] = shop_id
        data["data_widgetid"] = data_widgetid
        data["page"] = 1
        good_count(data)


def good_count(data):
    ua = UserAgent()
    headers = {
        "accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        'cookie': config.cookie,
        "referer": data["url"],
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua.random,
        "x-requested-with": "XMLHttpRequest"
    }
    shop_list_url = parse_url.urljoin(data["url"], "/i/asynSearch.htm?callback=jsonp146&input_charset=gbk&mid=w-{0}-0&wid={1}&path=/search.htm&search=y".format(data["data_widgetid"], data["data_widgetid"]))
    while 1:
        res = requests.get(shop_list_url, headers=headers)
        time_num = random.randint(1, 5)  # 生成随机时间
        time.sleep(time_num)
        print(shop_list_url)
        if "rgv587_flag" not in res.text:
            sel = Selector(text=res.text)
            goods_count = sel.css("div[class*='search-result'] span::text").extract_first().strip()
            data["count"] = int(goods_count)
            print(data)
            coll.update({"_id": data["_id"]}, {"$set": {"shopId": data["shopId"], "data_widgetid": data["data_widgetid"], "page": data["page"], "count": data["count"]}})
            break
        else:
            print("手动解除验证，并更换验证之后的cookie")
            config.cookie = input("输入更新的cookie")


if __name__ == "__main__":
    shop_info()