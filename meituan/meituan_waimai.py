import requests, zlib, base64
import json
import connRedis
from copy import deepcopy
from datetime import datetime


class meituan:
    def __init__(self):
        self.id = 1004735776843630
        self.conn = connRedis.OPRedis()

    def get_list(self):
        item = {}
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/kingkong?navigateType=910&firstCategoryId=910&secondCategoryId=910&title=%E7%BE%8E%E9%A3%9F',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': 'swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; showTopHeader=show; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lx_utm=utm_source%3D60040; au_trace_key_net=default; cssVersion=3e1f2511; openh5_uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; utm_source=60040; uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; wm_order_channel=bdxcx; _lx_utm=utm_source%3D60040; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; _lxsdk_test=1; openh5_uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635; userName=mhM563502399; utm_source=60040; uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; wm_order_channel=bdxcx; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; iuuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; mt_c_token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; oops=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635'
        }
        for i in range(1):
            start_time = int(datetime.now().timestamp() * 1000)
            url = 'https://i.waimai.meituan.com/openh5/channel/kingkongshoplist?_={}&startIndex={}&sortId=1&navigateType=910&firstCategoryId=910&secondCategoryId=910&wm_latitude=40078517&wm_longitude=116719944'.format(
                start_time, i)
            token = self.encode_token(start_time)
            datas = {
                '_token': token
            }
            response = requests.post(url, headers=headers, data=datas)
            data = json.loads(response.text)
            shoplist = data['data']['shopList']
            for shop in shoplist[:1]:
                item['shopName'] = shop['shopName']  # 商家名称
                item['mtWmPoiId'] = shop['mtWmPoiId']  # 商家id
                # self.get_info(item)
                # self.get_goods(item)
                self.get_comment(item)

    def get_info(self, item):
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/menu?dpShopId=&mtShopId={}&utm_source=60030&source=shoplist&initialLat=&initialLng=&actualLat=&actualLng='.format(item['mtWmPoiId']),
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': 'swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; showTopHeader=show; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lx_utm=utm_source%3D60040; au_trace_key_net=default; cssVersion=3e1f2511; openh5_uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; utm_source=60040; uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; wm_order_channel=bdxcx; _lx_utm=utm_source%3D60040; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; _lxsdk_test=1; openh5_uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635; userName=mhM563502399; utm_source=60040; uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; wm_order_channel=bdxcx; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; iuuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; mt_c_token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; oops=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635'
        }
        start_time = int(datetime.now().timestamp() * 1000)
        token = self.encode_token(start_time)
        form_data = {
            'mtWmPoiId': item['mtWmPoiId'],
            '_token': token
        }
        url = 'https://i.waimai.meituan.com/openh5/poi/info?_={}'.format(start_time)
        response = requests.post(url, headers=headers, data=form_data, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
        data = json.loads(response.text)['data']
        print(item['mtWmPoiId'], data)
        item['activity'] = []  # 商家活动
        activityList = data['activityList']
        for activity in activityList:
            item['activity'].append(activity['actDesc'])
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
        print(item)

    def get_goods(self, item):
        fooditem = {}
        foodlist = []
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/menu?dpShopId=&mtShopId={}&utm_source=60030&source=shoplist&initialLat=&initialLng=&actualLat=&actualLng='.format(item['mtWmPoiId']),
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': 'swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; showTopHeader=show; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lx_utm=utm_source%3D60040; au_trace_key_net=default; cssVersion=3e1f2511; openh5_uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; utm_source=60040; uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; wm_order_channel=bdxcx; _lx_utm=utm_source%3D60040; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; _lxsdk_test=1; openh5_uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635; userName=mhM563502399; utm_source=60040; uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; wm_order_channel=bdxcx; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; iuuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; mt_c_token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; oops=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635'
        }
        start_time = int(datetime.now().timestamp() * 1000)
        token = self.encode_token(start_time)
        form_data = {
            'mtWmPoiId': item['mtWmPoiId'],
            '_token': token
        }
        url = 'https://i.waimai.meituan.com/openh5/poi/food?_={}'.format(start_time)
        response = requests.post(url, headers=headers, data=form_data, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
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
                    for pic in pictureList:
                        pictureUrl = pic['pictureUrl']
                        fooditem['spuPicture'].append(deepcopy(pictureUrl))
                except:
                    fooditem['spuPicture'] = spu['bigImageUrl']
                fooditem['currentPrice'] = spu['currentPrice']  # 现价
                fooditem['originPrice'] = spu['originPrice']  # 原价
                fooditem['saleVolume'] = spu['saleVolumeDecoded']  # 销量
                skuList = spu['skuList']
                fooditem['skuid'] = []  # skuid
                for sku in skuList:
                    id = sku['skuId']
                    fooditem['skuid'].append(id)
            foodlist.append(deepcopy(fooditem))
        item['food'] = foodlist
        print(item)

    def get_comment(self, item):
        headers = {
            'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/menu?dpShopId=&mtShopId={}&utm_source=60030&source=shoplist&initialLat=&initialLng=&actualLat=&actualLng='.format(item['mtWmPoiId']),
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': 'swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; showTopHeader=show; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lxsdk_s=16e103d0c18-68c-c8d-964%7C%7C2; _lx_utm=utm_source%3D60040; au_trace_key_net=default; cssVersion=3e1f2511; openh5_uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; utm_source=60040; uuid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; wm_order_channel=bdxcx; _lx_utm=utm_source%3D60040; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; _lxsdk_test=1; openh5_uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; swanid=Sr8CCf1G4wTURENKimE5CCnGoNh4J88bJL36CRKvi7beeFgmFa6TC1hwa7eSsxWrMWcxXPmsjCsssuepMegJ1N2aA; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635; userName=mhM563502399; utm_source=60040; uuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; wm_order_channel=bdxcx; _lxsdk=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; _lxsdk_cuid=16dce2f0fc3c8-0081748614b4988-504c182b-3d10d-16dce2f0fc3c8; iuuid=24F9E6B89E486462696F7E452DCF9018C4081595734F9CD6271CEE5ED52DDC57; mt_c_token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; oops=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; token=wLK_wPK_z2I0x4YLrYFk0DzMWJoAAAAA5AgAANvCrbB1Wk7fcXyUpkPFD5WsHM0Uv4MHYUdZ6Mcq_RFXLQP5_SbysNwjmVMBqo7tUg; userId=2643733635'
        }
        start_time = int(datetime.now().timestamp() * 1000)
        token = self.encode_token(start_time)
        form_data = {
            'mtWmPoiId': item['mtWmPoiId'],
            '_token': token
        }
        url = 'https://i.waimai.meituan.com/openh5/poi/comments?_={}'.format(start_time)
        response = requests.post(url, headers=headers, data=form_data, proxies={'https': self.conn.randomOneIp('proxy:new_ip_list')})
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
            commentitem['pictures'] = []
            pictures = comment['pictures']
            for picture in pictures:
                pictureurl = picture['originalPicUrl']
                commentitem['pictures'].append(pictureurl)
            item['comments'].append(deepcopy(commentitem))
        print(item)

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


if __name__ == '__main__':
    meituan().get_list()



