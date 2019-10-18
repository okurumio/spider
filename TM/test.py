import requests
import json
import username_login


def get_lists(cookei):
    cookie = username_login.getCookie()
    headers = {
        'referer': 'http://list.tmall.com/search_product.htm?q=%BA%D3%CC%D7&type=p&cat=all',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'cookie': cookei

    }
    for i in range(10):
        url = 'http://list.tmall.com/m/search_items.htm?page_size=20&page_no={}&q=%BA%D3%CC%D7&type=p&cat=all'.format(i)
        print(url)
        response = requests.get(url, headers=headers)
        print(response.url)
        datas = json.loads(response.text)['item']
        for data in datas:
            title = data['title']
            url = 'https:' + data['url']
            print(title, url)


def tb():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Referer': 'https://uland.taobao.com/sem/tbsearch?refpid=mm_26632258_3504122_32538762&clk1=3d69a4f60819c8373c4517b679029338&keyword=%E6%B2%B3%E5%A5%97&page=0'

    }
    url = 'https://uland.taobao.com/sem/tbsearch?keyword=%E6%B2%B3%E5%A5%97&page=3'
    response = requests.get(url, headers=headers)
    print(response.text)


def get_cookei():
    str = ''
    dict = {"_hvn_login": "0", "_tb_token_": "e7b0ee3e3375b", "cookie2": "126a2bc4df39bc527d25b8e0371c7c79", "csg": "959eeed0", "t": "aabb1c1ed74bf02cedf161939e964858", "lc": "Vyu%2B4M9z4gNdCM8xOHGuRB4%3D", "lid": "%E8%91%AC%E4%BB%AA%E4%B8%BF%E5%A4%9C%E7%A5%9E%E6%9C%88", "log": "lty=Tmc%3D", "havana_tgc": "eyJjcmVhdGVUaW1lIjoxNTcxMjE5MDIxMTQyLCJsYW5nIjoiemhfQ04iLCJwYXRpYWxUZ2MiOnsiYWNjSW5mb3MiOnsiMCI6eyJhY2Nlc3NUeXBlIjoxLCJtZW1iZXJJZCI6MjY0NjU3NDAzNiwidGd0SWQiOiIxU09jUGlDM0ZuY2ZzM0dCMW0ycEtNZyJ9fX19", "_cc_": "UtASsssmfA%3D%3D", "_l_g_": "Ug%3D%3D", "_nk_": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708", "cookie1": "BxpRR3m3mq6u2SKR8tMIAV5PbfT0Mkqa7hIMcGbyJO8%3D", "cookie17": "UU6lS5IHpNO1Zw%3D%3D", "dnk": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708", "existShop": "MTU3MTIxOTAyMQ%3D%3D", "lgc": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708", "sg": "%E6%9C%886c", "skt": "b3cd3c1c99a908fd", "tg": "0", "tracknick": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708", "uc1": "lng=zh_CN&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D&cookie14=UoTbnKFVQuRBhQ%3D%3D&pas=0&cookie21=UtASsssmeW6lpyd%2BB%2B3t&cookie15=W5iHLLyFOGW7aA%3D%3D&tag=8&existShop=false", "uc3": "lg2=Vq8l%2BKCLz3%2F65A%3D%3D&id2=UU6lS5IHpNO1Zw%3D%3D&nk2=tzejKGxa%2FgjcE9Gg&vt3=F8dByuDsdLfBeKLvC8c%3D", "uc4": "nk4=0%40tUQ6%2FECahntTXqHnI5ioo65gNhdg9ew%3D&id4=0%40U2xo%2B4EAVHijItFSb4zrrl5FCNcx", "unb": "2646574036", "XSRF-TOKEN": "d08541af-cf39-452d-b7c3-17f9b753db86"}
    for i in dict:
        str = str + i + "=" + dict[i] + '; '
    return str


if __name__ == '__main__':
    cookei = get_cookei()
    # get_lists(cookei)
    tb()