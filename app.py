from flask import Flask, render_template, Response
import cv2
import zmq
import numpy as np
import threading
import json
from utils import utils

app = Flask(__name__)

base64Frame = ''
peopleIn = 0
peopleOut = 0


def getFrames():
    global base64Frame, peopleIn, peopleOut
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://127.0.0.1:5555")

    while True:
        response = json.loads(socket.recv())
        base64Frame = response['frame'].split("'")[1]
        peopleIn = response['peopleIn']
        peopleOut = response['peopleOut']
        # time.sleep(0.1)


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
