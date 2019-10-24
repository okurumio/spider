# -*- coding: utf-8 -*-
import hashlib

import scrapy
from pymongo import MongoClient
from Select8684.location import Location


class Bus8684Spider(scrapy.Spider):
    name = 'bus8684'
    client = MongoClient('localhost', 27017)
    db = client['admin']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    stations = []

    def start_requests(self):
        url = 'https://beijing.8684.cn'
        yield scrapy.Request(
            url,
            method='GET',
            callback=self.get_bus_list,
            dont_filter=True,
        )

    def get_bus_list(self, response):
        start_numbers = response.xpath("//div[@class='bus-layer depth w120']/div[@class='pl10'][1]/div/a")
        for start_number in start_numbers:
            url = 'https://beijing.8684.cn/' + start_number.xpath("@href").extract_first()
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                callback=self.get_bus,
                dont_filter=True,
            )

    def get_bus(self, response):
        bus_numbers = response.xpath("//div[@class='list clearfix']/a")
        for bus_number in bus_numbers:
            url = 'https://beijing.8684.cn/' + bus_number.xpath("@href").extract_first()
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                callback=self.get_station,
                dont_filter=True,
            )

    def get_station(self, response):
        item = {}
        line_lists = response.xpath("//div[@class='bus-lzlist mb15']")
        for line_list in line_lists:
            station_lists = line_list.xpath("./ol/li")
            for station_list in station_lists:
                item['station'] = station_list.xpath("./a/text()").extract_first()
                item['location_x'], item['location_y'] = Location().gaode_location(item['station'])
                item['_id'] = urlmd5(item['station'] + item['location_x'] + item['location_y'])
                id = self.db.station.find_one({'_id': item['_id']})
                if id is None:
                    print(item)
                    self.db.station.insert(item)


def urlmd5(url):
    sign = hashlib.md5()  # 创建md5对象
    sign.update(url.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
    signs = sign.hexdigest()  # 加密
    return signs