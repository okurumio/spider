from database import Mongo
from bs4 import BeautifulSoup
from copy import deepcopy
import requests
import re


class AllNumber:
    def __init__(self):
        db_name = 'bayan'
        self.collection_name = 'key'
        self.db = Mongo(db_name)

    def get_number(self):
        keys = self.db.get(self.collection_name)
        headers = {
            'referer': 'https://search.jd.com/Search?keyword=iphone&enc=utf-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
        goodsList = []
        for key in keys:
            url = 'https://search.jd.com/Search?keyword={}&enc=utf-8'.format(key['keyword'])
            response = requests.get(url, headers=headers).text
            soup = BeautifulSoup(response, "html.parser")
            count = re.findall(r"result_count:\'(\d+)\'", response)
            page_span = soup.find("span", class_="fp-text")
            pages = re.findall(r'\d+', page_span.find("i").text)[0]
            key['pages'] = int(pages)
            key['count'] = int(count[0])
            goodsList.append(deepcopy(key))
        return goodsList


