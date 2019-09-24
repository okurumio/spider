from coin import getTasks
import time, datetime
from coin.tasks import btc123, hecaijing, huoxun, huoxing24, bitkan
from apscheduler.schedulers.background import BackgroundScheduler


def job_func():
    try:
        btc123.run()
    except:
        print("btc123错误")
    try:
        hecaijing.run()
    except:
        print("hecaijing错误")
    try:
        huoxun.run()
    except:
        print("huoxun错误")
    try:
        huoxing24.run()
    except:
        print("huoxing24错误")
    try:
        bitkan.run()
    except:
        print("bitkan错误")


def test():
    print(datetime.datetime.now())


def Scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_func, 'interval', seconds=3600)
    scheduler.start()
    while True:
        print(datetime.datetime.now())
        time.sleep(600)


if __name__ == '__main__':
    # job_func()
    Scheduler()