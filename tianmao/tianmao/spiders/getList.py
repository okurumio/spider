# -*- coding: utf-8 -*-
import scrapy
import json
import time
from copy import deepcopy
from urllib.request import quote
from tianmao.common import connRedis
from tianmao.common import config
from tianmao.common import username_login


class GetlistSpider(scrapy.Spider):
    name = 'getList'
    # allowed_domains = ['www.baidu.com']
    # start_urls = ['http://www.baidu.com/']

    def start_requests(self):
        cookie = username_login.getCookie()
        item = {}
        list = []
        conn = connRedis.OPRedis()
        headers = {
            'referer': 'https://list.tmall.com/search_product.htm?q=%C6%A1%BE%C6&type=p&spm=a220m.8599659.a2227oh.d100&from=mallfp..m_1_suggest&searchType=default&sort=d',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            "Connection": "close",
            'cookie': 'sm4=110100; cna=l9oDFcy6VQ4CAd6AqijwI13O; tk_trace=1; t=68aeed5a9ead7edb2d26b8d916cdf5be; _tb_token_=3b5fe47538e69; cookie2=1735de9c85557f9f42e1df3633d89f42; _med=dw:1366&dh:768&pw:1366&ph:768&ist:0; dnk=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; tracknick=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; lid=%E8%91%AC%E4%BB%AA%E4%B8%BF%E5%A4%9C%E7%A5%9E%E6%9C%88; uc4=nk4=0%40tUQ6%2FECahntTXqHnI5ioot2jxOlREew%3D&id4=0%40U2xo%2B4EAVHijItFSb40x6HZvkQAW; lgc=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; enc=mgDx%2FG4LBa6Vh34myIUWRcXFDcku2yYoVmi5LRm6AqLVjcbsMLrPyszjHfBmSXuSEukb8S%2Bo%2Ffv6taJmBoY4pg%3D%3D; cq=ccp%3D0; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; swfstore=209459; x=__ll%3D-1%26_ato%3D0; _uab_collina=156877667696726520994751; res=scroll%3A1349*5531-client%3A1349*625-offset%3A1349*5531-screen%3A1366*768; pnm_cku822=098%23E1hvuQvUvbpvUvCkvvvvvjiPRFLwzjnbRFcWljljPmPOtj1hRFLvQjnjPLqysjtURphvChCvvvvCvpvVphhvvvvvKphv8hCvvvvvvhCvphvZ7pvvpFnvpCBXvvC2p6CvHHyvvh84phvZ7pvvpiuivpvUphvhrojveSJEvpvVpyUUCE%2BfmphvLhh6wQmFdcZIfvc6D40OjoE1paFZ5Cl0p5nC%2BnezrmphwhKn3feAOHHzLwexRdIAcVvHfwmK5eUpEZ8aiLyubhv3xw0tiCH%2BmB%2B%2BaNpPvpvhvv2MMTwCvvBvpvpZ; whl=-1%260%260%260; _m_h5_tk=b64abe9f69798e65a48e5518f2ce3209_1568797138854; _m_h5_tk_enc=7ad3e1ed6582abc7ee2fe8664927d1c9; uc1=lng=zh_CN&cookie21=UIHiLt3xThH8t7YQoFNq&existShop=false&cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D&cookie15=WqG3DMC9VAQiUQ%3D%3D&cookie14=UoTaECEopKnjRA%3D%3D&tag=8&pas=0; uc3=vt3=F8dByuKxrb90QLLzLnQ%3D&id2=UU6lS5IHpNO1Zw%3D%3D&lg2=VT5L2FSpMGV7TQ%3D%3D&nk2=tzejKGxa%2FgjcE9Gg; _l_g_=Ug%3D%3D; unb=2646574036; cookie1=BxpRR3m3mq6u2SKR8tMIAV5PbfT0Mkqa7hIMcGbyJO8%3D; login=true; cookie17=UU6lS5IHpNO1Zw%3D%3D; _nk_=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; sg=%E6%9C%886c; csg=4f4b3d78; tt=s.m.tmall.com; x5sec=7b22746d616c6c7365617263683b32223a226237336335663539373565306531643839656265336261653437313761326335434b3269682b774645504748317566333039323670774561444449324e4459314e7a51774d7a59374d513d3d227d; isg=BEVFsfe2tEVj9ZBnlNGGGm8PVIG_qvnGYNKYZEeqLXyL3mRQD1D9ZdO_7EKNpRFM; l=cBLiViNPqB8DGif1BOCZ5uI8aKbTRIRYjuPRwNvei_5CL6L1sbQOkswjLFp6cjWd9lYB4JuaUMv9-etkwRppO8_Tsszh.'
        }
        keys = config.getKey()
        for key in keys[:1]:
            for i in range(4):
                url = 'https://list.tmall.com/m/search_items.htm?page_size=60&page_no={}&q={}type=p&searchType=default&sort=d'.format(i, quote(key, encoding="gbk"))
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    headers=headers,
                    meta={'item': deepcopy(item), 'list': deepcopy(list)},
                    dont_filter=True,
                )
                # time.sleep(3)

    def parse(self, response):
        print(response)
        item = response.meta['item']
        list = response.meta['list']
        data = json.loads(response.text)
        goodslist = data['item']
        for good in goodslist:
            item['title'] = good['title']
            item['productId'] = good['item_id']
            item['url'] = 'https://detail.tmall.com/item.htm?id=' + str(item['productId'])
            list.append(deepcopy(item))
        print(list)
