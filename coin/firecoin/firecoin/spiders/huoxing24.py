# -*- coding: utf-8 -*-
import scrapy
from items import FirecoinItem


class Huoxing24Spider(scrapy.Spider):
    name = 'huoxing24'
    allowed_domains = ['www.huoxing24.com']
    start_urls = ['http://www.huoxing24.com/']

    def parse(self, response):
        print(response)