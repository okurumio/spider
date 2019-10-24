import pymongo
from urllib import parse as parse_url
import requests
from scrapy import Selector
import time
from fake_useragent import UserAgent
from byne_tb import config
import random
import hashlib
import re


client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]
db.authenticate("root", "e19ee8c4")
coll = db["dsManualData5"]  # 店铺数据集合
coll1 = db["dsManualData6"]  # 商品数据集合

createTime = int(time.time())


def Md5(_id):
    sign = hashlib.md5()
    sign.update(_id.encode())
    signs = sign.hexdigest()
    return signs


def good_list():
    datas = coll.find({"max_page": {"$exists": False}, "platformType": 2, "type": 1})
    print(datas.count())
    for item in datas:
        print(item)
        if (item["page"] - 1) * 24 >= item["count"]:
            continue
        topic(item)


def topic(item):
    ua = UserAgent()
    headers = {
        "accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        'cookie': config.cookie,
        "referer": item["url"],
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ua.random,
        "x-requested-with": "XMLHttpRequest"
    }
    shop_list_url = parse_url.urljoin(item["url"],
            "/i/asynSearch.htm?callback=jsonp146&input_charset=gbk&mid=w-{0}-0&wid={1}&path=/search.htm&search=y&pageNo={2}".format(
            item["data_widgetid"], item["data_widgetid"], item["page"]))
    while 1:
        res = requests.get(shop_list_url, headers=headers)
        time_num = random.randint(1, 5)  # 生成随机时间
        time.sleep(time_num)
        print(shop_list_url)
        if "rgv587_flag" not in res.text:
            sel = Selector(text=res.text)
            goods_list = sel.xpath("//div[contains(@class,'item3line1')]/dl")
            for good_info in goods_list:
                productName = good_info.css("dd[class*=detail] a::text").extract_first().strip()
                item["productName"] = productName
                if '套房' in item['productName'] or '短租' in item['productName'] or '高清实' in item['productName'] \
                        or '民宿' in item['productName'] or '度假村' in item['productName'] or '酒店' in item[
                    'productName'] or '日出房' in item['productName'] \
                        or '公寓' in item['productName'] or '人房' in item['productName'] or '家庭房' in item[
                    'productName'] or '地图' in item['productName'] or '高清实拍' in item['productName'] \
                        or '客房' in item['productName'] or '旅馆' in item[
                    'productName'] or '视频素材' in item['productName'] or '图片素材' in item['productName'] \
                        or 'Travelodge' in item['productName'] or '宾馆' in item['productName'] or '饭店' in item[
                    'productName']:
                    continue
                productId = good_info.css("::attr(data-id)").extract_first()
                productId = re.search("(\d+)", productId).group(1)
                pageUrl = "https://item.taobao.com/item.htm?id=" + str(productId)

                item['pageUrl'] = pageUrl
                item["shopName"] = item["column"]
                item["productId"] = productId
                item["keyword"] = item["column"]
                item.pop('_id')
                _id = item['pageUrl'] + item['keyword']
                item["_id"] = Md5(_id)
                item.pop('createTime')
                item["createTime"] = createTime
                item["brand"] = ""
                coll1.save(item)
                print(item)
            coll.update({"_id": item["_id"]}, {"$set": {"page": item["page"] + 1}})
            break
        else:
            print("手动解除验证，并更换验证之后的cookie")
            config.cookie = input("输入更新的cookie")
    if item["page"] * 24 >= item["count"]:
        print("翻至最后一页")
    else:
        item["page"] = item["page"] + 1
        print("跳转到下一页，页码:{}".format(item["page"]))
        topic(item)


if __name__ == "__main__":
    good_list()