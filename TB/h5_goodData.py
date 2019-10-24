# -*- coding: utf-8 -*-
import pymongo
from copy import deepcopy
import re
import json
import requests
import hashlib
from urllib.parse import urlencode
from byne_tb import config
import time


client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)
db = client[config.MONGO_DB]  # 获得数据库的句柄
db.authenticate("root", "e19ee8c4")
coll = db[config.MONGO_COLL]


def getGoodsData(goodsId, shopId):
    """
    :param shopId:  店铺id/关键词
    :param page: 　页数
    :param types: 搜索类型　1　店铺内商品　2　关键词搜索
    :return:
    """

    goodsDatas = {}
    a = 0
    while a < 3:
        # 默认三次,三次报错退出
        # 上传参数
        datass = {
            "appKey": '12574478',
            "t": '',
            "sign": '',
            'ttid': '600000@taobao_android_7.8.2.50823',
            "api": "mtop.macao.market.activity.applycoupon.querycouponsfordetail",
            "data": ''
        }
        data = '{"detail_v":"3.1.2","from":"detail","pageType":"weex","itemId":"%s","sellerId":"%s","sellerType":"C","ttid":"600000@taobao_android_7.8.2.50823"}' % (goodsId, shopId)
        datass['data'] = data
        url = 'https://h5api.m.tmall.com/h5/mtop.macao.market.activity.applycoupon.querycouponsfordetail/1.0/?'
        t = str(int(time.time()*1000))  # 要转化成字符串
        token = re.search(r'_m_h5_tk=(.+?)_', config.cookie).group(1)
        appkey = datass['appKey']
        datas = token+'&'+t+'&'+appkey+'&'+data
        sign = hashlib.md5()  # 创建md5对象
        sign.update(datas.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
        signs = sign.hexdigest()   # 加密
        datass['t'] = t
        datass['sign'] = signs
        data1 = urlencode(datass)  # 将要传输的数据编码 ，这里有个坑，有一个空格编码不出来，只能想换成2020再替换回来
        data1 = re.sub('\+', '', data1)
        # data1 = data1.replace('2020', '%20')
        data1 = data1.replace('%27', '%22')
        url += data1  # 拼接url
        r = requests.get(url, headers=config.headers)
        goodsDatas = json.loads(r.text)
        if goodsDatas['ret'][0] == "SUCCESS::调用成功":
            break
        else:
            print("cookie失效Error{}更换cookie".format(goodsDatas['ret']))
            config.cookie = input("json商品页面更新cookie")
        a += 1
    return goodsDatas


def goodsDown(item):
    item['stock'] = '已下架'
    item['stock'] = 0
    item['shopScore'] = []
    return item


def start_requests():
    # datas = coll.find({"platformType": 2, 'discount': {'$exists': False}}, no_cursor_timeout=True).limit(10000)
    datas = coll.find({"platformType": 2}, no_cursor_timeout=True).limit(10000)
    print(datas.count())
    for item in datas[500:]:
        print(item)
        url = "http://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{}%22%7D".format(item['productId'])
        # url = "http://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{}%22%7D".format(item['goodsId'])
        res = requests.get(url, headers=config.headers)
        time.sleep(2)
        response = res.text
        content(response, item)


def content(response, item):
    data = json.loads(response)
    item = item
    ret = data['ret'][0]
    if ret == 'SUCCESS::调用成功':
        try:
            data = data["data"]
            dataitem = data['item']
            apiStack = json.loads(data['apiStack'][0]['value'])
        except:
            try:
                redirectUrl = data['trade']['redirectUrl']
                coll.remove({"_id": item['_id']})
                # item = goodsDown(item)
                # yield item
                # print("该商品下架不存在-过期{}".format(item['productId']))
                print("该商品下架不存在-过期{}".format(item['goodsId']))
            except:
                url = "http://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{}%22%7D".format(item['productId'])
                # url = "http://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{}%22%7D".format(item['goodsId'])
                print('链接请求错误:{}'.format(url))
                res = requests.get(url, headers=config.headers)
                response = res.text
                content(response, item)
            return
        try:
            item['departureAddress'] = apiStack['delivery']['from']  # 发货地
        except:
            # 无发货地获取详情页显示地址
            try:
                item['departureAddress'] = apiStack['delivery']['completedTo']  # 发货地
            except:
                item['departureAddress'] = '无'
        item['currentPrice'] = apiStack['price']['price']['priceText']  # 现在的价格
        try:
            item['originalPrice'] = apiStack['price']['extraPrices'][0]['priceText']  # 原价
        except KeyError as e:
            # 无促销价格获取现价
            item['originalPrice'] = apiStack['price']['transmitPrice']['priceText']  # 原价
        except IndexError as e:
            item['originalPrice'] = apiStack['price']['transmitPrice']['priceText']  # 原价
        try:
            item['salesNumMonth'] = int(apiStack['item']['vagueSellCount'])  # 月销量
        except ValueError as e:
            try:
                item['salesNumMonth'] = int(float(apiStack['item']['vagueSellCount'].replace('万+', ''))*10000)
            except:
                item['salesNumMonth'] = int(re.search(r"\d+", apiStack['item']['vagueSellCount']).group(0))
        item['promotion'] = ''  # 商品促销信息
        item['stockNum'] = int(apiStack['skuCore']['sku2info']['0']['quantity'])  # 库存
        if item['stockNum']:
            item['stock'] = '有货'
        else:
            item['stock'] = '无货'
        service = apiStack['consumerProtection']['items']
        item['servicePromise'] = ''  # 承诺服务
        item['paymentInformation'] = ''
        for ser in service:
            try:
                promotionInfos = ser['desc']  # 承诺服务有['desc']
                item['servicePromise'] += ser['title'] + ' '
            except:  # 支付方式无['desc']
                item['paymentInformation'] += ser['title'] + ' '
        categoryId = int(dataitem['rootCategoryId'])  # 商品分类Id
        try:
            categories = db.tmCategoryId.find({'_id': categoryId})[0]['name']
            item['categories'] = categories  # 商品分类
        except:
            item['categories'] = ''  # 商品分类
        item['productName'] = data['item']['title']  # 商品名称
        try:
            item['couponDescription'] = dataitem['subtitle']  # 商品描述
        except KeyError as e:
            item['couponDescription'] = ""
        item['productName'] += item['couponDescription']
        # 商品规格
        item['productParam'] = ''
        item['productSkuDetail'] = []  # 商品sku 详情
        try:
            sku2info = data['skuBase']['skus']
        except KeyError as e:
            sku2info = []
        try:
            skuprops = data['skuBase']['props']
        except KeyError as e:
            skuprops = []
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
        item['cmtStarLevel'] = 0.0  # 淘宝无商品评分
        item['shopName'] = data['seller']['shopName']  # 店铺名称
        item['shopUrl'] = "https://shop{}.taobao.com".format(data['seller']['shopId'])  # 电铺链接
        item['shopId'] = data['seller']['shopId']
        item['userId'] = data['seller']['userId']
        item['discount'] = []
        # data1 = getGoodsData(int(item['productId']), int(item['userId']))
        # if data1 == {}:
        #     print("获取店铺内商品页数据报错")
        #     return
        # else:
        #     try:
        #         dataList = data1['data']['coupons'][0]['couponList']
        #         for data2 in dataList:
        #             item['discount'].append({'reduce': data2['title'], 'use': data2['subtitles'][0]})
        #     except:
        #         pass
        item['shopScore'] = []  # 店铺评分
        item['post_title'] = item["productName"]
        for shop in data['seller']['evaluates']:
            item['shopScore'].append(shop['title'])
            item['shopScore'].append(shop['score'])
        item['params'] = ''  # 商品详情
        try:
            props = data['props']['groupProps'][0]['基本信息']
        except KeyError as e:
            props = []
        for propDict in props:
            for key, value in propDict.items():
                item['params'] += key + ':' + value + ','
        commentUrl = 'https://rate.taobao.com/detailCount.do?itemId={}'.format(item['productId'])
        # commentUrl = 'https://rate.taobao.com/detailCount.do?itemId={}'.format(item['goodsId'])
        url2 = 'https://count.taobao.com/counter3?callback=jsonp249&keys=ICCP_1_{}'
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            "referer": item['pageUrl']
            # "referer": item['url']
        }
        a = 0
        while True:
            if a < 3:
                try:
                    r = requests.get(commentUrl, headers=headers, timeout=10)
                    comment = re.search(r'\d+', r.text).group(0)
                    item['commentsCount'] = int(comment)  # 评论数量
                    r2 = requests.get(url2.format(item['productId']), headers=headers, timeout=15)
                    # r2 = requests.get(url2.format(item['goodsId']), headers=headers, timeout=15)
                    item['collectionNum'] = int(
                        re.search(r'jsonp\d+\({"ICCP_1_\d+":(\d+)}\);', r2.text).group(1))  # 收藏数量
                    break
                except:
                    print('获取店铺评论数量和收藏数量链接:{}数据异常第{}尝试'.format(commentUrl, a))
                    a += 1
            else:
                return
        process_item(item)
        # print(item)
    else:
        print('链接请求错误,商品Id:{}，错误:{}'.format(item['productId'], ret))
        url = "http://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{}%22%7D".format(item['productId'])
        # print('链接请求错误,商品Id:{}，错误:{}'.format(item['goodsId'], ret))
        # url = "http://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{}%22%7D".format(item['goodsId'])
        res = requests.get(url, headers=config.headers)
        response = res.text
        content(response, item)


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


