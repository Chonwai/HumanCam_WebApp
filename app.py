from flask import Flask, render_template, Response
from service.schedule import dashboardSchedule
import zmq
import numpy as np
import threading
import json
from time import sleep
from utils import utils
from config.cacha import config
import redis


app = Flask(__name__)
app.config.from_mapping(config)
r = redis.Redis(host='redis', port=6379, decode_responses=True)
r.set('people_in', 0)
r.set('people_out', 0)
r.set('base64HumanCounterFrame', '')
r.set('base64AgeGenderFrame', '')


lastPeopleIn = 0
lastPeopleOut = 0


def getHumanCounterFrames():
    global lastPeopleIn, lastPeopleOut
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://yolo:5555")

    while True:
        response = json.loads(socket.recv())
        if response['peopleIn'] == 0 and response['peopleOut'] == 0:
            lastPeopleIn = 0
            lastPeopleOut = 0
        r.set('base64HumanCounterFrame', response['frame'].split("'")[1])
        currentPeopleIn = response['peopleIn']
        currentPeopleOut = response['peopleOut']
        if (currentPeopleIn - lastPeopleIn) != 0 or (currentPeopleOut - lastPeopleOut) != 0:
            print("Temp In: " + str(currentPeopleIn - lastPeopleIn))
            print("Temp Out: " + str(currentPeopleOut - lastPeopleOut))
            r.set('people_in', float(r.get('people_in')) +
                  ((currentPeopleIn - lastPeopleIn) / 2))
            r.set('people_out', float(r.get('people_out')) +
                  ((currentPeopleOut - lastPeopleOut) / 2))
        lastPeopleIn = currentPeopleIn
        lastPeopleOut = currentPeopleOut


def getAgeGenderFrame():
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://agd:5556")

    response = json.loads(socket.recv())

    while True:
        response = json.loads(socket.recv())
        r.set('base64AgeGenderFrame', response['frame'].split("'")[1])
        

def fetchHumanCounterFrames():
    while True:
        sleep(0.5)
        if (r.get('base64HumanCounterFrame') != ''):
            frame = utils.Utils.convertBase64Frame2Frame(r.get('base64HumanCounterFrame'))
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def fetchAgeGenderFrames():
    while True:
        sleep(0.5)
        if (r.get('base64AgeGenderFrame') != ''):
            frame = utils.Utils.convertBase64Frame2Frame(r.get('base64AgeGenderFrame'))
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/people_in')
def people_in():
    res = float(r.get('people_in'))
    return str(int(res))


@app.route('/people_out')
def people_out():
    res = float(r.get('people_out'))
    return str(int(res))


@app.route('/people_flow')
def people_flow():
    peopleFlow = int(float(r.get('people_in')) + float(r.get('people_out')))
    return str(peopleFlow)


@app.route('/human_counter_video_feed')
def human_counter_video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(fetchHumanCounterFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/age_gender_video_feed')
def age_gender_video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(fetchAgeGenderFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    humanCounterframeThread = threading.Thread(target=getHumanCounterFrames)
    ageGenderFrameThread = threading.Thread(target=getAgeGenderFrame)
    dashboardScheduleThread = threading.Thread(target=dashboardSchedule)
    humanCounterframeThread.start()
    ageGenderFrameThread.start()
    dashboardScheduleThread.start()
    app.run(debug=True, host='0.0.0.0', port=8888)
