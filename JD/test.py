import requests, zlib, base64
import json
import re
from datetime import datetime
import connRedis

goods_id = 10840194307
shopId = 600597


def main(cat):
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
                'Referer': 'https://item.jd.com/10582162427.html'
            }
    promotionUrl = 'https://cd.jd.com/promotion/v2?skuId={}&area=1_2800_2848&shopId={}&cat={}'.format(goods_id, shopId, cat)
    print(promotionUrl)
    response = requests.get(url=promotionUrl, headers=headers)
    response.encoding = 'gbk'
    text = json.loads(response.text)['prom']
    promotion = ''
    for te in text['pickOneTag']:
        if '登录' in te['content']:
            pass
        else:
            promotion += te['content'] + ','
    for te in text['tags']:
        if '登录' in te['content']:
            pass
        else:
            promotion += te['content'] + ','
    print(promotion)


def cat():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    url = 'https://item.jd.com/{}.html'.format(goods_id)
    response = requests.get(url, headers=headers)
    cat = re.findall(r'\[(.+)\]', re.findall(r'cat:(.+)', response.text)[0])[0]
    cat = cat.replace(',', '%2C')
    main(cat)


def url_decode(data):
    """token解码"""
    if isinstance(data, str):
        data = base64.b64decode(data)
        base_data = zlib.decompress(data)
        return base_data


def meituan():
    conn = connRedis.OPRedis()
    headers = {
        'Sec-Fetch-Mode': 'cors',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://h5.waimai.meituan.com',
        'Referer': 'https://h5.waimai.meituan.com/waimai/mindex/home',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
    }
    url = 'https://i.waimai.meituan.com/openh5/homepage/poilist?_=1571120809726'
    jsons = {
        "startIndex": 0,
        "sortId": 0,
        "geoType": 2,
        "uuid": '1A20860165EF079A6A4BE8C172F8167C7F0F48F3BD83C562BBD0AB6757B294EC',
        "platform": 3,
        "partner": 4,
        "originUrl": 'https://h5.waimai.meituan.com/waimai/mindex/home',
        "riskLevel": 71,
        "optimusCode": 10,
        "wm_latitude": 40053034,
        "wm_longitude": 116306295,
        "wm_actual_latitude": 0,
        "wm_actual_longitude": 0,
        "openh5_uuid": '1A20860165EF079A6A4BE8C172F8167C7F0F48F3BD83C562BBD0AB6757B294EC',
        "_token": 'eJyVkWuPmkAUhv8LiX5ZIwy3AROzEQUc8QqsujZNMwLCKAwujKg0/e9lu26b9luTSd73POck5zLfuQKFXA8IAAqgw1VRwfU40BW6KtfhWNlkFAiAqMlQkXWlwwV/MRXKQofbF+sR1/siQaWjqvDrO3Cb+A/440S5ee8VqCngEsbOZY/nE6V7xSTDpJtFhF0w7QZ5xn8gPiM0jG58FtHLc3j2kvyMwn47Yw+nA0HWdU3XoKIDSWpfWPatzC9FEPXbDy2bypSUrE0oYQSnU8z6vz2N+20cNE1/YVnoCpKqAvjJmjQAaldqmkhic5L/GflEaHzKafxMcUVizCL/fo7eB24fSFGyYUPivLh/LNEuoyCn4T+QEZZG/ZYJW4bZ0syWqbcGUku3uOaGmd/csNHTQ/FD2Wc8a76yGbkkMW1cNLmzk2lVyXCwSg78dFwk65XrXYcb+rLdzbJIPHrzo4Dz1J8ME2Ltq6rypIjhwz4wtTm8wvtS3G59TRzSmwwPKDSmTzwC3k4ewBAKJ7A26sSaaUqdHu1X5ZocX71dnmB4245fQmuQZAaxvbHNHA2ZazxOiYUtVLt2YmFAaDHbp/RiviEh3cHMcs1z4c5K6q9uG3uBt/oLSxdB7Bl0vanqRalppa3gfbaU7/a0Pk3OuYdYelgOXUdaa+uNw3wn5NEdzJdK8iTsBluV7YOLLpQg5pnijPT1baio8cZQXNfP6c0x6gNm8xrN81V0tnzbtGZDx+E3xcBFiblAfmycFBKe/Pny6q8cXVRo7duvYIvUe6wpQV4Mggrx0fQw4eESlaJ62ZgAjeTSeRLq5F5V41LFfJZbmrHiL3rsRvu09KWxMFJv4ptw7fe5Hz8BnxMg3g=='
    }
    response = requests.post(url, headers=headers, json=jsons, proxies={'https': conn.randomOneIp('proxy:new_ip_list')})

    print(response.text)


if __name__ == '__main__':
    time = int(datetime.now().timestamp() * 1000)
    print(time)
