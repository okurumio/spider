# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FirecoinItem(scrapy.Item):
    created_at = scrapy.Field()
    read_count = scrapy.Field()
    original_url = scrapy.Field()
    page_url = scrapy.Field()
    source_host = scrapy.Field()
    screen_name = scrapy.Field()
    text = scrapy.Field()
    time = scrapy.Field()
    floor = scrapy.Field()
    columnn = scrapy.Field()
    platform = scrapy.Field()
    column1 = scrapy.Field()
    originalPlatformId = scrapy.Field()
    keywordId = scrapy.Field()
    reptileType = scrapy.Field()
    contentType = scrapy.Field()
