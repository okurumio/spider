import json
import hashlib
import time
import random

import requests


class YouDao:
    def tramslate(self, text):
        headers = {
            'Host': 'fanyi.youdao.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest', 'Content-Length': '262', 'Connection': 'keep-alive',
            'Referer': 'http://fanyi.youdao.com/',
            'Cookie': 'OUTFOX_SEARCH_USER_ID=-244748932@10.108.160.17; JSESSIONID=aaaJXAwjjxrxuciZ0jq4w; OUTFOX_SEARCH_USER_ID_NCOO=672999022.6146495; ___rl__test__cookies=1572229311197'
        }
        salt = str(int(time.time() * 1000) + random.randint(0, 10))
        data = {
            "i": text,
            "from": "AUTO",
            "to": "AUTO",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "ts": salt[:-1],
            "salt": salt,
            "sign": self.sign_b(text, salt),
            "bv": self.md5_b("5.0 (Windows)"),
            "doctype": "json",
            "version": "2.1",
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTIME',
        }
        url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        response = requests.post(url, headers=headers, data=data)
        print(response.text)

    def md5_b(self, key):
        m = hashlib.md5()
        m.update(key.encode('utf-8'))
        return m.hexdigest()

    def sign_b(self, key, salt):
        sign = 'fanyideskweb' + key + str(salt) + 'n%A-rKaT5fb[Gy?;N5@Tj'
        return self.md5_b(sign)


if __name__ == '__main__':
    text = 'In this exercise, you will implement linear regression and get to see it work'
    YouDao().tramslate(text)