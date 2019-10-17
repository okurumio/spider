from copy import deepcopy
import requests
import re
import json
import time
import hashlib
import connRedis


class GoodsComment:
    def get(self, item, page):
        conn = connRedis.OPRedis()
        comment_list = []
        goods_id = re.findall(r'\d+', item['pageUrl'])[0]
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Referer': 'https://item.jd.com/{}.html'.format(goods_id)
        }
        url = 'https://sclub.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=6&page={}&pageSize=10'.format(goods_id, page)
        while True:
            try:
                response = requests.get(url, headers=headers, proxies={'https': conn.randomOneIp('proxy:new_ip_list')}, timeout=5).text
                break
            except:
                print("重新获取评论")
        if response != '':
            data = json.loads(response)
            comments = data['comments']
            comments_count = int(data['productCommentSummary']['commentCount'])
            get_num = len(comments)
            last_time_num = 0
            if page < 100:
                if get_num > 0:
                    for comment in comments:
                        lastTime = comment['creationTime']  # 获取评论最后时间
                        lastTime = int(time.mktime(time.strptime(lastTime, '%Y-%m-%d %H:%M:%S')))
                        if lastTime >= 1569859200:  # if 大于昨日
                            craw_date = time.localtime(lastTime)
                            craw_date = time.strftime("%Y-%m-%d", craw_date)
                            url = item['shopId'] + str(item['productId']) + craw_date + item['platform']
                            comments_item = {'rateContent': comment['content'],  # 评论内容
                                      'displayUserNick': comment['nickname'],  # 评论用户
                                      'rateDate': comment['creationTime'],  # 评论时间
                                      'cmtStarLevel': str(comment['score']),  # 评分星级
                                      'source': '',  # 评论来源
                                      'label': '',  # 标签
                                      'sellShop': '',  # 卖家
                                      'fabulous': int(comment['usefulVoteCount']),  # 点赞数
                                      'readCount': int(comment['replyCount']),  # 阅读数
                                      'floor': int(comment['id']),
                                      'connectGoodsId': urlmd5(url)  # 连接商品表商品信息id(md5)
                                      }
                            # print(comments_item)
                            comment_list.append(deepcopy(comments_item))
                        else:
                            last_time_num += 1
                    if last_time_num < get_num:
                        # 每页最少有一条符合要求的数据
                        # 拼接下一页
                        page += 1
                        self.get(item, page)
                    else:
                        pass
                        # print('本页无所需数据,停止翻页')
                else:
                    print("无评论")
            crawlCommentsTime = int(time.time() * 1000)
            return comment_list, crawlCommentsTime
        else:
            crawlCommentsTime = int(time.time() * 1000)
            return [],crawlCommentsTime


def urlmd5(url):
    sign = hashlib.md5()  # 创建md5对象
    sign.update(url.encode())  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
    signs = sign.hexdigest()  # 加密
    return signs
