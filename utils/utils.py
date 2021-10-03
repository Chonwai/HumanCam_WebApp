import numpy as np
import cv2
import base64

class Utils:
    @staticmethod
    def convertBase64Frame2Frame(base64Frame):
        nparr = np.fromstring(base64.b64decode(base64Frame), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return frame
