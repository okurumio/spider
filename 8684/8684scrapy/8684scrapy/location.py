import requests
import json
import re


class Location:
    def gaode_location(self, station):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
        url = 'https://restapi.amap.com/v3/place/text?s=rsv3&children=&key=8325164e247e15eea68b59e89200988b&page=1&offset=10&city=110000&language=zh_cn&callback=jsonp_688971_&platform=JS&logversion=2.0&sdkversion=1.3&appname=https%3A%2F%2Flbs.amap.com%2Fconsole%2Fshow%2Fpicker&csid=EE2393C5-A78C-446A-B091-734FCA65BB36&keywords={}'.format(station)

        response = requests.get(url, headers=headers)
        data = re.findall(r'jsonp_688971_\((.*)\)', response.text)[0]
        text = json.loads(data)
        location = text['pois'][0]['location']
        location_x = re.findall(r'(.*),', location)[0]
        location_y = re.findall(r',(.*)', location)[0]
        return location_x, location_y

    def meituan_location(self, station):
        url = 'https://maf.meituan.com/search?key=be9427ec-bca4-4bfa-b981-9314f6a1adc7&location=116.311658%2C40.032256&region=CITY&orderby=weight&radius=50000&pageSize=20&page=1&city=%E5%8C%97%E4%BA%AC&keyword={}&wm_latitude=0&wm_longitude=0&wm_actual_latitude=40032256&wm_actual_longitude=116311658&_=1571796195571'.format(station)
        response = requests.get(url)
        data = json.loads(response.text)
        location = data['result']['pois'][0]['location']
        location_x = re.findall(r'(.*),', location)[0]
        location_y = re.findall(r',(.*)', location)[0]
        return location_x, location_y


if __name__ == '__main__':
    Location().meituan_location('西二旗公交站')
    Location().gaode_location('西二旗公交站')