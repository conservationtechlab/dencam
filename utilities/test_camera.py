"""Test basic functioning of the picamera.

Test script to verify basic functioning of the picamera which is the
camera of the DenCam system, i.e. to make sure it is mechanically
connected properly, that all the picamera tools are installed, that
the camera itself is functioning etc.

The script records approximately 30 seconds of video to a file named
test.h264.

"""

import time
from picamera import PiCamera

camera = PiCamera()

camera.rotation = 180

camera.start_recording('test.h264')
time.sleep(30)
camera.stop_recording()
