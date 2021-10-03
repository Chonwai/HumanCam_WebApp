from flask import Flask, render_template, Response
import cv2
import socket
import zmq
import sys
import base64
import numpy as np

app = Flask(__name__)

# camera = cv2.VideoCapture(0)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)


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
    context = zmq.Context()

    socket = context.socket(zmq.PULL)
    socket.connect("tcp://127.0.0.1:5555")

    while True:
        response = socket.recv()
        frameBase64 = response.decode('utf-8')
        nparr = np.fromstring(base64.b64decode(frameBase64), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/people_in')
def people_in():
    # Video streaming route. Put this in the src attribute of an img tag
    yield "10"



@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(fetchFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
