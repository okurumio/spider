# -*- coding: utf-8 -*-
import time, datetime
import re
import requests
import json
from coin import getTasks
from copy import deepcopy
from coin import connRedis


def run():
    db = getTasks.getTasks().getMongo()
    keys = getTasks.getTasks().huoxun()
    headers = {
        "Connection": "close",
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'PHPSESSID=0clbstiheafjj5gr2ob50p0rj6; Hm_lvt_f396f0424d21da4c5df398bf0ca78f23=1566180318; Hm_lvt_b7769c8d87ab17b2001f99ab6b37c33d=1566180318; Hm_lpvt_f396f0424d21da4c5df398bf0ca78f23=1566206928; Hm_lpvt_b7769c8d87ab17b2001f99ab6b37c33d=1566206928',
        'referer': 'https://huoxun.com/search.html',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    conn = connRedis.OPRedis()
    item = {}
    for i in keys:
        url = 'https://huoxun.com/cms/api/search_quick.html?search_field=title&keyword={}&page=1'.format(str(i['key']))
        j = 0
        while j < 5:
            try:
                response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
                break
            except:
                j += 1
                print(url + "请求失败")
        data = json.loads(response.text)
        lists = data['data']
        for list in lists:
            item['post_title'] = list['title']
            timeStamp = list['update_time']
            timeArray = time.localtime(timeStamp)
            item['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            item['read_count'] = 0
            item['original_url'] = 'https://huoxun.com/search.html'
            item['page_url'] = item['original_url']
            item['source_host'] = ""
            item['screen_name'] = '匿名'
            item['text'] = list['des']
            item['time'] = int(time.time())
            item['floor'] = int(list['id'])
            item['column'] = i['key']
            item['platform'] = '火讯财经'
            item['column1'] = i['column1']
            item['originalPlatformId'] = i['originalPlatformId']
            item['keywordId'] = i['keywordId']
            item['reptileType'] = i['reptileType']
            item['contentType'] = i['contentType']
            title = db.huoxun.find_one({'post_title': item['post_title']})
            if title is None:
                print(item)
                getTasks.post_data(item)
                db.huoxun.insert(deepcopy(item))
    print('success')


if __name__ == '__main__':
    run()