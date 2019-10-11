import requests
from tianmao.common import connRedis
import json
import hashlib
from copy import deepcopy
from pymongo import *
from urllib.request import quote
import time


def run(page, key):
    item = {}
    a = []
    conn = connRedis.OPRedis()
    headers = {
        'referer': 'https://list.tmall.com/search_product.htm?q=%C6%A1%BE%C6&type=p&spm=a220m.8599659.a2227oh.d100&from=mallfp..m_1_searchbutton&searchType=default&sort=d',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        "Connection": "close",
    }
    url = 'https://list.tmall.com/m/search_items.htm?page_size=60&page_no={}&q={}&type=p&spm=a220m.8599659.a2227oh.d100&from=mallfp..m_1_searchbutton&searchType=default&sort=d'.format(page, quote(key, encoding="gbk"))
    response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}).text
    data = json.loads(response)
    lists = data['item']
    for list in lists:
        item['title'] = list['title']
        item['productId'] = list['item_id']
        item['url'] = 'https://detail.tmall.com/item.htm?id=' + str(item['productId'])
        a.append(deepcopy(item))
    return a



def urlmd5(url):
    """
    图片链接md5加密
    :param img_url: 图片链接
    :return: md5字符串　
    """
    sign = hashlib.md5()  # 创建md5对象
    sign.update(url.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
    signs = sign.hexdigest()  # 加密
    return signs


if __name__ == '__main__':
    client = MongoClient('192.168.0.12', 40000)
    db = client['node']
    db.authenticate("root", "e19ee8c4")
    keys = ['啤酒', '大米', '矿泉水', '纯净水']
    time = int(time.time())
    count = 0
    for i in range(2):
        for key in keys:
            idlists = run(i+1, key)
            for j in idlists:
                id = urlmd5(str(j['url']) + key)

                oldid = db.hrGoodsData.find_one({'_id': id})
                if oldid is None:
                    db.hrGoodsData.insert({'_id': id, 'productId': j['productId'], 'pageUrl': j['url'], 'keyword': key, 'createTime': time, 'platformType': 1, 'productName': j['title'], 'platform': '天猫', 'brand': ''})
                    count += 1
                    print(count)

