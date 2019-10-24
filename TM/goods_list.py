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
        self.save_collection_name = 'TMGoodsUrl'
        self.collection_name = 'TMkey'
        self.db = Mongo(db_name)

    def get_list(self, list):
        urllist = []
        headers = {
            'referer': 'http://list.tmall.com/search_product.htm?q={}&type=p&spm=a220m.6910245.a2227oh.d100&from=mallfp..m_1_searchbutton&sort=d'.format(quote(list['keyword'], encoding="gbk")),
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': 'cna=l9oDFcy6VQ4CAd6AqijwI13O; _med=dw:1366&dh:768&pw:1366&ph:768&ist:0; lid=%E8%91%AC%E4%BB%AA%E4%B8%BF%E5%A4%9C%E7%A5%9E%E6%9C%88; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _uab_collina=156877667696726520994751; hng=CN%7Czh-CN%7CCNY%7C156; enc=twxIgD2w8bZQSql4cagTND22VE%2FhUTEOaq2XkcEtDvxxkz37BO5Mh25gdOoNdNoJF5i9aTpzn%2BrzEdT6wQL1qA%3D%3D; sm4=110100; _m_h5_tk=b33074b6753c714e2c5a32fd78d6c426_1571630922757; _m_h5_tk_enc=db58b55df9684e14b5c1aaef72e5c979; t=68aeed5a9ead7edb2d26b8d916cdf5be; _tb_token_=33b56e71b803e; cookie2=1d0efb3fed419cc8c79c62ce27633524; dnk=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; cq=ccp%3D0; tracknick=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; _l_g_=Ug%3D%3D; unb=2646574036; lgc=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; cookie1=BxpRR3m3mq6u2SKR8tMIAV5PbfT0Mkqa7hIMcGbyJO8%3D; login=true; cookie17=UU6lS5IHpNO1Zw%3D%3D; _nk_=%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708; sg=%E6%9C%886c; uc1=cookie14=UoTbnKU5vO8R1A%3D%3D&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D&pas=0&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&lng=zh_CN&existShop=false&tag=8&cookie21=U%2BGCWk%2F7p4mBoUyS4E9C; uc3=id2=UU6lS5IHpNO1Zw%3D%3D&nk2=tzejKGxa%2FgjcE9Gg&vt3=F8dByuckA3AzTRgxjWY%3D&lg2=VT5L2FSpMGV7TQ%3D%3D; uc4=nk4=0%40tUQ6%2FECahntTXqHnI5ioo65kDQrdQ7Y%3D&id4=0%40U2xo%2B4EAVHijItFSb4zrqlzll9lp; csg=66cb9310; x5sec=7b22746d616c6c7365617263683b32223a226433303262376437326166623365333865613263653965323938316134613934434a5846744f3046455048736b71766867504c3234674561444449324e4459314e7a51774d7a59374d673d3d227d; pnm_cku822=098%23E1hvevvUvbpvUvCkvvvvvjiPRszOAj1En2sWljD2PmPpsjrUnLSU1jE2PFMWlj3vRphvChCvvvvPvpvhvv2MMQhCvvXvovvvvvvEvpCWpSuUv8ROjovDN%2BClHdUf8B69D70Ode%2BRVA3l%2Bb8rwAtYmq0DW3CQcmx%2Fsj7J%2B3%2BijLjEIEkffvyf8j7yHdBYLjnv6nQ7RAYVEvLvq8yCvv3vpvolaufqRIyCvvXmp99he1KtvpvIphvvvvvvphCvpCBXvvCCN6CvHHyvvhn2phvZ7pvvpiivpCBXvvCmeuwCvvBvpvpZ; res=scroll%3A1349*5314-client%3A1349*318-offset%3A1349*5314-screen%3A1366*768; isg=BBkZMDWmoCVFC3xjiPXyRrtzKAUzDg1k1P50YDvO3sC_QjjUg_W7KLoQREaRf6WQ; l=dBLiViNPqB8DGUOzBOCZZuI8amQTKIRbSuPRwN4pi_5CG68_WbQOkM1H9FJ6cjWAGn8B4JuaUMvTCFJgJsl0NE8xDfpFlkM2B'
        }
        for page in range(list['page']):
            url = 'http://list.tmall.com/m/search_items.htm?page_size=20&page_no={}&q={}&type=p&sort=d'.format(page+1, quote(list['keyword'], encoding="gbk"))
            print(url)
            response = requests.get(url, headers=headers)
            print(response.text)
            datas = json.loads(response.text)['item']
            for data in datas:
                list['productName'] = data['title']
                list['pageUrl'] = 'https:' + data['url']
                print(list)
                urllist.append(deepcopy(list))
            time.sleep(10)
        if urllist != []:
            self.db.insert(self.save_collection_name, urllist)
            print('抓取数量：' + str(len(urllist)), '显示数量：' + str(list['count']))
        else:
            print(list['keyword'] + '无商品')

    def run(self):
        # self.db.drop(self.save_collection_name)
        keys = self.db.get(self.collection_name)
        i = 0
        for key in keys:
            print(i)
            i += 1
            list = AllNumber().get_number(key)
            print("正在抓取关键词：" + list['keyword'])
            GoodsList().get_list(list)
            time.sleep(10)


if __name__ == '__main__':
    GoodsList().run()



