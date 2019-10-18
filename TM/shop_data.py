from database import Mongo
from scrapy.selector import Selector
from urllib.request import quote
import connRedis
import requests


class AllNumber:
    def __init__(self):
        db_name = 'bayan'
        self.collection_name = 'TMkey'
        self.db = Mongo(db_name)
        self.conn = connRedis.OPRedis()

    def get_number(self):
        goodsList = []
        keys = self.db.get(self.collection_name)
        headers = {
            'referer': 'https://list.tmall.com/search_product.htm?q={}'.format(quote('三胖蛋', encoding="gbk")),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'cookie': 'sm4=110100; cna=l9oDFcy6VQ4CAd6AqijwI13O; _med=dw:1366&dh:768&pw:1366&ph:768&ist:0; lid=%E8%91%AC%E4%BB%AA%E4%B8%BF%E5%A4%9C%E7%A5%9E%E6%9C%88; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _uab_collina=156877667696726520994751; hng=CN%7Czh-CN%7CCNY%7C156; enc=twxIgD2w8bZQSql4cagTND22VE%2FhUTEOaq2XkcEtDvxxkz37BO5Mh25gdOoNdNoJF5i9aTpzn%2BrzEdT6wQL1qA%3D%3D; t=68aeed5a9ead7edb2d26b8d916cdf5be; _tb_token_=7a3ee3e76440e; cookie2=15e9eb44b0f560e5f91c3fcece093fd2; swfstore=283797; dnk=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; whl=-1%260%260%260; tracknick=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; lgc=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; _m_h5_tk=81520ec83430fd239d377e4675e6f5d6_1571289042457; _m_h5_tk_enc=9800ebaece9ee7d0e1816c435a6d703f; res=scroll%3A1349*5387-client%3A1349*625-offset%3A1349*5387-screen%3A1366*768; uc1=existShop=false&cookie21=WqG3DMC9Fb5mPLIQo9kR&pas=0&cookie14=UoTbnKFcjyENBw%3D%3D&cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&tag=8&cookie15=V32FPkk%2Fw0dUvg%3D%3D&lng=zh_CN; uc3=lg2=URm48syIIVrSKA%3D%3D&id2=UU6lS5IHpNO1Zw%3D%3D&nk2=tzejKGxa%2FgjcE9Gg&vt3=F8dByuDscmAK7qJhHII%3D; _l_g_=Ug%3D%3D; uc4=id4=0%40U2xo%2B4EAVHijItFSb4zrrlfYyBm3&nk4=0%40tUQ6%2FECahntTXqHnI5ioo65gP1%2FkUnM%3D; unb=2646574036; cookie1=BxpRR3m3mq6u2SKR8tMIAV5PbfT0Mkqa7hIMcGbyJO8%3D; login=true; cookie17=UU6lS5IHpNO1Zw%3D%3D; _nk_=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; sg=%E6%9C%886c; csg=7bfdb20d; tt=login.taobao.com; pnm_cku822=098%23E1hvtvvUvbpvUpCkvvvvvjiPRszUzjEbPFzplj1VPmPv6jr2RFqpgjr8n25yQjn8n4wCvvpvvhHh2QhvCvvvvvvCvpvVvUCvpvvvKphv8vvvphvvvvvvvvCHhQvvvf9vvhZLvvmCvvvvBBWvvvH%2BvvCHhQvvv7AivpvUvvCCbHYoGCeEvpvVvpCmpYsOmphvLvbPXeOa6fItn1viHExreEeKjkx%2F1WoKHs4Aby5BIX%2F4V331oGLve3KXHFXXiXhpVE01Ux8x9C%2BaRfU6pwethb8rV369D76Od34AVA6tvpvhvvCvpv%3D%3D; cq=ccp%3D0; isg=BFBQBlyNOXTSreWo2Zo7rbr0IZ6iGTRjdZnN60ohhKt-hfMv8iqA8-XzXQ3AUuw7; l=dBLiViNPqB8DG19vBOfwhurza77tuIRf11PzaNbMiICPO41W5CZdWZIuoBTXCnGVHsBXR3yE78SHBPYNVyCqi7T2kX98ERUo3dC..'
        }
        for key in keys:
            url = 'https://list.tmall.com/search_product.htm?q={}&type=p'.format(quote('三胖蛋', encoding="gbk"))
            response = requests.get(url, headers=headers)
            selector = Selector(text=response.text)
            count = selector.xpath("//p[@class='crumbTitle j_ResultsNumber']/span/text() | //p[@class='crumbTitle']/span/text()").extract_first()
            if count is None:
                print("解除验证码更换cookie")
            else:
                content = selector.xpath("//div[@class='suggestTip']//text()").extract_first()
                key['page'] = 0
                if content:
                    key['count'] = 0
                else:
                    key['count'] = int(count)
                print(key)
                goodsList.append(key)
        return goodsList


if __name__ == '__main__':
    AllNumber().get_number()