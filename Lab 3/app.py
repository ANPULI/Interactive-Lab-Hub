from flask import Flask, render_template, Response, request, g
import cv2
import os
from threading import Thread
from queue import Queue
from speak import speak
from record import record

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # use 0 for web camera
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


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

#background process happening without any refreshing
@app.route('/empty')
def empty():
    print("Empty")
    # os.system('echo "The bowl is empty! Please refill it." | festival --tts')
    g.status_flag = 0
    return 

@app.route('/refill')
def refill():
    print("Refill")
    # os.system('echo "woof woof. Come eat." | festival --tts')
    g.status_flag = 1
    return 

@app.route('/', methods=['GET', 'POST'])
def index():
    check_flag = Queue()
    g.status_flag = 0
    t1 = Thread(target=record, args=(check_flag, ))
    t2 = Thread(target=speak, args=(check_flag, g.status_flag, ))
    t1.start()
    t2.start()
    """Video streaming home page."""
    return render_template('index.html', status_flag=g.status_flag)



if __name__ == '__main__':
    app.run(debug=True)