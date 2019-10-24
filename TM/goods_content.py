from TM.goods_comment import GoodsComment
import hashlib
from database import Mongo
import requests
import connRedis
import time
import json
import re


class GoodsContent:
    def __init__(self):
        db_name = 'bayan'
        self.collection_name = 'TMGoodsUrl'
        self.save_collection_name = 'TMGoodsData'
        self.db = Mongo(db_name)
        self.conn = connRedis.OPRedis()

    def get(self, item):
        goods_id = re.findall(r'id=(\d+)', item['pageUrl'])
        item['pageUrl'] = 'https://detail.tmall.com/item.htm?id={}'.format(goods_id[0])
        item['_id'] = urlmd5(item['pageUrl'] + item['keyword'])
        item['productId'] = int(goods_id[0])
        item['custom'] = 2  # 平台
        item['platformType'] = 2
        url = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{}%22%7D'.format(goods_id[0])
        response = requests.get(url)
        print(response.url)
        data = json.loads(response.text)['data']
        dataitem = data['item']
        dataprops = data['props']
        apiStack = json.loads(data['apiStack'][0]['value'])
        try:
            item['productParam'] = dataprops['groupProps'][0]['基本信息'][12]['食品口味']  # 商品规格
        except:
            item['productParam'] = ''
        item['currentPrice'] = apiStack['price']['price']['priceText']
        try:
            item['originalPrice'] = apiStack['price']['extraPrices'][0]['priceText']  # 原价
        except IndexError as e:
            try:
                item['originalPrice'] = apiStack['price']['transmitPrice']['priceText']
            except:
                item['originalPrice'] = item['current_price']
        except KeyError as e:
            try:
                item['originalPrice'] = apiStack['price']['transmitPrice']['priceText']
            except:
                item['originalPrice'] = item['current_price']
        try:
            item['salesNumMonth'] = int(apiStack['item']['sellCount'])  # 月销量
        except:
            item['salesNumMonth'] = 0
        item['servicePromise'] = ''  # 服务承诺
        servicePromise = apiStack['consumerProtection']['items']
        for prom in servicePromise:
            item['servicePromise'] += prom['title'] + ' '
        item['paymentInformation'] = '信用卡快捷支付蚂蚁花呗余额宝'  # 支付方式
        item['stockNum'] = int(apiStack['skuCore']['sku2info']['0']['quantity'])  # 库存
        if item['stockNum']:
            item['stock'] = '有货'
        else:
            item['stock'] = '无货'
        item['shopName'] = data['seller']['shopName']  # 店铺名称
        item['shopUrl'] = "https://shop{}.taobao.com".format(data['seller']['shopId'])  # 店铺链接
        item['shopId'] = data['seller']['shopId']
        item['shopScore'] = []  # 店铺评分
        for shop in data['seller']['evaluates']:
            item['shopScore'].append(shop['title'])
            item['shopScore'].append(shop['score'])
        item['commentsCount'] = dataitem['commentCount']  # 评论数量
        item['collectionNum'] = dataitem['favcount']  # 收藏数量
        item['departureAddress'] = apiStack['delivery']['from']  # 发货地

        item['promotion'] = ''  # 商品促销信息
        try:
            shopProm = apiStack['price']['shopProm']
        except:
            shopProm = []
        for prom in shopProm:
            for con in prom['content']:
                if '登录' in con:
                    pass
                else:
                    item['promotion'] += con + ','
        try:
            pram = apiStack['consumerProtection']['channel']['title']  # 是否聚划算 商品
        except:
            pram = ''
        item['promotion'] += pram

        item['crawlTime'] = int(time.time() * 1000)
        craw_date = time.localtime(item['crawlTime'] / 1000)
        craw_date = time.strftime("%Y-%m-%d", craw_date)
        url = item['shopId'] + str(item['productId']) + craw_date + item['platform']
        item['connectGoodsId'] = urlmd5(url)

        item['productSkuDetail'] = []  # 商品sku 详情
        try:
            skuprops = data['skuBase']['props']
        except KeyError as e:
            skuprops = []
        try:
            sku2info = data['skuBase']['skus']
        except KeyError as e:
            sku2info = []
        for sku2 in sku2info:
            sku_price = apiStack['skuCore']['sku2info'][sku2['skuId']]['price']['priceText']
            sku_stock = apiStack['skuCore']['sku2info'][sku2['skuId']]['quantity']
            propPath = sku2['propPath'].split(";")[-1].split(":")
            for prop in skuprops:
                if prop['pid'] == propPath[0]:
                    for col in prop['values']:
                        if col['vid'] == propPath[1]:
                            sku_name = col['name']
                            item['productParam'] += sku_name + ' '
                            item['productSkuDetail'].append(
                                {'sku_id': sku2['skuId'], 'sku_name': sku_name, 'sku_price': sku_price,
                                 'sku_stock': sku_stock})
        comments, crawlCommentsTime = GoodsComment().get(item, 1)
        item['commentsData'] = comments
        item['crawlCommentsCount'] = len(comments)
        print('评论数：' + str(len(comments)))
        item['crawlCommentsTime'] = crawlCommentsTime
        print(item)

    def run(self):
        i = 0
        items = self.db.get(self.collection_name)
        for item in items:
            print(i)
            goodsitem = self.get(item)
            self.db.insert(self.save_collection_name, goodsitem)
            i += 1


def urlmd5(url):
    sign = hashlib.md5()  # 创建md5对象
    sign.update(url.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
    signs = sign.hexdigest()  # 加密
    return signs


if __name__ == '__main__':
    GoodsContent().run()
