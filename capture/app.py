# taken from: https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00

import logging
from datetime import datetime
from pathlib import Path

import cv2
import cvzone
import numpy as np
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from flask import Flask, Response, render_template, request

app = Flask(__name__)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

path_data = Path(__file__).parent.parent / "gallery/snapshots"

frame_width, frame_height = 640, 480

camera = cv2.VideoCapture(0)
camera.set(3, frame_width)  # 3=width, 4=height
camera.set(4, frame_height)

segmentor = SelfiSegmentation(model=0)

random_state = np.random.RandomState(987234)

factor = 100
threshold = 0.1
bkg_rate = 30

save_snapshot = False


def to_gamma_rays(frame):
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = random_state.poisson((frame + bkg_rate) / factor).astype("uint8") * factor
    return cv2.applyColorMap(frame, cv2.COLORMAP_INFERNO)


def save_frame(frame):
    now = datetime.now().strftime("%m-%d-%y-%H-%M-%S")
    filename = path_data / f"snapshot-{now}.jpg"
    log.info(f"Saving frame to {filename}")
    cv2.imwrite(str(filename), frame)


def capture_frames():
    while True:
        success, img = camera.read()  # read the camera frame
        if not success:
            break
        else:
            global save_snapshot

            frame = segmentor.removeBG(img, imgBg=(0, 0, 0), cutThreshold=threshold)
            frame = to_gamma_rays(frame)

            if save_snapshot:
                save_frame(frame)
                save_snapshot = False

            frame = cvzone.stackImages([img, frame], cols=2, scale=1)

            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )  # concat frame one by one and show result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/requests", methods=["POST", "GET"])
def tasks():
    if request.method == "POST":
        if request.form.get("snapshot") == "Snapshot":
            global save_snapshot
            save_snapshot = True

    elif request.method == "GET":
        return render_template("index.html")

    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        capture_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(debug=True)
