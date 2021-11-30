import numpy as np
import cv2
import csv
import base64
import datetime
from os.path import exists
from datetime import datetime
import redis
import os
import pandas as pd


r = redis.Redis(host='redis', port=6379, decode_responses=True)


class Utils:
    @staticmethod
    def convertBase64Frame2Frame(base64Frame):
        nparr = np.fromstring(base64.b64decode(base64Frame), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return frame

    @staticmethod
    def checkReportExists(header):
        if not exists('storage/report/{filename}.csv'.format(filename=datetime.now().strftime("%Y-%m-%d"))):
            with open('storage/report/{filename}.csv'.format(filename=datetime.now().strftime("%Y-%m-%d")), 'w+', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)
                
    @staticmethod
    def getPeopleIn():
        if not exists('storage/report/{filename}.csv'.format(filename=datetime.now().strftime("%Y-%m-%d"))):
            return 0;
        else:
            df = pd.read_csv(os.path.join('storage/report/{filename}.csv'.format(filename=datetime.now().strftime("%Y-%m-%d"))))
            lastPeopleIn = df[-1:]['people_in']
            return int(lastPeopleIn)
        
    @staticmethod
    def getPeopleOut():
        if not exists('storage/report/{filename}.csv'.format(filename=datetime.now().strftime("%Y-%m-%d"))):
            return 0;
        else:
            df = pd.read_csv(os.path.join('storage/report/{filename}.csv'.format(filename=datetime.now().strftime("%Y-%m-%d"))))
            lastPeopleOut = df[-1:]['people_out']
            return int(lastPeopleOut)
