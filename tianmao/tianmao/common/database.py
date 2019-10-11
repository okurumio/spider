import pymongo


def db():
    client = pymongo.MongoClient('localhost', 27017)
    db_name = 'tianmao'
    return client[db_name]


def saveList():
    db().goodsList.insert()