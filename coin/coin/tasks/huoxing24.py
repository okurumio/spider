# -*- coding: utf-8 -*-
import time, datetime
import re
import requests
import json
from copy import deepcopy
from coin import getTasks
from coin import connRedis


def run():
    keys = getTasks.getTasks().huoXing()
    db = getTasks.getTasks().getMongo()
    headers = {
        "Connection": "close",
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'UM_distinctid=16c99cbf4b9d1-08963401d03938-7373e61-100200-16c99cbf4ba0; _ga=GA1.2.955456149.1565948376; Hm_lvt_d70f8822d1ff168453d5ea7b3e359297=1567396038,1567646981,1569203292; CNZZDATA1272858809=353535772-1566174481-https%253A%252F%252Fflash.huoxing24.com%252F%7C1569198357; _gid=GA1.2.620194914.1569203293; _gat_gtag_UA_121795392_1=1; USD=6.833898; rightAdImgCloseTime=2019-09-23; Hm_lpvt_d70f8822d1ff168453d5ea7b3e359297=1569203315; SERVERID=29dcb2c2e0682adea06ad95c2d4fe0cc|1569203446|1569203415',
        'referer': 'https://www.huoxing24.com/search/%E7%81%AB%E5%B8%81',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sign-param': 'eyJwbGF0Zm9ybSI6InBjIiwibm9uY2UiOiJQR1NObk8iLCJ0aW1lc3RhbXAiOjE1NjYyMDUxNjUyMDYsInNpZyI6IjhhODg5MDdiMmFmYjhiNGM4ODVjMTc4MmY2NjNkZjUxIn0=',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    conn = connRedis.OPRedis()
    item = {}
    for i in keys:
        url = 'https://www.huoxing24.com/info/news/multisearch?page=1&pageSize=18&type=2&q={}&deviceSource=web'.format(str(i['key']))
        # quote(key, encoding="gbk")
        j = 0
        while j < 5:
            try:
                response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}, timeout=3)
                print(response.text)
                break
            except:
                j += 1
                print(url+"请求失败")
        data = json.loads(response.text)
        if data['code'] == 1:
            lists = data['obj']['inforList']
            for list in lists:
                p1 = re.compile(r'[【](.*?)[】]', re.S)  # 最小匹配
                item['post_title'] = re.findall(p1, list['content'])[0]
                year = list['id'][:4]
                mounth = list['id'][4:6]
                day = list['id'][6:8]
                hour = list['id'][8:10]
                minute = list['id'][10:12]
                item['created_at'] = year+"-"+mounth+"-"+day+" "+hour+":"+minute
                item['read_count'] = 0
                item['original_url'] = 'https://www.huoxing24.com/search/{}'.format(str(i['key']))
                item['page_url'] = item['original_url']
                item['source_host'] = ""
                item['screen_name'] = list['author']
                item['text'] = list['content']
                item['time'] = int(time.time())
                item['floor'] = int(list['id'][8:])
                item['column'] = i['key']
                item['platform'] = '火星财经'
                item['column1'] = i['column1']
                item['originalPlatformId'] = i['originalPlatformId']
                item['keywordId'] = i['keywordId']
                item['reptileType'] = i['reptileType']
                item['contentType'] = i['contentType']
                title = db.huoxing.find_one({'post_title': item['post_title']})
                if title is None:
                    print(item)
                    getTasks.post_data(item)
                    db.huoxing.insert(deepcopy(item))
    print('end')


if __name__ == '__main__':
    run()