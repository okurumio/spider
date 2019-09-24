import redis  # 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库


class OPRedis(object):
    def __init__(self):
        if not hasattr(OPRedis, 'pool'):
            OPRedis.getRedisCoon()  # 创建redis连接
        self.coon = redis.Redis(connection_pool=OPRedis.pool)

    @staticmethod
    def getRedisCoon():
        OPRedis.pool = redis.ConnectionPool(host='114.55.84.165', password='FNldn.dgdj,gDN,34md', port=6379, db=0)

    # 判断表类型
    def typeredis(self, key):
        res = self.coon.type(key).decode()
        return res

    """
    string类型 {'key':'value'} redis操作
    """

    def setredis(self, key, value, time=None):
        # 非空即真非0即真
        if time:
            res = self.coon.setex(key, value, time)
        else:
            res = self.coon.set(key, value)
        return res

    def getRedis(self, key):
        res = self.coon.get(key).decode()
        return res

    def delRedis(self, key):
        res = self.coon.delete(key)
        return res

    """
    hash类型，{'name':{'key':'value'}} redis操作
    """

    def setHashRedis(self, name, key, value):
        res = self.coon.hset(name, key, value)
        return res

    def getHashRedis(self, name, key=None):
        # 判断key是否我为空，不为空，获取指定name内的某个key的value; 为空则获取name对应的所有value
        if key:
            res = self.coon.hget(name, key)
        else:
            res = self.coon.hgetall(name)
        return res

    def delHashRedis(self, name, key=None):
        if key:
            res = self.coon.hdel(name, key)
        else:
            res = self.coon.delete(name)
        return res

    # 获取set　集合数据
    def gethsetRedis(self, key):
        res = self.coon.smembers(key)
        datas = []
        for data in res:
            datas.append(data.decode())
        return datas

    def randomOneIp(self, key):
        res = self.coon.srandmember(key, 1)[0].decode()
        return res
if __name__ == '__main__':
    coon = OPRedis()
    # datas = coon.gethsetRedis('proxy:new_ip_list')
    # data = coon.typeredis('proxy:new_ip_list')
    # print(data)
    datas = coon.randomOneIp('proxy:new_ip_list')
    print(datas)