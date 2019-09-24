import requests


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
url = 'https://www.huoxing24.com/info/news/multisearch?page=1&pageSize=18&type=2&q=火币&deviceSource=web'
response = requests.get(url, headers=headers)
print(response.text)