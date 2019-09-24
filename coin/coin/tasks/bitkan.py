import time, datetime
import re
import requests
import json
from copy import deepcopy
from coin import getTasks
from coin import connRedis


def run():
    keys = getTasks.getTasks().bitKan()
    db = getTasks.getTasks().getMongo()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    conn = connRedis.OPRedis()
    item = {}
    url = 'https://bitkan.com/api/news/weibo/705014?locale=zh'
    response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
    data = json.loads(response.text)
    lists = data['briefs']
    for list in lists:
        item['post_title'] = list['title']
        item['created_at'] = list['updated_at']
        item['read_count'] = 0
        item['original_url'] = 'https://bitkan.com/zh/news'
        item['page_url'] = item['original_url']
        item['source_host'] = ""
        item['screen_name'] = list['name']
        item['text'] = list['content']['text']
        item['time'] = int(time.time())
        item['floor'] = int(list['id'])
        item['column'] = '火币'
        item['platform'] = '比特币快讯'
        item['column1'] = '比特币快讯'
        item['originalPlatformId'] = 188
        item['keywordId'] = 12235
        item['reptileType'] = keys['reptileType']
        item['contentType'] = keys['contentType']
        title = db.bitkan.find_one({'post_title': item['post_title']})
        if title is None:
            print(item)
            getTasks.post_data(item)
            db.bitkan.insert(deepcopy(item))

    print('end')


if __name__ == '__main__':
    run()
