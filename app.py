from time import sleep
from flask import Flask, render_template, Response
import cv2
import zmq
import numpy as np
import threading
import json
import time
from utils import utils
from flask_caching import Cache
from config.cacha import config
import redis

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
r = redis.Redis(host='redis', port=6379, decode_responses=True)
r.set('people_in', 0)
r.set('people_out', 0)
r.set('base64HumanCounterFrame', '')
r.set('base64AgeGenderFrame', '')


lastPeopleIn = 0
lastPeopleOut = 0
startTime = time.time()


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


def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def fetchHumanCounterFrames():
    while True:
        sleep(0.5)
        frame = utils.Utils.convertBase64Frame2Frame(
            r.get('base64HumanCounterFrame'))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def fetchAgeGenderFrames():
    while True:
        sleep(0.5)
        frame = utils.Utils.convertBase64Frame2Frame(
            r.get('base64AgeGenderFrame'))
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
    HumanCounterframeThread = threading.Thread(target=getHumanCounterFrames)
    ageGenderFrameThread = threading.Thread(target=getAgeGenderFrame)
    HumanCounterframeThread.start()
    ageGenderFrameThread.start()
    app.run(debug=True, host='0.0.0.0', port=8888)
