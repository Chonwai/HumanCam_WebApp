from time import sleep
from flask import Flask, render_template, Response
import cv2
import zmq
import numpy as np
import threading
import json
import time
from utils import utils

app = Flask(__name__)

base64Frame = ''
peopleIn = 0
peopleOut = 0
lastPeopleIn = 0
lastPeopleOut = 0
startTime = time.time()


def getFrames():
    global base64Frame, peopleIn, peopleOut
    global lastPeopleIn, lastPeopleOut
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://127.0.0.1:5555")

    # print("People In Start! " + str(peopleIn))
    # print("People Out Start! " + str(peopleOut))

    response = json.loads(socket.recv())

    while True:
        if response['peopleIn'] == 0 and response['peopleOut'] == 0:
            # print("All 0!")
            lastPeopleIn = 0
            lastPeopleOut = 0
        response = json.loads(socket.recv())
        base64Frame = response['frame'].split("'")[1]
        currentPeopleIn = response['peopleIn']
        currentPeopleOut = response['peopleOut']
        peopleIn = peopleIn + (currentPeopleIn - lastPeopleIn)
        peopleOut = peopleOut + (currentPeopleOut - lastPeopleOut)
        # print('Response PeopleIn: ' +
        #       str(response['peopleIn']) + ' Global People In: ' + str(peopleIn) + ' Current People In: ' + str(currentPeopleIn) + ' Last People In: ' + str(lastPeopleIn) + ' Current - Last: ' + str(currentPeopleIn - lastPeopleIn))
        lastPeopleIn = currentPeopleIn
        lastPeopleOut = currentPeopleOut


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


def fetchFrames():
    global base64Frame
    while True:
        sleep(0.5)
        frame = utils.Utils.convertBase64Frame2Frame(base64Frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/people_in')
def people_in():
    global peopleIn
    # Video streaming route. Put this in the src attribute of an img tag
    return str(peopleIn)


@app.route('/people_out')
def people_out():
    global peopleOut
    # Video streaming route. Put this in the src attribute of an img tag
    return str(peopleOut)


@app.route('/people_flow')
def people_flow():
    global peopleIn, peopleOut
    peopleFlow = peopleIn + peopleOut
    # Video streaming route. Put this in the src attribute of an img tag
    return str(peopleFlow)


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(fetchFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    frameThread = threading.Thread(target=getFrames)
    frameThread.start()
    app.run(debug=True, host='0.0.0.0', port=8888)
