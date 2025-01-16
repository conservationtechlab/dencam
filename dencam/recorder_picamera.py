"""Picamera-based recorder classes

"""
import logging
import picamera
from picamera import PiCamera

from dencam.recorder import Recorder

log = logging.getLogger(__name__)


class PicameraRecorder(Recorder):
    """Recorder that uses a picamera

    """
    def __init__(self, configs):
        super().__init__(configs)

        # camera setup
        log.info('Set up camera per configurations')
        self.camera = PiCamera(framerate=configs['FRAME_RATE'])
        text_size = int((1/20) * configs['CAMERA_RESOLUTION'][1])
        self.camera.annotate_text_size = text_size
        self.camera.annotate_foreground = picamera.color.Color('white')
        self.camera.annotate_background = picamera.color.Color('black')

        super().finish_setup()

    def toggle_zoom(self, zoom_on, zoom_factor):
        """Toggle zoom in and out

        """
        if not zoom_on:
            width, _ = self.camera.resolution
            zoom_factor = self.configs['DISPLAY_RESOLUTION'][0]/width
            left = 0.5 - zoom_factor/2.
            top = 0.5 - zoom_factor/2.
            self.camera.zoom = (left, top, zoom_factor, zoom_factor)
        else:
            self.camera.zoom = (0, 0, 1.0, 1.0)
