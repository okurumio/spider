from JD.shop_data import AllNumber
from scrapy.selector import Selector
from database import Mongo
from copy import deepcopy
import requests
import time


class GoodsList:
    def __init__(self):
        self.count = 0
        db_name = 'bayan'
        self.collection_name = 'JDGoodsUrl'
        self.db = Mongo(db_name)

    def get_list(self, list):
        urllist = []
        headers = {
            'referer': 'https://search.jd.com/Search?keyword=minecraft&enc=utf-8&pvid=b55d6cb7986748d6a32da02876cc9874',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
        del list['_id']
        pages = list['pages']
        pages = pages*2+1
        for page in range(pages)[1:]:
            url = 'https://search.jd.com/s_new.php?keyword={}&psort=3&enc=utf-8&page={}&s={}&scrolling=y&log_id={}'.format(list['keyword'], page, page*31, int(time.time()))
            response = requests.get(url, headers=headers).text
            selector = Selector(text=response)
            goods = selector.xpath('//li[@class="gl-item"]')
            for good in goods:
                goodsurl = good.xpath('.//a[@target="_blank"]/@href').extract()[0]
                list['pageUrl'] = 'https:' + goodsurl
                print(list)
                urllist.append(deepcopy(list))
        self.count = len(urllist)
        back = self.check(list['count'], urllist)
        if back == 'success':
            print(list['keyword'] + ":成功")
            return urllist
        else:
            print(list['keyword'] + ":失败,重新抓取")
            self.get_list(list)

    def check(self, count, urllist):
        if self.count == count:
            self.db.insert(self.collection_name, urllist)
            self.count = 0
            return 'success'

    def run(self):
        self.db.drop(self.collection_name)
        lists = AllNumber().get_number()
        for list in lists:
            print("正在抓取关键词：" + list['keyword'])
            GoodsList().get_list(list)
            time.sleep(1)


def test():
    list = {'keyword': '河套官方旗舰店', 'pages': 3, 'count': 154}
    GoodsList().get_list(list)





