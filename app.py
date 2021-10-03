from flask import Flask, render_template, Response
import cv2
import socket
import zmq
import time
import base64
import numpy as np
import threading
from utils import utils

app = Flask(__name__)

base64Frame = ''


def getFrames():
    global base64Frame
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://127.0.0.1:5555")

    while True:
        response = socket.recv()
        base64Frame = response.decode('utf-8')


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
        time.sleep(0.5)
        frame = utils.Utils.convertBase64Frame2Frame(base64Frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


# def fetchPeopleIn():
#     peopleIn = 1
#     yield peopleIn


# @app.route('/people_in')
# def people_in():
#     # Video streaming route. Put this in the src attribute of an img tag
#     return Response(fetchPeopleIn(), mimetype='text/html')
#     # yield "10"


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(fetchFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    for i in range(5):
        peopleInData = i
        time.sleep(1)
    return render_template('index.html', peopleIn=peopleInData)


if __name__ == '__main__':
    frameThread = threading.Thread(target=getFrames)
    frameThread.start()
    app.run(debug=True)
