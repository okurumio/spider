import hashlib
import re
import requests
import connRedis
import json
import time


class GoodsComment:
    def __init__(self):
        self.conn = connRedis.OPRedis()
        self.comment_list = []

    def get(self, item, page):
        last_time_num = 0
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'referer': 'https://detail.m.tmall.com/item.htm?id=566603678176&skuId=4080112804775',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'cookie': 'sm4=110100; cna=l9oDFcy6VQ4CAd6AqijwI13O; lid=%E8%91%AC%E4%BB%AA%E4%B8%BF%E5%A4%9C%E7%A5%9E%E6%9C%88; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; hng=CN%7Czh-CN%7CCNY%7C156; enc=twxIgD2w8bZQSql4cagTND22VE%2FhUTEOaq2XkcEtDvxxkz37BO5Mh25gdOoNdNoJF5i9aTpzn%2BrzEdT6wQL1qA%3D%3D; t=68aeed5a9ead7edb2d26b8d916cdf5be; _tb_token_=79e3dbeb0eaea; cookie2=1dfdba00d2c64b337b13ab30300482e5; l=dBLiViNPqB8DGeBDBOfalurza77TUCAf5rVzaNbMiICPODC2A0YhWZI6r-YyCnGV3stMR3yE78S3BfLZdyUBlZXRFJXn9Mp9XdTeR; isg=BPr6Abqic9x-Qf9mF-ghSxzmSyAcq36F00u3pQT3_A0095Mx7Dg5lTtFR8OO4fYd; x5sec=7b22726174656d616e616765723b32223a226161323263333063646531383439383765316261616333343333636638626261434e792b70653046454a654e2b72482f7a634b2b6851453d227d'
        }
        url = 'https://rate.tmall.com/list_detail_rate.htm?itemId={}&sellerId={}&order=3&currentPage={}&pageSize=10'.format(item['productId'], item['shopId'], page)
        response = requests.get(url, headers=headers)
        text = re.search('jsonp\d+\((.+)\)', response.text).group(1)
        text = json.loads(text)
        comments = text['rateDetail']['rateList']
        get_num = len(comments)  # 获取该页评论总数
        if get_num > 0:
            for comment in comments:
                lastTime = comment['rateDate']  # 获取评论最后时间
                lastTime = int(time.mktime(time.strptime(lastTime, '%Y-%m-%d %H:%M:%S')))
                if lastTime >= 1569859200:  # if 大于昨日的数据
                    # 符合条件的数据添加到评论列表中
                    craw_date = time.localtime(lastTime)
                    craw_date = time.strftime("%Y-%m-%d", craw_date)
                    url = item['shopId'] + str(item['productId']) + craw_date + item['platform']
                    liItem = {'rateContent': comment['rateContent'],  # 评论内容
                              'displayUserNick': comment['displayUserNick'],  # 评论用户
                              'rateDate': comment['rateDate'],  # 评论时间
                              'cmtStarLevel': '',  # 评分星级
                              'source': '',  # 评论来源
                              'label': '',  # 标签
                              'sellShop': '',  # 卖家
                              'fabulous': 0,  # 点赞数
                              'readCount': 0,  # 阅读数
                              'floor': int(comment['id']),
                              'connectGoodsId': urlmd5(url)  # 连接商品表商品信息id(md5)
                              }
                    emoji_pattern = re.compile(u'[\U00010000-\U0010ffff]')
                    liItem['rateContent'] = emoji_pattern.sub('', liItem['rateContent'])
                    self.comment_list.append(liItem)
                else:
                    # 不符合条件的数据标记+1
                    last_time_num += 1
            if last_time_num < get_num:
                # 每页最少有一条符合要求的数据
                # 拼接下一页
                page += 1
                self.get(item, page)
            else:
                # 本页无所需数据,停止翻页
                print("商品id:{},page:{},本页数据超出所需范围,停止抓取".format(item['productId'], page))
        else:
            print("无评论内容")
            # 无评论内容储存该商品数据
        crawlCommentsTime = int(time.time() * 1000)
        return self.comment_list, crawlCommentsTime


def urlmd5(url):
    sign = hashlib.md5()  # 创建md5对象
    sign.update(url.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
    signs = sign.hexdigest()  # 加密
    return signs
