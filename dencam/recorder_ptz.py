"""Recorder class and related for PTZ camera

The classes needed for interfacing with a PTZ network surveillance
camera as the recording device for a dencam.

"""
import os
import time
import logging
import subprocess
import multiprocessing as mp

import cv2
# TODO: i think we should consider *not* using ptzipcam.camera.Camera
# We should consider just using a cv2.VideoCapture object directly or
# maybe even ffmpeg directly via subprocess. We do not need so many
# layers, especially given ptzipcam.camera.Camera has its own thread
# and a very thin amount of wrapping around cv2.VideoCapture.
# Although, also might be worth considering adding a lightweight
# ptzipcam.camera.LightweightCamera that still encapsulates all the
# ptz-ish setup stuff in that package but doesn't run its own camera
# checking thread.
from ptzipcam.camera import Camera

from dencam.recorder import Recorder
from dencam.joystick import PTZController

log = logging.getLogger(__name__)

WINDOW_NAME = "DenCam Mimir View"


class MimirCamera:
    """High-level PTZ camera class

    Wraps a ptzipcam.camera.Camera to match API expected by rest of
    DenCam

    """
    def __init__(self, configs):
        self.configs = configs

        self.rotation = 0
        self.resolution = None
        self._crop = (0, 0, 1.0, 1.0)

        # This next attribute was necessary for drawing timestamp in
        # picamera version.  Not really necessary for Mimir because
        # the network camera has own capability to draw that timestamp
        # built in.  We will keep it to match Fenrir attributes
        self.annotate_text = None

        self.stop_display_event = mp.Event()
        self.stop_record_event = mp.Event()
        self.stop_joystick_event = mp.Event()

    @property
    def zoom(self):
        """Getter for crop box tuple

        """
        return self._crop

    @zoom.setter
    def zoom(self, value):
        self._crop = value
        self._on_zoom_change()

    def _on_zoom_change(self):
        self.stop_preview()
        self.start_preview()

    def _orient_frame(self, frame, rotation):
        if rotation == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        return frame

    def _joystick(self, configs, event):
        ptz_controller = PTZController(configs)
        while not event.is_set():
            ptz_controller.run_joystick()

        ptz_controller.release_joystick()
            
    def _display(self, configs, event):
        cam = Camera(ip=configs['CAMERA_IP'],
                     user=configs['CAMERA_USER'],
                     passwd=configs['CAMERA_PASS'],
                     stream=configs['CAMERA_STREAM'])

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
        cv2.setWindowProperty(WINDOW_NAME,
                              cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
        cv2.moveWindow(WINDOW_NAME, 0, -30)
        cv2.resizeWindow(WINDOW_NAME, 320, 240)
        
        while not event.is_set():
            frame = cam.get_frame()
            if frame is not None:
                x_norm, y_norm, width_norm, height_norm = self._crop
                x_pixels = int(x_norm * frame.shape[1])
                y_pixels = int(y_norm * frame.shape[0])
                width_pixels = int(width_norm * frame.shape[1])
                height_pixels = int(height_norm * frame.shape[0])
                cropped_region = frame[y_pixels:y_pixels + height_pixels,
                                       x_pixels:x_pixels + width_pixels]
                cropped_region = self._orient_frame(cropped_region,
                                                    self.rotation)
                cv2.imshow(WINDOW_NAME, cropped_region)
                cv2.waitKey(33)
        cv2.destroyAllWindows()
        cam.release()

    def start_preview(self):
        """Start display of camera stream to screen

        """
        self.stop_display_event.clear()
        display_worker = mp.Process(target=self._display,
                                    args=(self.configs, self.stop_display_event))
        display_worker.start()

        self.stop_joystick_event.clear()
        joystick_worker = mp.Process(target=self._joystick,
                            args=(self.configs, self.stop_joystick_event))
        joystick_worker.start()

    def stop_preview(self):
        """Stop display of cam stream

        """
        self.stop_display_event.set()
        self.stop_joystick_event.set()

    def _check_resolution(self, resolution):
        """Warn if a resolution doesn't match self.resolution

        Unlike with Fenrir, as of now, we are not using the resolution
        configuration parameter to set the camera stream
        resolution. It is possible to do this over ONVIF but, for the
        time being at least, we configure this directly on the camera
        using its web interface as we don't tend to change the value
        that often.

        However, this check issues a warning if the setting in the
        config file doesn't match what the camera is actual set to.

        """
        log.info("Camera Resolution: %s", resolution)
        if not self.resolution == list(resolution):
            log.warning("Camera stream not set to expected resolution")
            log.warning("Config Resolution Setting: %s", self.resolution)

    def _record(self, filename, configs, event):

        # TODO: no longer using `self._check_resolution here or
        # anywhere. Should we try to get the resolution from the
        # ffmpeg process and check on that.  Alternatively, we use
        # ONVIF to write the desired resolution to the camera ala how
        # it used to work with the picamera.

        # TODO: not using frame rotation config to re-orient the frame
        # anymore since switch to ffmpeg

        camip = configs['CAMERA_IP'],
        usr = configs['CAMERA_USER'],
        passw = configs['CAMERA_PASS'],
        stream = configs['CAMERA_STREAM']

        url = f"rtsp://{usr}:{passw}@{camip}:554/Streaming/Channels/10{stream}"
        cmd = ["ffmpeg", "-i", url, "-acodec", "copy",
               "-vcodec", "copy", filename, "-nostdin"]
        process = subprocess.Popen(cmd)

        while not event.is_set():
            time.sleep(.01)

        process.terminate()

    def start_recording(self, filename, quality=None):
        """Start recording camera stream to video

        """
        # TODO: what to with the quality argument?

        # first strip off and replace the .h264 extension that current
        # recorder is providing
        # TODO: maybe make base Recorder object not assume the .h264
        # extension?
        base = os.path.splitext(filename)[0]
        filename = f"{base}.mp4"

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

    def release(self):
        """Clean up any running processes

        """
        log.info("MimirCamera releasing mp processes")
        self.stop_preview()
        self.stop_recording()


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

        super().finish_setup()

    def release(self):
        self.camera.release()
