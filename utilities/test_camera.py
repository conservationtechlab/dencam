"""Program that tests basic functioning of a pi camera.

Records approximately 30 seconds of video to a file named test.h264.
"""

import time
from picamera import PiCamera

camera = PiCamera()

camera.rotation = 180

camera.start_recording('test.h264')
time.sleep(30)
camera.stop_recording()
