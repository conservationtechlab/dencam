"""Recorder class and related for PTZ camera

The classes needed for interfacing with a PTZ network surveillance
camera as the recording device for a dencam.

"""
import os
import time
import logging
import multiprocessing as mp

import cv2
from ptzipcam.camera import Camera

from dencam.recorder import Recorder

log = logging.getLogger(__name__)


class MimirCamera:
    """High-level PTZ camera class

    Wraps a ptzipcam.camera.Camera to match API expected by rest of
    DenCam

    """
    def __init__(self, configs):
        self.configs = configs

        self.rotation = 0
        self.resolution = 1  # TODO: doesn't control anything yet
        self._crop = (0, 0, 1.0, 1.0)

        # This next attribute was necessary for drawing timestamp in
        # picamera version.  Not really necessary for Mimir because
        # the network camera has own capability to draw that timestamp
        # built in.  We will keep it to match Fenrir attributes
        self.annotate_text = None

        self.window_name = "DenCam Mimir View"

        self.stop_display_event = mp.Event()
        self.stop_record_event = mp.Event()

    @property
    def zoom(self):
        return self._crop

    @zoom.setter
    def zoom(self, value):
        self._crop = value
        self.on_zoom_change()

    def on_zoom_change(self):
        self.stop_preview()
        self.start_preview()

    def orient_frame(self, frame, rotation):
        if rotation == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)

    def _display(self, configs, event):
        cam = Camera(ip=configs['CAMERA_IP'],
                     user=configs['CAMERA_USER'],
                     passwd=configs['CAMERA_PASS'],
                     stream=configs['CAMERA_STREAM'])

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)
        cv2.setWindowProperty(self.window_name,
                              cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
        cv2.moveWindow(self.window_name, 0, -30)
        cv2.resizeWindow(self.window_name, 320, 240)

        while not event.is_set():
            frame = cam.get_frame()
            if frame is not None:
                x_norm, y_norm, width_norm, height_norm = self._crop
                x = int(x_norm * frame.shape[1])
                y = int(y_norm * frame.shape[0])
                width = int(width_norm * frame.shape[1])
                height = int(height_norm * frame.shape[0])
                cropped_region = frame[y:y + height, x:x + width]
                self.orient_frame(cropped_region, self.rotation)
                cv2.imshow(self.window_name, cropped_region)
                cv2.waitKey(33)
        cv2.destroyAllWindows()
        cam.release()

    def start_preview(self):
        """Start display of camera stream to screen

        """
        self.stop_display_event.clear()
        worker = mp.Process(target=self._display,
                            args=(self.configs, self.stop_display_event))
        worker.start()

    def stop_preview(self):
        """Stop display of cam stream

        """
        self.stop_display_event.set()

    def _record(self, filename, configs, event):
        cam = Camera(ip=configs['CAMERA_IP'],
                     user=configs['CAMERA_USER'],
                     passwd=configs['CAMERA_PASS'],
                     stream=configs['CAMERA_STREAM'])

        frame = cam.get_frame()
        resolution = (frame.shape[1], frame.shape[0])
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(filename,
                                 fourcc,
                                 30.0,
                                 resolution)

        self.orient_frame(frame, self.rotation)
        writer.write(frame)

        while not event.is_set():
            # TODO: there are definitely problems in the frame timing
            time.sleep(0.03333333333)
            frame = cam.get_frame()
            if frame is None:
                log.warning("Frame was None")
            else:
                self.orient_frame(frame, self.rotation)
                writer.write(frame)

    def start_recording(self, filename, quality=None):
        """Start recording camera stream to video

        """
        # TODO: what to with the quality argument?

        # first strip off and replace the .h264 extension that current
        # recorder is providing
        # TODO: maybe make base Recorder object not assume the .h264
        # extension?
        base = os.path.splitext(filename)[0]
        filename = f"{base}.avi"

        self.stop_record_event.clear()
        worker = mp.Process(target=self._record,
                            args=(filename,
                                  self.configs,
                                  self.stop_record_event))
        worker.start()

    def stop_recording(self):
        """Stop recording of camera video

        """
        self.stop_record_event.set()


class PTZRecorder(Recorder):
    """Recorder that uses a pan-tilt-zoom network surveillance camera

    """
    def __init__(self, configs):
        super().__init__(configs)

        # camera setup
        log.info('Set up camera per configurations')

        self.camera = MimirCamera(configs)
        # self.camera = PiCamera(framerate=configs['FRAME_RATE'])
        # text_size = int((1/20) * configs['CAMERA_RESOLUTION'][1])
        # self.camera.annotate_text_size = text_size
        # self.camera.annotate_foreground = picamera.color.Color('white')
        # self.camera.annotate_background = picamera.color.Color('black')

        # super().finish_setup()
