from TM.shop_data import AllNumber
from database import Mongo
from urllib.request import quote
from copy import deepcopy
import requests
import json
import time


class GoodsList:
    def __init__(self):
        db_name = 'bayan'
        self.collection_name = 'TMGoodsUrl'
        self.db = Mongo(db_name)

    def get_list(self, list):
        urllist = []
        headers = {
            'referer': 'http://list.tmall.com/search_product.htm?q={}&type=p&spm=a220m.6910245.a2227oh.d100&from=mallfp..m_1_searchbutton&sort=d'.format(quote(list['keyword'], encoding="gbk")),
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': 'sm4=110100; cna=l9oDFcy6VQ4CAd6AqijwI13O; _med=dw:1366&dh:768&pw:1366&ph:768&ist:0; lid=%E8%91%AC%E4%BB%AA%E4%B8%BF%E5%A4%9C%E7%A5%9E%E6%9C%88; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _uab_collina=156877667696726520994751; hng=CN%7Czh-CN%7CCNY%7C156; enc=twxIgD2w8bZQSql4cagTND22VE%2FhUTEOaq2XkcEtDvxxkz37BO5Mh25gdOoNdNoJF5i9aTpzn%2BrzEdT6wQL1qA%3D%3D; t=68aeed5a9ead7edb2d26b8d916cdf5be; _tb_token_=7a3ee3e76440e; cookie2=15e9eb44b0f560e5f91c3fcece093fd2; swfstore=283797; dnk=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; whl=-1%260%260%260; tracknick=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; lgc=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; _m_h5_tk=e91e8db252f1f1af5d035442eecbd779_1571308888546; _m_h5_tk_enc=fd33b2b7939ed80e9a51e2c8f4fdad32; uc1=cookie21=Vq8l%2BKCLjhS4UhJVbhgU&cookie15=W5iHLLyFOGW7aA%3D%3D&cookie14=UoTbnKCtZtqsvw%3D%3D&tag=8&cookie16=WqG3DMC9UpAPBHGz5QBErFxlCA%3D%3D&existShop=false&pas=0&lng=zh_CN; uc3=nk2=tzejKGxa%2FgjcE9Gg&lg2=W5iHLLyFOGW7aA%3D%3D&id2=UU6lS5IHpNO1Zw%3D%3D&vt3=F8dByuDsfAbPdCngADA%3D; _l_g_=Ug%3D%3D; uc4=nk4=0%40tUQ6%2FECahntTXqHnI5ioo65hlvwMjcQ%3D&id4=0%40U2xo%2B4EAVHijItFSb4zrrzoIu2lO; unb=2646574036; cookie1=BxpRR3m3mq6u2SKR8tMIAV5PbfT0Mkqa7hIMcGbyJO8%3D; login=true; cookie17=UU6lS5IHpNO1Zw%3D%3D; _nk_=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; sg=%E6%9C%886c; csg=c84ceb17; tt=login.taobao.com; cq=ccp%3D0; res=scroll%3A1349*5387-client%3A1349*189-offset%3A1349*5387-screen%3A1366*768; x5sec=7b22746d616c6c7365617263683b32223a223230376439346236316365616263326435313163653539623530313539366662434f54476f4f3046454d322b6c5948556f34764478514561444449324e4459314e7a51774d7a59374d513d3d227d; pnm_cku822=098%23E1hvPpvUvbpvUpCkvvvvvjiPRszWQjrEPsdhQjD2PmPWAjtUPsMZsjinP2cv6jEbRFyCvvpvvhCvKphv8vvvphvvvvvvvvCHhQvvvngvvhZLvvmCvvvvBBWvvvH%2BvvCHhQvvv7AEvpvVvpCmpYsOuphvmvvvpo1F8%2F0FmphvLvj%2FR29afBeKHdUf8cc6%2Bu6wdeQEfJmK5d0%2FfvDrQ8TJhLISNUkQ%2Bu6Od56OfwmKDBhTWDKtkC4AdB9aUExrV8TxhowH%2BE7reTTJEcgCvpvVvvBvpvvv2QhvCvvvvvm5vpvhvvCCBv%3D%3D; l=dBLiViNPqB8DGmx8BOCwlurza77tDIRf_uPzaNbMi_5wC181EU7OkGCiLeJ6cjWAG-8B4JuaUMvTyFJLJsl0NE8xOLeuB7H2B; isg=BGZmxUkvB1mPaNMqo_R1TwDCt9zoR6oBX--b6VAPJQlk0wftuNRxEXbhK496_KIZ'
        }
        for page in range(list['page']):
            url = 'http://list.tmall.com/m/search_items.htm?page_size=20&page_no={}&q={}&type=p&sort=s'.format(page+1, quote(list['keyword'], encoding="gbk"))
            response = requests.get(url, headers=headers)
            print(response.url)
            datas = json.loads(response.text)['item']
            for data in datas:
                list['productName'] = data['title']
                list['pageUrl'] = 'https:' + data['url']
                print(list)
                urllist.append(deepcopy(list))
        self.db.insert(self.collection_name, urllist)
        print('抓取数量：' + str(len(urllist)), '显示数量：' + str(list['count']))

    def run(self):
        self.db.drop(self.collection_name)
        lists = AllNumber().get_number()
        for list in lists[:1]:
            list['page'] = int(list['count'] / 20) + 1
            print("正在抓取关键词：" + list['keyword'])
            GoodsList().get_list(list)
            time.sleep(1)

    def test(self):
        self.db.drop(self.collection_name)
        list = {'column1': '天猫', 'platform': '天猫', 'originalPlatformId': 35, 'reptileType': 1, 'contentType': 2,
                'keyword': '三胖蛋', 'keywordId': 8541, 'page': 0, 'count': 172}
        list['page'] = int(list['count']/20)+1
        GoodsList().get_list(list)


if __name__ == '__main__':
    GoodsList().test()





