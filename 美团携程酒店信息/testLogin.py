
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
    tel = '123'  # 手机号
    sendCode(tel)
    code = input("请输入验证码:")
    token = checkCode(code, tel)
    auth = login(token)
    print(auth)
