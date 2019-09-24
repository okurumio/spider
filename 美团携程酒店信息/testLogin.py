
# import requests
# url = 'https://passport.ctrip.com/gateway/api/soa2/11448/checkPhoneCode.json'
# json = {"AccountHead":{},
#         "Data":
#             {"messageCode":"S200078",
#              "code":"114986",
#              "countryCode":"86",
#              "mobilePhone":"13613575930"},
#         "head":
#             {}}
# headers = {
#     'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16E227 NebulaSDK/1.8.100112 Nebula WK PSDType(0) AlipayDef',
#     'Referer': 'https://2017081708237081.hybrid.alipay-eco.com/2017081708237081/0.2.1904232103.32/index.html#pages/accounts/login?__appxPageId=110&__navigator=6'
# }
# r = requests.post(url,json=json,headers=headers)
# print(r.text)

# DA60D63B05CB13838E319647B8C057A9058266D0A83800B91E31AC867474534F

# url = 'https://passport.ctrip.com/gateway/api/soa2/12559/userLogin.json'
# json1 = {"AccountHead":{},
#         "Data":
#             {"accessCode":"B6CE8D84FEBBFC0E",
#              "strategyCode":"85D4BB47E79522CA",
#              "loginName":"",
#              "certificateCode":"DA60D63B05CB13838E319647B8C057A9058266D0A83800B91E31AC867474534F"},
#         "head":{}}
# headers = {
#     'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16E227 NebulaSDK/1.8.100112 Nebula WK PSDType(0) AlipayDef',
#     'Referer': 'https://2017081708237081.hybrid.alipay-eco.com/2017081708237081/0.2.1904232103.32/index.html#pages/accounts/login?__appxPageId=110&__navigator=6'
# }
# r = requests.post(url, json=json1, headers=headers)
# print(r.text)
# F2BF55DA779037C874B72EB2AE7F6DB59C0416EFFB87706D378538E83BB2244F
# F2BF55DA779037C874B72EB2AE7F6DB5DFA17E274740D2603A83474D7F78542D
import requests
import json

headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16E227 NebulaSDK/1.8.100112 Nebula WK PSDType(0) AlipayDef',
        'Referer': 'https://2017081708237081.hybrid.alipay-eco.com/2017081708237081/0.2.1904232103.32/index.html#pages/accounts/login?__appxPageId=110&__navigator=6'
    }


def sendCode(tel):
    url = 'https://passport.ctrip.com/gateway/api/soa2/11448/sendMessageByPhoneLogin.json'
    json1 = {"AccountHead":
         {"ImageCaptcha":
              {"Signature":"",
               "CaptchaId":""}},
     "Data":{"messageCode":"S200078",
             "CountryCode":"86",
             "MobilePhone":tel,
             "sendScene":"SMS-LOGIN-SITE",
             "CheckMobilePhoneNumber":"NoCheck",
             "extension":[]},
     "head":{}}

    r = requests.post(url, json=json1, headers=headers)
    print(r.text)


def checkCode(code, tel):
    url = 'https://passport.ctrip.com/gateway/api/soa2/11448/checkPhoneCode.json'
    json1 = {"AccountHead":{},
            "Data":
                {"messageCode":"S200078",
                 "code":code,
                 "countryCode":"86",
                 "mobilePhone":tel},
            "head":
                {}}
    r = requests.post(url, json=json1, headers=headers)
    data = json.loads(r.text)
    print(data)
    token = json.loads(data['Result'])['token']
    return token


def login(token):
    url = 'https://passport.ctrip.com/gateway/api/soa2/12559/userLogin.json'
    json1 = {"AccountHead": {},
             "Data":
                 {"accessCode": "B6CE8D84FEBBFC0E",
                  "strategyCode": "85D4BB47E79522CA",
                  "loginName": "",
                  "certificateCode": token},
             "head": {}}
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16E227 NebulaSDK/1.8.100112 Nebula WK PSDType(0) AlipayDef',
        'Referer': 'https://2017081708237081.hybrid.alipay-eco.com/2017081708237081/0.2.1904232103.32/index.html#pages/accounts/login?__appxPageId=110&__navigator=6'
    }
    r = requests.post(url, json=json1, headers=headers)
    data = json.loads(r.text)
    print(data)
    auth = json.loads(data['Result'])['ticket']
    return auth


if __name__ == '__main__':
    # tel = '13520197084'
    # sendCode(tel)
    # code = input("请输入验证码:")
    # token = checkCode(code, tel)
    # print(token)
    auth = login('725296CCA65F8334ED263F93FC6D842C01C110483DCD61C3669032B3314F88AE')
    print(auth)

# 725296CCA65F8334ED263F93FC6D842C01C110483DCD61C3669032B3314F88AE