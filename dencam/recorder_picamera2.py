import logging
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from datetime import datetime
import os
import time
from dencam.recorder import Recorder

log = logging.getLogger(__name__)


class Picam2:
    def __init__(self, configs):
        self.configs = configs
        self.encoder = H264Encoder()
        
        self.camera = Picamera2()
        self.camera.preview_configuration.enable_lores()
        self.camera.preview_configuration.lores.size = (320, 240)
        self.camera.configure("preview")
        self.camera.start_preview(Preview.NULL)
        self.camera.start()

    def start_preview(self):
        self.camera.stop_preview()
        self.camera.start_preview(Preview.QT, x=-4, y=-25, width=324, height=245)
        log.info('Started Preview')

    def stop_preview(self):
        self.camera.stop_preview()
        self.camera.start_preview(Preview.NULL)
        log.info('Stopped Preview')


    def start_recording(self, filename, quality=None):
        self.camera.start_recording(self.encoder, filename)
        log.info('Started Recording: ' + filename)

    def stop_recording(self):
        self.camera.stop_recording()
        log.info('Stopped Recording"')

class Picamera2Recorder(Recorder):
    """Recorder that uses picamera2

    """
    def __init__(self, configs):
        super().__init__(configs)
        log.info('Set up camera per configurations')
        self.camera = Picam2(configs)
        self.configs = configs

        super().finish_setup()
