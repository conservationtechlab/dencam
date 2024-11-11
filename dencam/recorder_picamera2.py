"""Redefining picamera2 class to fit into recorder.py

"""
import logging
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview

from dencam.recorder import Recorder

log = logging.getLogger(__name__)


class Picam2:
    """Class for initializing picamera2 and following recorder.py api

    """
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
        """Stop null preview, start QT preview and log

        """
        self.camera.stop_preview()
        self.camera.start_preview(Preview.QT,
                                  x=-4,
                                  y=-25,
                                  width=324,
                                  height=245)
        log.info('Started Preview')

    def stop_preview(self):
        """Stop preview, start null preview and log

        """
        self.camera.stop_preview()
        self.camera.start_preview(Preview.NULL)
        log.info('Stopped Preview')

    def start_recording(self, filename, quality=None):
        """Start recording and log

        """
        self.camera.start_recording(self.encoder, filename)
        log_message = 'Started Recording: ' + str(filename)
        log.info(log_message)

    def stop_recording(self):
        """Stop recording and log

        """
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
