from utils.utils import Utils
import schedule
import time
from datetime import datetime
import redis
from csv import DictWriter
import uuid


r = redis.Redis(host='redis', port=6379, decode_responses=True)


class ScheduleService:
    @staticmethod
    def job():
        r.set('people_in', 0)
        r.set('people_out', 0)

    @staticmethod
    def updateDailyReport():
        header = ['id', 'people_in', 'people_out', 'created_at']
        row = {'id': uuid.uuid4(), 'people_in': int(float(r.get('people_in'))),
               'people_out': int(float(r.get('people_out'))), 'created_at': datetime.now()}
        Utils.checkReportExists(header)
        with open('storage/report/{filename}.csv'.format(filename=datetime.now().strftime("%Y-%m-%d")), 'a+', newline='') as writeObj:
            dictWriter = DictWriter(writeObj, fieldnames=header)
            dictWriter.writerow(row)


def dashboardSchedule():
    schedule.every().hour.do(ScheduleService.updateDailyReport)
    schedule.every().day.at("00:00").do(ScheduleService.job)
    while True:
        schedule.run_pending()
        time.sleep(1)
