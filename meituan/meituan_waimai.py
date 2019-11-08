import requests, zlib, base64
import json
import time
from meituan.meituan import connRedis
from pymongo import MongoClient
from copy import deepcopy
from datetime import datetime


class meituan:
    def __init__(self):
        self.conn = connRedis.OPRedis()
        client = MongoClient('localhost', 27017)
        self.db = client['admin']
        self.useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        self.cookoe = '_lxsdk_cuid=16e152bc9ffc8-0a20f5888339d2-5373e62-100200-16e152bca00c8; _ga=GA1.3.1438179633.1572313222; iuuid=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; _hc.v=e30873cc-c29b-660a-be71-2aa3c59beff6.1572488944; IJSESSIONID=ilz4qls88cot8zbcdtxauacz; __utma=74597006.471011287.1573184589.1573184589.1573184589.1; __utmc=74597006; __utmz=74597006.1573184589.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); ci3=1; latlng=40.042113,116.299429,1573184592253; i_extend=C_b1Gimthomepagecategory1394H__a; wm_order_channel=mtib; __utmb=74597006.4.8.1573184591617; cssVersion=f2cbd8b3; utm_source=60030; au_trace_key_net=default; _lx_utm=utm_source%3D60030; openh5_uuid=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; uuid=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; _lxsdk_s=16e491bbb80-0b1-41a-f59%7C%7C8'

    # 生成token
    def encode_token(self, start_time):
        ts = start_time
        token_dict = {
            'rId': 910,
            'ver': '1.0.6',
            'ts': ts,
            'cts': ts + 100 * 1000,
            'brVD': [1010, 750],
            'brR': [[1920, 1080], [1920, 1040], 24, 24],
            'bI': ['https://gz.meituan.com/meishi/c11/', ''],
            'mT': [],
            'kT': [],
            'aT': [],
            'tT': [],
            'aM': '',
            'sign': 'eJwdjktOwzAQhu/ShXeJ4zYNKpIXqKtKFTsOMLUn6Yj4ofG4UjkM10CsOE3vgWH36df/2gAjnLwdlAPBBsYoR3J/hYD28f3z+PpUnmJEPqYa5UWEm0mlLBRqOSaP1qjEtFB849VeRXJ51nr56AOSVIi9S0E3LlfSzhitMix/mQwsrdWa7aTyCjInDk1mKu9nvOHauCQWq2rB/8laqd3cX+adv0zdzm3nbjTOdzCi69A/HQAHOOyHafMLmEtKXg=='
        }
        # 二进制编码
        encode = str(token_dict).encode()
        # 二进制压缩
        compress = zlib.compress(encode)
        # base64编码
        b_encode = base64.b64encode(compress)
        # 转为字符串
        token = str(b_encode, encoding='utf-8')
        return token

    # 解压token
    def decode_token(self, token):
        # base64解码
        token_decode = base64.b64decode(token.encode())
        # 二进制解压
        token_string = zlib.decompress(token_decode)
        return token_string

    def get_cookie(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        }
        url = 'https://h5.waimai.meituan.com/waimai/mindex/home'
        response = requests.get(url, headers, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
        time.sleep(2)
        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        print(cookies)

    def get_list(self):
        item = {}
        list = []
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/kingkong?navigateType=910&firstCategoryId=910&secondCategoryId=910&title=%E7%BE%8E%E9%A3%9F',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': '_lxsdk_cuid=16e152bc9ffc8-0a20f5888339d2-5373e62-100200-16e152bca00c8; _ga=GA1.3.1438179633.1572313222; iuuid=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; _hc.v=e30873cc-c29b-660a-be71-2aa3c59beff6.1572488944; uuid=641f2233ea8f417c9dbb.1573120815.1.0.0; _gid=GA1.3.720087403.1573120730; __mta=214823848.1573120730363.1573120813591.1573121684065.3; IJSESSIONID=1paqqonuvf8fs16stuf8alo1nr; ci3=1; __utmc=74597006; __utmz=74597006.1573121913.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); wm_order_channel=mtib; utm_source=60030; au_trace_key_net=default; openh5_uuid=03B31769F0D0665209C5173E30779BAE012940CB666FF42A3E769B834C55DB7A; showTopHeader=show; __utma=74597006.657717205.1573121913.1573121913.1573177077.2; meishi_ci=1; cityid=1; latlng=40.042113,116.299429,1573178771198; __utmb=74597006.14.9.1573178771505; i_extend=C_b1Gimthomepagecategory1394H__a; cssVersion=b713183e; _lx_utm=utm_source%3D60030; webloc_geo=40.043389%2C116.305531%2Cgcj02%2C-1; _lxsdk_s=16e48a928fe-15e-e82-28%7C%7C38'
        }
        for i in range(5):
            start_time = int(datetime.now().timestamp() * 1000)
            url = 'https://i.waimai.meituan.com/openh5/channel/kingkongshoplist?_={}&startIndex={}&sortId=5&navigateType=910&firstCategoryId=910&secondCategoryId=910&wm_latitude=40043389&wm_longitude=116305531'.format(start_time, i)
            token = self.encode_token(start_time)
            datas = {
                '_token': token
            }
            response = requests.post(url, headers=headers, data=datas)
            response.encoding = 'utf-8'
            data = json.loads(response.text)
            shoplist = data['data']['shopList']
            for shop in shoplist:
                item['shopName'] = shop['shopName']  # 商家名称
                item['mtWmPoiId'] = shop['mtWmPoiId']  # 商家id
                item = self.get_info(item)
                item = self.get_goods(item)
                item = self.get_comment(item)
                list.append(deepcopy(item))
                self.save(list)

    def get_info(self, item):
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/menu?dpShopId=&mtShopId={}&utm_source=60030&source=shoplist&initialLat=&initialLng=&actualLat=&actualLng='.format(item['mtWmPoiId']),
            'User-Agent': self.useragent,
            'cookie': self.cookoe
        }
        start_time = int(datetime.now().timestamp() * 1000)
        token = self.encode_token(start_time)
        form_data = {
            'mtWmPoiId': item['mtWmPoiId'],
            '_token': token
        }
        url = 'https://i.waimai.meituan.com/openh5/poi/info?_={}'.format(start_time)
        response = requests.post(url, headers=headers, data=form_data, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
        response.encoding = 'utf-8'
        data = json.loads(response.text)['data']
        activityList = data['activityList']
        item['activity'] = [activity['actDesc'] for activity in activityList]  # 商家活动
        item['shopAddress'] = data['shopAddress']  # 商家地址
        shopLat = data['shopLat']
        shopLng = data['shopLng']
        invoiceSupport = data['invoiceSupport']
        if invoiceSupport == 1:
            item['service'] = '该商家支持在线支付'  # 商家服务
        else:
            item['service'] = ''
        item['coordinates'] = str(shopLat) + ',' + str(shopLng)  # 商家坐标
        item['discribe'] = data['tip']  # 商家描述
        item['isBrand'] = data['isBrand']  # 是否品牌商家
        item['serTime'] = data['serTime']  # 配送时间
        return item

    def get_goods(self, item):
        fooditem = {}
        foodlist = []
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/menu?dpShopId=&mtShopId={}&utm_source=60030&source=shoplist&initialLat=&initialLng=&actualLat=&actualLng='.format(item['mtWmPoiId']),
            'User-Agent': self.useragent,
            'cookie': self.cookoe
        }
        start_time = int(datetime.now().timestamp() * 1000)
        token = self.encode_token(start_time)
        form_data = {
            'mtWmPoiId': item['mtWmPoiId'],
            '_token': token
        }
        url = 'https://i.waimai.meituan.com/openh5/poi/food?_={}'.format(start_time)
        response = requests.post(url, headers=headers, data=form_data, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
        response.encoding = 'utf-8'
        data = json.loads(response.text)['data']
        shopinfo = data['shopInfo']
        item['bulletin'] = shopinfo['bulletin']  # 商家描述
        categoryList = data['categoryList']
        for category in categoryList:
            fooditem['categoryName'] = category['categoryName']  # 商品分类
            spuList = category['spuList']
            for spu in spuList:
                fooditem['activity'] = spu['spuPromotionInfo']  # 商品活动
                fooditem['unit'] = []  # 商品规格
                spuAttrList = spu['spuAttrList']
                for spuAttr in spuAttrList:
                    spuAttrValueList = spuAttr['spuAttrValueList']
                    for spuAttrValue in spuAttrValueList:
                        spuitem = {}
                        spuitem['attrId'] = spuAttrValue['attrId']
                        spuitem['attrValue'] = spuAttrValue['attrValue']
                        fooditem['unit'].append(deepcopy(spuitem))
                fooditem['spuName'] = spu['spuName']  # 商品名称
                fooditem['spuId'] = spu['spuId']  # 商品ID
                fooditem['spuDesc'] = spu['spuDesc']  # 商品描述
                fooditem['spuPicture'] = []  # 图片链接
                try:
                    pictureList = spu['productLabelPictureList']
                    fooditem['spuPicture'] = [pic['pictureUrl'] for pic in pictureList]
                except:
                    fooditem['spuPicture'] = spu['bigImageUrl']
                fooditem['currentPrice'] = spu['currentPrice']  # 现价
                fooditem['originPrice'] = spu['originPrice']  # 原价
                fooditem['saleVolume'] = spu['saleVolumeDecoded']  # 销量
                skuList = spu['skuList']
                fooditem['skuid'] = [sku['skuId'] for sku in skuList]  # skuid
            foodlist.append(deepcopy(fooditem))
        item['food'] = foodlist
        return item

    def get_comment(self, item):
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/menu?dpShopId=&mtShopId={}&utm_source=60030&source=shoplist&initialLat=&initialLng=&actualLat=&actualLng='.format(item['mtWmPoiId']),
            'User-Agent': self.useragent,
            'cookie': self.cookoe
        }
        start_time = int(datetime.now().timestamp() * 1000)
        token = self.encode_token(start_time)
        form_data = {
            'mtWmPoiId': item['mtWmPoiId'],
            '_token': token
        }
        url = 'https://i.waimai.meituan.com/openh5/poi/comments?_={}'.format(start_time)
        response = requests.post(url, headers=headers, data=form_data, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
        response.encoding = 'utf-8'
        data = json.loads(response.text)['data']
        item['shopScore'] = data['shopScore']  # 店铺评分
        item['recordCount'] = data['recordCount']  # 评论数量
        item['comments'] = []
        comments = data['list']
        for comment in comments:
            commentitem = {}
            commentitem['userName'] = comment['userName']
            commentitem['userID'] = comment['userID']
            commentitem['commentTime'] = comment['commentTime']
            commentitem['score'] = comment['score']
            commentitem['content'] = comment['content']
            pictures = comment['pictures']
            commentitem['pictures'] = [picture['originalPicUrl'] for picture in pictures]
            item['comments'].append(deepcopy(commentitem))
        return item

    def get_qualification(self, item):
        headers = {
            'x-requested-with': 'XMLHttpRequest',
            'Sec-Fetch-Mode': 'cors',
            'content-type': 'application/x-www-form-urlencoded',
            'Referer': 'https://i.waimai.meituan.com/c/foods_safe_doc/index.html?wm_poi_id=938107949519001',
            'User-Agent': self.useragent,
        }
        form_data = {
            'wm_poi_id': item['mtWmPoiId'],
        }
        url = 'https://i.waimai.meituan.com/ajax/v6/poi/qualification'
        response = requests.post(url, headers=headers, data=form_data, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
        data = json.loads(response.text)['data']
        item['company_name'] = data['certify_info']['company_name']  # 单位名称
        item['company_address'] = data['certify_info']['address']  # 单位地址
        item['business_scope'] = data['certify_info']['business_scope']  # 主营业务
        item['business_type'] = data['certify_info']['business_type']  # 公司类型
        item['company_owner'] = data['certify_info']['company_owner']  # 法定代表人
        item['permit_num'] = data['certify_info']['permit_num']  # 许可证号
        item['expire_time'] = data['certify_info']['expire_time']  # 有效期
        item['qualify_pics'] = data['qualify_pics']  # 资质信息
        return item

    def save(self, list):
        self.db.meituandata_.insert(list)
        print(list)


if __name__ == '__main__':
    item = {'shopName': '小恒水饺（上地数码大厦店）', 'mtWmPoiId': '1067867502046944'}
    # meituan().get_list()
    # meituan().get_info(item)
    # meituan().get_goods(item)
    # meituan().get_comment(item)
    # meituan().get_qualification(item)
