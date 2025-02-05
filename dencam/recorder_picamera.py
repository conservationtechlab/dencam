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
