import scrapy
from copy import deepcopy
from urllib.request import quote
from tianmao.common import config


class GetcountSpider(scrapy.Spider):
    name = 'getCount'
    # allowed_domains = ['www.baidu.com']

    def start_requests(self):
        item = {}
        keys = config.getKey()
        headers = {
            'referer': 'https://www.tmall.com/?ali_trackid=2:mm_26632258_3504122_48284354:1568685244_128_2054002187&clk1=fdcdc974875c084c2e7cc3e3533793a8&upsid=fdcdc974875c084c2e7cc3e3533793a8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        }
        for key in keys:
            try:
                url = 'http://list.tmall.com/search_product.htm?q={}'.format((quote(key, encoding="gbk")))
            except:
                url = 'http://list.tmall.com/search_product.htm?q={}'.format(key)
            item['key'] = key
            item['url'] = url
            yield scrapy.Request(
                url=url,
                headers=headers,
                callback=self.parse,
                dont_filter=True,
                meta={"item": deepcopy(item)}
            )

    def parse(self, response):
        item = response.meta['item']
        count = response.xpath("//p[@class='crumbTitle j_ResultsNumber']/span/text() | //p[@class='crumbTitle']/span/text()").extract_first()
        page = response.xpath("//input[@name='totalPage']/@value").extract_first()
        item['count'] = count
        item['page'] = page


