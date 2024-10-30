"""Recorder class and related for PTZ camera

The classes that 

"""
import logging
import multiprocessing as mp

import cv2
from ptzipcam.camera import Camera

from dencam.recorder import Recorder

log = logging.getLogger(__name__)


class CyclopsCamera:
    """High-level PTZ camera class

    Wraps a ptzipcam.camera.Camera to match API expected by rest of
    DenCam

    """
    def __init__(self, configs):
        self.configs = configs
        
        self.rotation = 0  # TODO: doesn't control anything yet
        self.resolution = 1  # TODO: doesn't control anything yet
        self.zoom = (0, 0, 1.0, 1.0)  # TODO: doesn't control anything yet

        self.window_name = "DenCam View"

        self.stop_display_event = mp.Event()

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
                cv2.imshow(self.window_name, frame)
                cv2.waitKey(33)
        cv2.destroyAllWindows()
        
    def start_preview(self):
        self.stop_display_event.clear()
        worker = mp.Process(target=self._display,
                            args=(self.stop_display_event,))
        worker.start()

    def stop_preview(self):
        self.stop_display_event.set()

    def annotate_text(self):
        raise NotImplemented

    def start_recording(self):
        raise NotImplemented

    def stop_recording(self):
        raise NotImplemented
        

class PTZRecorder(Recorder):
    """Recorder that uses a pan-tilt-zoom network surveillance camera

    """
    def __init__(self, configs):
        super().__init__(configs)

        # camera setup
        log.info('Set up camera per configurations')

        self.camera = CyclopsCamera(configs)
        # self.camera = PiCamera(framerate=configs['FRAME_RATE'])
        # text_size = int((1/20) * configs['CAMERA_RESOLUTION'][1])
        # self.camera.annotate_text_size = text_size
        # self.camera.annotate_foreground = picamera.color.Color('white')
        # self.camera.annotate_background = picamera.color.Color('black')

        # super().finish_setup()
