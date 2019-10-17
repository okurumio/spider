from database import Mongo
from scrapy.selector import Selector
from JD.goods_comment import GoodsComment
import connRedis
import re
import requests
import json
import time
import hashlib
import post


class GoodsContent:
    def __init__(self):
        db_name = 'bayan'
        self.collection_name = 'JDGoodsUrl'
        self.save_collection_name = 'JDGoodsData'
        self.db = Mongo(db_name)
        self.conn = connRedis.OPRedis()

    def get(self, item):
        goods_id = re.findall(r'\d+', item['pageUrl'])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
        url = 'https://item.jd.com/{}.html'.format(goods_id[0])
        i = 0
        while i < 5:
            try:
                response = requests.get(url, headers=headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')}, timeout=5)
                break
            except:
                i += 1
                print('重新获取商品')
        print(response.url)
        if response.url == 'https://m.jd.com/404.htm?errcode=10001':
            print('该商品不存在')
            # db.goodsData.remove({"_id": item['_id']})
        current_price, original_price, compAddress, productParam, stockNum = self.get_price(goods_id[0])
        selector = Selector(text=response.text)
        item['pageUrl'] = "https://item.jd.com/{}.html".format(goods_id[0])
        item['_id'] = urlmd5(item['pageUrl'] + item['keyword'])
        product_name = selector.xpath('//div[@class="item ellipsis"]/@title').extract()[0]
        item['productName'] = product_name  # 商品名称
        item['productId'] = int(goods_id[0])  # 商品id
        item['platform'] = '京东'  # 平台
        item['custom'] = 2  # 平台
        item['platformType'] = 3
        item['brand'] = ''
        item['servicePromise'] = ''
        item['paymentInformation'] = ''
        item['productParam'] = ''  # 商品规格
        for parm in productParam:
            item['productParam'] += parm + ', '
        shop_url = selector.xpath('//div[@class="J-hove-wrap EDropdown fr"]//div[@class="name"]/a/@href').extract()[0]
        item['shopUrl'] = 'https:' + shop_url  # 店铺链接
        shop_id = selector.xpath(
            '//div[@class="J-hove-wrap EDropdown fr"]//div[@class="follow J-follow-shop"]/@data-vid').extract()[0]
        item['shopId'] = str(shop_id)  # 店铺id
        shop_name = selector.xpath('//div[@class="J-hove-wrap EDropdown fr"]//div[@class="name"]/a/@title').extract()[0]
        item['shopName'] = shop_name  # 店铺名称
        item['departureAddress'] = compAddress  # 发货地
        item['currentPrice'] = current_price  # 现价
        item['originalPrice'] = original_price  # 原价
        item['stockNum'] = stockNum  # 库存
        if item['stockNum'] == 33 or item['stockNum'] == 39 or item['stockNum'] == 40:  #33 现货 39|40 有货 36预订 其他无货
            item['stock'] = '有货'
        elif item['stockNum'] == 36:
            item['stock'] = '预订'
        else:
            item['stock'] = '无货'
        item['salesNumMonth'] = 0  # 月销量
        item['categories'] = ''  # 商品分类
        item['couponDescription'] = ''  # 商品描述
        item['collectionNum'] = 0  # 收藏量
        item['productSkuDetail'] = [{'sku_id': str(item['productId']), 'sku_name': item['productName'], 'sku_price': item['currentPrice'], 'sku_stock': item['stockNum']}]  # 商品sku 详情
        item['productSkuDetail'] = json.dumps(item['productSkuDetail'], ensure_ascii=False)
        count, level = self.commetn_count(goods_id)
        item['cmtStarLevel'] = level  # 商品评分
        item['commentsCount'] = count  # 评论数量
        item['crawlTime'] = int(time.time() * 1000)
        item['shopScore'] = selector.xpath("//div[@class='score-part']/span[@class='score-desc']/text() | //div[@class='score-part']/span[@class='score-detail']//text()").extract()
        shopScore = {'服务': '0.0', '描述': '0.0', '物流': '0.0'}
        # print(item['shopScore'])
        for i in range(0, len(item['shopScore']), 2):
            score = re.sub(r'\r+|\n+| +|\t+|n+|,+', '', item['shopScore'][i])
            if '评价' in score or '描述' in score:
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
        attrs = selector.xpath("//div[@class='p-parameter']//li//text()").extract()  # 商品详情介绍
        item['params'] = ''
        for attr in attrs:
            item['params'] += re.sub(r'\n+| +', '', attr) + ', '

        cat = re.findall(r'\[(.+)\]', re.findall(r'cat:(.+)', response.text)[0])[0]
        cat = cat.replace(',', '%2C')
        promotion = self.get_promotion(item['productId'], item['shopId'], cat)
        item['promotion'] = promotion  # 商品促销
        del item['count']
        craw_date = time.localtime(item['crawlTime'] / 1000)
        craw_date = time.strftime("%Y-%m-%d", craw_date)
        url = item['shopId'] + str(item['productId']) + craw_date + item['platform']
        item['connectGoodsId'] = urlmd5(url)
        page = 0
        comment_list, crawlCommentsTime = GoodsComment().get(item, page)
        item['commentsData'] = comment_list
        item['crawlCommentsCount'] = len(comment_list)
        item['crawlCommentsTime'] = crawlCommentsTime
        return item

    def commetn_count(self, goods_id):
        headers = {
            'Referer': 'https://item.m.jd.com/product/{}.html'.format(goods_id[0]),
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        url = 'http://sclub.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=6&page=0&pageSize=10'.format(goods_id[0])
        url2 = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'.format(goods_id[0])
        i = 0
        while i < 5:
            try:
                response = requests.get(url, headers=headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')}, timeout=5)
                break
            except:
                i += 1
        if response.text == '':
            response = requests.get(url2, headers=headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')}, timeout=5)
            data = json.loads(response.text)
            count = data['CommentsCount'][0]['CommentCount']
            level = data['CommentsCount'][0]['GoodRateShow']
        else:
            data = json.loads(response.text)
            count = data['productCommentSummary']['commentCount']
            level = data['productCommentSummary']['goodRateShow']
        return count, level

    def get_price(self, goods_id):
        headers = {
            'referer': 'https://list.jd.com/list.html?cat=1320,1584,13789&tid=17675&ev=exbrand_8179',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        url = 'https://item.m.jd.com/product/{}.html'.format(goods_id)
        i = 0
        while i < 5:
            try:
                response = requests.get(url, headers=headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
                break
            except:
                i += 1
        price = re.findall(r"\"price\":(.+),", response.text)[0]
        price = json.loads(price)
        current_price = price['p']
        original_price = price['op']
        try:
            stock = re.findall(r"\"stock\":(.+),", response.text)[0]
            stock = json.loads(stock)
        except:
            stock = {'ir': [], 'serviceInfo': '', 'StockState': 33}
        try:
            compAddress = stock['self_D']['df']  # 发货地
        except KeyError as e:
            try:
                compAddress = stock['D']['df']
            except:
                try:
                    compAddress = re.search(r"<.+>(.+)<", stock['serviceInfo']).group(1)
                except:
                    compAddress = stock['serviceInfo']
        try:
            salePropSeq = re.findall(r"\"salePropSeq\":{.*\"1\":(\[.+?\]).*\]}", response.text)[0]
        except:
            salePropSeq = '[]'
        try:
            salePropSeq = json.loads(salePropSeq)
        except:
            salePropSeq = re.findall(r"\"salePropSeq\":{.*\"1\":(\[.+?\]),.*\]}", response.text)[0]
            try:
                salePropSeq = json.loads(salePropSeq)
            except:
                salePropSeq = []
        productParam = salePropSeq
        if productParam == [""]:
            productParam = []
        stockNum = int(stock['StockState'])  # 库存 33 现货 39|40 有货 36预订 其他无货
        return current_price, original_price, compAddress, productParam, stockNum

    def get_promotion(self, productId, shopId, cat):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
        promotionUrl = 'https://cd.jd.com/promotion/v2?skuId={}&area=1_2800_2848&shopId={}&cat={}'.format(productId, shopId, cat)
        response = requests.get(url=promotionUrl, headers=headers)
        response.encoding = 'gbk'
        text = json.loads(response.text)['prom']
        promotion = ''
        for te in text['pickOneTag']:
            if '登录' in te['content']:
                pass
            else:
                promotion += te['content'] + ','
        for te in text['tags']:
            if '登录' in te['content']:
                pass
            else:
                promotion += te['content'] + ','
        return promotion

    def run(self):
        i = 0
        items = self.db.get(self.collection_name)
        for item in items[4358:]:
            print(i)
            goodsitem = self.get(item)
            print(goodsitem)
            post.uploadData(goodsitem)
            # self.db.insert(self.save_collection_name, goodsitem)
            i += 1


def urlmd5(url):
    sign = hashlib.md5()  # 创建md5对象
    sign.update(url.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
    signs = sign.hexdigest()  # 加密
    return signs