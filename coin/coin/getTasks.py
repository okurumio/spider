import requests
import json
from copy import deepcopy
from pymongo import MongoClient


class getTasks:
    def __init__(self):
        url = ''  # 获取任务接口
        res = requests.get(url,)
        res.encoding = 'utf-8'
        self.res = json.loads(res.text.strip('var data='))

    def huoXing(self):
        data = self.res['data']['keywords'][43]
        return self.getTask(data)

    def heCaijing(self):
        data = self.res['data']['keywords'][50]
        return self.getNosearchTask(data)

    def bitKan(self):
        data = self.res['data']['keywords'][56]
        return self.getNosearchTask(data)

    def btc123(self):
        data = self.res['data']['keywords'][54]
        return self.getTask(data)

    def huoxun(self):
        data = self.res['data']['keywords'][51]
        return self.getTask(data)

    def getTask(self, data):
        lists = []
        keys = {}
        keys['column1'] = data['column1']
        keys['platform'] = data['platform']
        keys['originalPlatformId'] = data['originalPlatformId']
        keys['reptileType'] = data['reptileType']
        keys['contentType'] = data['contentType']
        keyworlds = data['column']
        for i in keyworlds:
            keys['key'] = i['name']
            keys['keywordId'] = i['keywordId']
            lists.append(deepcopy(keys))
        return lists

    def getNosearchTask(self, data):
        keys ={}
        keys['column1'] = data['column1']
        keys['platform'] = data['platform']
        keys['originalPlatformId'] = data['originalPlatformId']
        keys['reptileType'] = data['reptileType']
        keys['contentType'] = data['contentType']
        keys['key'] = ''
        keys['keywordId'] = ''
        return keys

    def getMongo(self):
        client = MongoClient('localhost', 27017)
        db_name = 'huobi'
        db = client[db_name]
        return db


def post_data(datass):
    data = {
        "dictPlan": "[[]]",
        "datas": [datass],
        "currentPort": "8071",
        "currentHost": "",
        "page_url": datass['page_url']
    }
    try:
        req = requests.post(
            '',  # 上传接口
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Content-Type": "text/xml; charset=utf8"
            }
        )
        print(req.text)
    except Exception as e:
        print(e)
