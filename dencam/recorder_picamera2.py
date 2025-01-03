"""Redefining picamera2 class to fit into recorder.py

"""
import logging
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview
from libcamera import controls

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
        self.camera.preview_configuration.lores.size = (640, 480)
        self.camera.configure("preview")
        self.camera.start_preview(Preview.NULL)
        self.camera.start()
        metadata = self.camera.capture_metadata()
        print("metadata: " + str(metadata))
    def start_preview(self):
        """Stop null preview, start QT preview and log

        """
        self.camera.stop_preview()
        self.camera.start_preview(Preview.QT,
                                  x=-4,
                                  y=-30,
                                  width=640,
                                  height=480)
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

    def toggle_zoom(self, zoom_on):
        """Toggle zoom

        """
        if not zoom_on:
            size = self.camera.capture_metadata()['ScalerCrop'][2:]

            full_res = self.camera.camera_properties['PixelArraySize']

            for _ in range(20):
                self.camera.capture_metadata()

                size = [int(s * 0.95) for s in size]
                offset = [(r - s) // 2 for r, s in zip(full_res, size)]
                self.camera.set_controls({"ScalerCrop": offset + size})
        else:
            size = self.camera.capture_metadata()['ScalerCrop'][2:]
            full_res = self.camera.camera_properties['PixelArraySize']

            for _ in range(20):
                self.camera.capture_metadata()
                size = [int(s * 1.05) for s in size]
                size = [min(s, r) for s, r in zip(size, full_res)]
                offset = [(r - s) // 2 for r, s in zip(full_res, size)]
                self.camera.set_controls({"ScalerCrop": offset + size})
            self.camera.set_controls({"ScalerCrop": [0, 0] + list(full_res)})


class Picamera2Recorder(Recorder):
    """Recorder that uses picamera2

    """
    def __init__(self, configs):
        super().__init__(configs)
        log.info('Set up camera per configurations')
        self.camera = Picam2(configs)
        self.configs = configs

        super().finish_setup()
