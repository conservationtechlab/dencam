"""Tool to examine focus in view of Mini Den Cam.

Number displayed in each grid element of a grid (grid defaults to 4x4)
can be used to judge focus for the grid element and in aggregate for
the scene.  The number's value is a function of both the degree of
focus *and* complexity of what is in view within that grid element so
it has to be treated as a relative focus tool i.e. as focus is
adjusted on the lens, the number will peak at best focus (provided
view is unchanged) but that peak could be a very different number for
one scene versus another.

"""

import io
import argparse

import cv2
import picamera
import numpy as np
from screeninfo import screeninfo

parser = argparse.ArgumentParser()
parser.add_argument('-r',
                    '--rows',
                    default=4,
                    help='number of rows in grid. 8 can be nice.')
parser.add_argument('-c',
                    '--cols',
                    default=4,
                    help='number of columns in grid. 8 can be nice.')
args = parser.parse_args()


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


monitor = screeninfo.get_monitors()
display_width = monitor[0].width
display_height = monitor[0].height

stream = io.BytesIO()
camera = picamera.PiCamera()
camera.rotation = 180

cv2.namedWindow('out', cv2.WINDOW_NORMAL)
cv2.resizeWindow('out', int(display_width * .9), int(display_height * .9))


for _ in camera.capture_continuous(stream, format='jpeg'):
    stream.truncate()
    stream.seek(0)
    data = np.frombuffer(stream.getvalue(),
                         dtype=np.uint8)
    frame = cv2.imdecode(data, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    num_cols = int(args.cols)
    num_rows = int(args.rows)
    sector_width = int(width/num_cols)
    sector_height = int(height/num_rows)

    for i in range(num_cols):
        for j in range(num_rows):
            left = int(sector_width * i)
            right = left + sector_width
            top = int(sector_height * j)
            bottom = top + sector_height

            sector = gray[top:bottom, left:right]

            cv2.rectangle(frame,
                          (left + 2, top + 2),
                          (right - 2, bottom - 2),
                          (255, 0, 0))

            fm = variance_of_laplacian(sector)
            cv2.putText(frame,
                        '{:.0f}'.format(fm),
                        (left + 10, top + 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        2)
    cv2.imshow('out', frame)
    key = cv2.waitKey(30)
    if key == ord('q'):
        break
