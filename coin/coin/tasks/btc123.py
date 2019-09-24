# -*- coding: utf-8 -*-
import time, datetime
import requests
import json
from coin import getTasks
from copy import deepcopy
from coin import connRedis


def run():
    keys = getTasks.getTasks().btc123()
    db = getTasks.getTasks().getMongo()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Connection": "close",
    }
    conn = connRedis.OPRedis()
    item = {}
    for i in keys:
        url = 'https://apioperate.btc123.com/api/content/selectPageFlashNews?pageNumber=1&title={}&sourceId=1'.format(str(i['key']))
        j = 0
        while j < 5:
            try:
                response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
                break
            except:
                j += 1
                print(url + "请求失败")
        data = json.loads(response.text)
        lists = data['data']['list']
        for list in lists:
            item['post_title'] = list['title']
            item['created_at'] = list['createTime']
            item['read_count'] = 0
            item['original_url'] = 'https://www.btc123.com/search?type=flash&keyword={}'.format(str(i['key']))
            item['page_url'] = item['original_url']
            item['source_host'] = list['source']
            item['screen_name'] = '匿名'
            item['text'] = list['content']
            item['time'] = int(time.time())
            item['floor'] = int(list['id'])
            item['column'] = i['key']
            item['platform'] = '区块链快讯'
            item['column1'] = i['column1']
            item['originalPlatformId'] = i['originalPlatformId']
            item['keywordId'] = i['keywordId']
            item['reptileType'] = i['reptileType']
            item['contentType'] = i['contentType']
            title = db.btc123.find_one({'post_title': item['post_title']})
            if title is None:
                print(item)
                getTasks.post_data(item)
                db.btc123.insert(deepcopy(item))
    print('end')


if __name__ == '__main__':
    run()