def process_item(item):
    shopScore = {'服务': '0.0', '描述': '0.0', '物流': '0.0'}
    for i in range(0, len(item['shopScore']), 2):
        score = re.sub(r'\r+|\n+| +|\t+|n+|,+', '', item['shopScore'][i])
        if '描述' in score:
            score = '描述'
        elif '物流' in score:
            score = '物流'
        elif '服务' in score:
            score = '服务'
        try:
            shopScore[score] = re.search(r'\d+.\d+', item['shopScore'][i + 1]).group(0)
        except:
            shopScore[score] = '0.0'
    item['shopScore'] = '描述:{},物流:{},服务:{}'.format(shopScore['描述'], shopScore['物流'], shopScore['服务'])
    item['productId'] = int(item['productId'])
    # item['productId'] = int(item['goodsId'])
    item['shopId'] = str(item['shopId'])
    if not len(item['productSkuDetail']):
        item['productSkuDetail'] = [
            {'sku_id': str(item['productId']), 'sku_name': item['productName'],
             'sku_price': item['currentPrice'],
             'sku_stock': item['stockNum']}]  # 商品sku 详情
    item['productSkuDetail'] = json.dumps(item['productSkuDetail'], ensure_ascii=False)
    item['crawlTime'] = int(time.time() * 1000)
    craw_date = time.localtime(item['crawlTime']/1000)
    craw_date = time.strftime("%Y-%m-%d", craw_date)
    url = item['shopId'] + str(item['productId']) + craw_date + item['platform']
    item['connectGoodsId'] = urlmd5(url)
    try:
        commentsData = deepcopy(item['commentsData'])
        commentType = 1  # 有评论数据标记为1
        item.pop('commentsData')
    except:
        commentType = 0  # 无评论数据标记为0
    # while True:
        # try:
        #     msg = post_data_mongo(item)
        #     break
        # except:
        #     print('错误')
        #     time.sleep(0.5)
    # if msg['message'] == 'SUCCESS':
    if commentType:
        item['commentsData'] = commentsData
    saveItem = coll.save(item)
    print("成功一条", item)
        # logger.info('上传成功{}'.format(saveItem))
    # else:
    #     logger.info("上传失败不储存数据\nerror:{}\n{}".format(msg, item))


if __name__ == "__main__":
    start_requests()