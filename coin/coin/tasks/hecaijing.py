# -*- coding: utf-8 -*-
import time, datetime
import re
import requests
import json
from coin import getTasks
from copy import deepcopy
from coin import connRedis


def run():
    keys = getTasks.getTasks().heCaijing()
    db = getTasks.getTasks().getMongo()
    headers = {
        'Cookie': 'PHPSESSID=dq7c7te4bmvco8ddmj4kt171p7; _ga=GA1.2.1003817106.1566180235; _gid=GA1.2.2147195660.1566180235; Hm_lvt_b94ff1ee8863337601c8a7baf17d031c=1566180235; Hm_lpvt_b94ff1ee8863337601c8a7baf17d031c=1566209238; _gat_gtag_UA_122528065_1=1',
        'Host': 'www.hecaijing.com',
        'Referer': 'https://www.hecaijing.com/kuaixun/',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    conn = connRedis.OPRedis()
    item = {}
    for i in range(1, 5):
        url = 'https://www.hecaijing.com/express/loadmore?coin=&pn={}'.format(i)
        response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
        data = json.loads(response.text)
        lists = data['data'][0]['buttom']
        for list in lists:
            item['post_title'] = list['title']
            item['created_at'] = list['update_time']
            item['read_count'] = 0
            item['original_url'] = 'https://www.hecaijing.com/kuaixun/'
            item['page_url'] = item['original_url']
            item['source_host'] = ""
            item['screen_name'] = list['publish_adminuser']
            item['text'] = list['main']
            item['time'] = int(time.time())
            item['floor'] = int(list['id'])
            item['column'] = '火币'
            item['platform'] = keys['platform']
            item['column1'] = keys['column1']
            item['originalPlatformId'] = keys['originalPlatformId']
            item['keywordId'] = 12235
            item['reptileType'] = keys['reptileType']
            item['contentType'] = keys['contentType']
            title = db.hecaijing.find_one({'post_title': item['post_title']})
            if title is None:
                print(item)
                getTasks.post_data(item)
                db.hecaijing.insert(deepcopy(item))

    print('end')


if __name__ == '__main__':
    run()
