import re
import os
import json

import requests


s = requests.Session()
# cookies序列化文件
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'


class UsernameLogin:

    def __init__(self, username, ua, TPL_password2):
        """
        账号登录对象
        :param username: 用户名
        :param ua: 淘宝的ua参数
        :param TPL_password2: 加密后的密码
        """
        # 检测是否需要验证码的URL
        self.user_check_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
        # 验证淘宝用户名密码URL
        self.verify_password_url = "https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.tmall.com%2F%3Fali_trackid%3D2%3Amm_26632258_3504122_48284354%3A1568771491_194_633735732%26clk1%3Dbf77ace2ec2c1d1ff954b7234067d409%26upsid%3Dbf77ace2ec2c1d1ff954b7234067d409"
        # 访问st码URL
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        # 淘宝个人 主页
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'

        # 淘宝用户名
        self.username = username
        # 淘宝关键参数，包含用户浏览器等一些信息，很多地方会使用，从浏览器或抓包工具中复制，可重复使用
        self.ua = ua
        # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
        self.TPL_password2 = TPL_password2

        # 请求超时时间
        self.timeout = 3

    def _user_check(self):
        """
        检测账号是否需要验证码
        :return:
        """
        data = {
            'username': self.username,
            'ua': self.ua
        }
        try:
            response = s.post(self.user_check_url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('检测是否需要验证码请求失败，原因：')
            raise e
        needcode = response.json()['needcode']
        print('是否需要滑块验证：{}'.format(needcode))
        return needcode

    def _verify_password(self):
        """
        验证用户名密码，并获取st码申请URL
        :return: 验证成功返回st码申请地址
        """
        verify_password_headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://login.taobao.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F%3Fspm%3Da1z02.1.1581860521.1.60c1782da2mXMb',
        }
        # 登录toabao.com提交的数据，如果登录失败，可以从浏览器复制你的form data
        verify_password_data = {
            'TPL_username': '15297122456',
            'ncoToken': 'f15d0d835c576d09f03c5d50c1790b4f3fdca9a2',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': 0,
            'newlogin': 0,
            'TPL_redirect_url': 'https://www.tmall.com/?ali_trackid=2:mm_26632258_3504122_48284354:1568771491_194_633735732&clk1=bf77ace2ec2c1d1ff954b7234067d409&upsid=bf77ace2ec2c1d1ff954b7234067d409',
            'from': 'tmall',
            'fc': 'default',
            'style': 'miniall',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'gvfdcname': '10',
            'gvfdcre': '68747470733A2F2F6C6F67696E2E746D616C6C2E636F6D2F3F73706D3D3837352E373933313833362F422E61323232366D7A2E312E32303138343236354D58396A617426726564697265637455524C3D68747470732533412532462532467777772E746D616C6C2E636F6D253246253346616C695F747261636B6964253344322533416D6D5F32363633323235385F333530343132325F3438323834333534253341313536383737313439315F3139345F363333373335373332253236636C6B31253344626637376163653265633263316431666639353462373233343036376434303925323675707369642533446266373761636532656332633164316666393534623732333430363764343039',
            'TPL_password_2': '8e9e1af2303788e26c6bf5232a30b8ea239ebf5639a3c5cb658c66324474cc78a0ed00fe6d30d657cc645b4b8e999f62ce834ba780f3619fcbb547c7a49c71f42cfb4fd5b8c6a811ee65a4ad818f686ddb46776174c1561cf6f0449841b5d711d01a46d39c2859c7e7ac26f3572a975ef10cb671d97c27eb4b19c5225be578f3',
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-CN',
            'sr': '1366*768',
            'naviVer': 'chrome|76.038091',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'osPF': 'Win32',
            'appkey': '00000000',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://www.taobao.com/?spm=a1z02.1.1581860521.1.60c1782da2mXMb&useMobile=true',
            'showAssistantLink': '',
            'um_token': 'https://login.taobao.com/member/login.jhtml?tpl_redirect_url=https://www.tmall.com/?ali_trackid=2:mm_26632258_3504122_48284354:1568771491_194_633735732&clk1=bf77ace2ec2c1d1ff954b7234067d409&upsid=bf77ace2ec2c1d1ff954b7234067d409&style=miniall&enup=true&newMini2=true&full_redirect=true&sub=true&from=tmall&allp=assets_css=3.0.10/login_pc.css&pms=1568771338972&useMobile=true',
            'ua': '120#bX1bSY9P6jbYAxp9jvYoSEbfbcL0/4yZ7kVmWRGn+el38yYPRMj5ZX/Jj2tV+2L5a/kiTh/vshoea4Tznt0OsYmi0t9ITBRl+UaVxImBPR+46FSn3D82TlfH6EkjZLJsnZcZuepnzqBfYwLGqmTfVfawYoHabyAGXaXpli7IIe6uOOOh2B3xWcwg7U0gZGOS2uuOBI5a80/r3woBcbTUsgfKY2c4Fthe8cjWLTfCA1UoewM6izX53IP2hCY5C2eozwi7gMqBjbAGHsN9v6po0EIbbB+pzyMPCIvSllGbP/hYy12b7UHBWOa/K1x22UMPDLlav54ACQeMPYxS76dPEWl/G1Vyia/PP8IbbaB0Nle/5U+bju3PPP0JbvSk4yMPPXISb5vpWc9yaVRPSjTxdoxVSxtkOyzBzUb6ivwp0XWm9nTpVJrRsaIX+qjroAKCo78j4gFtVyRFG5Z1zb14U+6nmbNhawHVOZiouh6bfpanNMd+trNTVVBjeOUWLe20w4+VaN7mPaSz1OIpT+TScElaaDbMD02EN4JVc60c8AgjBAvlhtylGRs6dw1HcLK5e+7zK0+F7XUbdxQRbyHylhnJTxpptRZB9LJf/Nc/PZNb/+GXc5sS3I1KyNk0NGb8LAI5DF5INzDsUgVr+UZ3jIhuhtNKk+ZA77rlxLssAm2AwnjnMhjy3V4rZoFwsPTzK3e/SKv1IAS0FmxNf/cadfpFIFNFRQ45kPk7jCKjUqNlaa+jvKxJReDlZ1gIdxBiovejP1YIMmpkE3Sy8xINbEh2msCj+UDM2IAbsa7F4CucLdWiXkJQmsUR/7UhyuE3SvXqI4bijnsfmh90EJGEYQFDpf3nRrRgtiK6lply7ZgJU1z7y7NxpIFhZdZrlKqIpVgoLn+MezFaYFWbmKXJpgoX9aM6vYqyp1N8o/RykIQc5vMn3r4WaazKUg6rchB9N0Rvx2Cphdgz1wsoAfp6tiGdmjz4EugAeBP0Jou3/1gYnJMIhqBdnilxrSTMElq7oopzp8I3H8TWSnFziZe2Kexv9h9TTeQMrrTG5tUTQc6+tChA0Cqm8FIZjgxZxKKtRW+oFuF3E/UbMT2etd0vPWEO8egTjWbJfl5eJbRk/Mn88jDBdHHG0zDyR0K7DNXPRgxdVe2CknF63RCXu+IzQJKlvx/PGluJba4jh5zoL7TIHkvDMFowP3z0kGij/8MylPdbnNywbH/WXMva5wRjEk7GYYwZoJQCm5m+L4aXiyulTI8F9zMWWS2gNsrTO5f4TRSXdEVtmO3WtThFQiYfPLeo+AMtHXO8h2xma5XOuMnOI/upPNkGLG3w+F2Wh7jvCVjQbB0ZgN1vhd/sFCw5RtcBGsHqQ+XmVp63BYP0KVZyjSmR7wU5atC48LGyApsXCvAXLBcj6YR7NXr6qy8hMWZPoX6hFkXpaGLR/E5XIILYuiNv29IFSzGDDJRKLW1e0/WQkKAG8q9097Qcdkur2hcxuO2e1fQ4P7EPE1=='
        }
        try:
            response = s.post(self.verify_password_url, headers=verify_password_headers, data=verify_password_data,
                              timeout=self.timeout)
            response.raise_for_status()
            # 从返回的页面中提取申请st码地址
        except Exception as e:
            print('验证用户名和密码请求失败，原因：')
            raise e
        # 提取申请st码url
        print(response.text)
        apply_st_url_match = re.search(r'<script src="(.*?)"></script>', response.text)
        # 存在则返回
        if apply_st_url_match:
            print('验证用户名密码成功，st码申请地址：{}'.format(apply_st_url_match.group(1)))
            return apply_st_url_match.group(1)
        else:
            raise RuntimeError('用户名密码验证失败！response：{}'.format(response.text))

    def _apply_st(self):
        """
        申请st码
        :return: st码
        """
        apply_st_url = self._verify_password()
        try:
            response = s.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申请st码请求失败，原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('获取st码成功，st码：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败！response：{}'.format(response.text))

    def login(self):
        """
        使用st码登录
        :return:
        """
        # 加载cookies文件
        if self._load_cookies():
            return True
        # 判断是否需要滑块验证
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = s.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录请求，原因：')
            raise e
        # 登录成功，提取跳转淘宝用户主页url
        my_taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if my_taobao_match:
            print('登录淘宝成功，跳转链接：{}'.format(my_taobao_match.group(1)))
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！response：{}'.format(response.text))

    def _load_cookies(self):
        # 1、判断cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        # 2、加载cookies
        s.cookies = self._deserialization_cookies()
        # 3、判断cookies是否过期
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载淘宝登录cookies成功!!!')
        return True

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(s.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):
        """
        获取淘宝昵称
        :return: 淘宝昵称
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = s.get(self.my_taobao_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('获取淘宝主页请求失败！原因：')
            raise e
        # 提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取淘宝昵称失败！response：{}'.format(response.text))


def getCookie():
    a = ''
    dict = {"_hvn_login": "0", "_tb_token_": "17456e3a53b1", "cookie2": "1faa649d3208a638eeea31267628be46",
            "csg": "329bf00a", "t": "d6698cc42cfad68c30cd3de90c943e56", "lc": "VyoFjLv40wbopTlWUKnWCD8%3D",
            "lid": "%E8%91%AC%E4%BB%AA%E4%B8%BF%E5%A4%9C%E7%A5%9E%E6%9C%88", "log": "lty=Tmc%3D",
            "havana_tgc": "eyJjcmVhdGVUaW1lIjoxNTY4NzcxOTA3MzQ0LCJsYW5nIjoiemhfQ04iLCJwYXRpYWxUZ2MiOnsiYWNjSW5mb3MiOnsiMCI6eyJhY2Nlc3NUeXBlIjoxLCJtZW1iZXJJZCI6MjY0NjU3NDAzNiwidGd0SWQiOiIxWDFRSllPeDFMOEQ0RE1KTlBvdUdrUSJ9fX19",
            "_cc_": "VT5L2FSpdA%3D%3D", "_l_g_": "Ug%3D%3D",
            "_nk_": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708",
            "cookie1": "BxpRR3m3mq6u2SKR8tMIAV5PbfT0Mkqa7hIMcGbyJO8%3D", "cookie17": "UU6lS5IHpNO1Zw%3D%3D",
            "dnk": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708", "existShop": "MTU2ODc3MTkwNw%3D%3D",
            "lgc": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708", "sg": "%E6%9C%886c",
            "skt": "4f11ce9635df5223", "tg": "0", "tracknick": "%5Cu846C%5Cu4EEA%5Cu4E3F%5Cu591C%5Cu795E%5Cu6708",
            "uc1": "cookie21=WqG3DMC9Fb5mPLIQo9kR&cookie15=URm48syIIVrSKA%3D%3D&pas=0&lng=zh_CN&existShop=false&cookie14=UoTaECEnuG%2F5FQ%3D%3D&cookie16=WqG3DMC9UpAPBHGz5QBErFxlCA%3D%3D&tag=8",
            "uc3": "lg2=VFC%2FuZ9ayeYq2g%3D%3D&nk2=tzejKGxa%2FgjcE9Gg&id2=UU6lS5IHpNO1Zw%3D%3D&vt3=F8dByuKxoy9YoE5ofXI%3D",
            "uc4": "id4=0%40U2xo%2B4EAVHijItFSb40x6HZvnZ%2B1&nk4=0%40tUQ6%2FECahntTXqHnI5ioot2jxOldGGA%3D",
            "unb": "2646574036", "XSRF-TOKEN": "327c5202-4796-40dc-87d2-f6309bf9eac2"}
    for i in dict:
        a += str(i) + '=' + str(dict[i]) + '; '
    cookie = a[:-2]
    return cookie


if __name__ == '__main__':
    # 淘宝用户名
    username = '15297122456'
    # 淘宝重要参数，从浏览器或抓包工具中复制，可重复使用
    ua = '120#bX1bSEVUxwh5On+s+1Yo7NYfbco0G0vV9igqXPMIaYyuBa5zvl0lRFRvYG3X2eDZdtzj7SmhAFaEvQhBrBMTcRISp7fOtOp1F6wkwJYg+pG922H721SyQoJ/i+P9Q+uwk6Kuy/6KLK4tsRQF2+7sQKdrb6YB17K8P2M9d/mmklY7OA8DRAuExo3Jva+hND8U+G9dh0KkCg5OaL3HLWZhGnHF5lURQs+VdJRChTF1nlB7n7Iu1Mzu06/747KHSvRpYv7nHOdxdDOEq+M0tteQFnWmNv2vTEI2b7/e+gMPvx/SjlO5P/hYy1Yb7U6YWexbNbx22UMP/Slxv54NiqeMPbbb7h4PEW0LEv5zuqPPPXIbbwFRPqPIiDFS7rPPWpi/AyhczC/PPXIbb27GYK/+JIG37g9Psypob8Vdoa/PPXIbb2FdEq/5L15Q75vPWWc/b2utTQMUiMkSbKMQNlP/ybbVAoxPNtaPzbYtipzPyyIbb56lNPe/y5+bi9dPyPc/bbbITXMPPXISb5vpWc9yaVjUSXpf6ZTVSxtkOyzBzh2YpHBWO4lfQFaj7JiMFtjVRojTbs/PTky8qBFgowtkPUwbWvCgrA/KCx94hTBVNKPh07huHh5C9DeSSLTeoQhc4adonopEMTZcSGcJywnF5aK41Ak91NxAXKqOqwPVDTNn8ScAwiHsVLuVS0ThYLxRRIoiB1ZipgG8Mmu3ZcZvsGDuROhdt7XOUXSqWK1sGJcV2+XS82AAB/lkrd4oa1r2SQkrybm+hQy37DyY9nbfEza+nGyDWSL0eFVxELVcrjwUgXeNJhQhECe49OGPK1SNVTyTfQJnDdqNW2FKyEcxWyP4kUlBb9ixn1k00qxslmIGiY26iUuVWMQDefoTQsnEcUBoVdRuIRzS8j2NYT9BCS+RTMsAWaxGNF9SICKBETYqKvpe3XjqZlt87K1YFxqgrSGIDmZRAOGFUUDfm8RIbXcosmP+BlBb9apnPBnynm4gXLau0WVmGXHx9xzTjf2Zp+sAdDclUJ69+gWGtXYH/G0kYhsqc1kgsr1zlK6yMansx0JAwQ02yzMucLF31XbOzqvXv2eXWnX9nELnPGKWaSBDm465pvLZZLIoG3oyKSp7048KpIaTESsr83LR+GpaZGH6ppI7FO6ySEbnxplEhxhCadfoPANty7n11yJolw/JUfOqc3aNEkG2RllT/PiasO/+2XQLQos1U7Jx8Aa+fztlPrU0UvKSLlfCYJUpxGYZxkIGa3GZ7MNJx1tn4tA5PrCukBA8cO2zfqGptW8RLa80jDLxdx1SsmgqF+yxvXqEAbyGkQn='
    # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
    TPL_password2 = '88a71d84b2462815581e11c8ef44422348a120899de6837325f520540cbf0f16b0d74bde290333cf02b25996dc9fae504aec5daf4321d736907eb07d9423d21ce541c91ecc86faa9e043a3fd13e7fb0be756a0e2f471b81e9b2d4728516ad209304766b01e1aa79cfd279aa8601535e144f218af2dd1a9bc565a2d978d656ad4'
    ul = UsernameLogin(username, ua, TPL_password2)
    ul.login()
