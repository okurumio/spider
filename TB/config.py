cookie = input("输入cookie")

headers = {
    'accept-encoding': 'gzip, deflate, br',
    'cookie': cookie,
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
}

MONGO_HOST = "192.168.0.12"
MONGO_PORT = 40000
MONGO_DB = "node"
MONGO_COLL = "dsManualData3"