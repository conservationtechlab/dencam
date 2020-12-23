import os
import time

from datetime import datetime
from picamera import PiCamera

DEFAULT_PATH = '/home/pi/'


class Recorder():
    def __init__(self, configs):
        self.record_start_time = time.time()  # also used in initial countdown

        # Recording settings
        self.video_path = configs['VIDEO_PATH']

        # PiTFT characteristics
        self.DISPLAY_RESOLUTION = configs['DISPLAY_RESOLUTION']

        # Camera settings
        CAMERA_RESOLUTION = configs['CAMERA_RESOLUTION']
        CAMERA_ROTATION = configs['CAMERA_ROTATION']
        FRAME_RATE = configs['FRAME_RATE']

        self.VIDEO_QUALITY = configs['VIDEO_QUALITY']

        self.initial_pause_complete = False

        # camera setup
        self.camera = PiCamera(framerate=FRAME_RATE)
        self.camera.rotation = CAMERA_ROTATION
        self.camera.resolution = CAMERA_RESOLUTION
        self.preview_on = False
        self.zoom_on = False
        # recording setup
        self.recording = False

        self.vid_count = 0

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def toggle_zoom(self):
        if not self.zoom_on:
            width, height = self.camera.resolution
            # zoom_factor = 1/float(ZOOM_FACTOR)
            zoom_factor = self.DISPLAY_RESOLUTION[0]/width
            left = 0.5 - zoom_factor/2.
            top = 0.5 - zoom_factor/2.
            self.camera.zoom = (left, top, zoom_factor, zoom_factor)
        else:
            self.camera.zoom = (0, 0, 1.0, 1.0)
        self.zoom_on = not self.zoom_on

    def toggle_preview(self):
        if not self.preview_on:
            self.camera.start_preview()
        else:
            self.camera.stop_preview()
        self.preview_on = not self.preview_on

    def start_recording(self):
        self.recording = True
        self.vid_count += 1

        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")

        if not os.path.exists(self.video_path):
            strg = ("ERROR: Video path broken. " +
                    "Recording to {}".format(DEFAULT_PATH))
            self.error_label['text'] = strg
            self.video_path = DEFAULT_PATH
            print("[ERROR] Video path doesn't exist. "
                  + "Writing files to /home/pi")

        todays_dir = os.path.join(self.video_path, date_string)

        if not os.path.exists(todays_dir):
            os.makedirs(todays_dir)
        date_time_string = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        filename = os.path.join(todays_dir, date_time_string + '.h264')
        self.camera.start_recording(filename, quality=self.VIDEO_QUALITY)
        self.record_start_time = time.time()

    def stop_recording(self):
        self.recording = False
        self.camera.stop_recording()
