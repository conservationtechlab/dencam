"""Redefining picamera2 class to fit into recorder.py

"""
import logging
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview, MappedArray
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time

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

    def update_timestamp(self):
        self.camera.camera.pre_callback = self._pre_callback_wrapper

    def _pre_callback_wrapper(self, request):
        """ Wrapper function to call update_timestamp without needing to pass request
        """
        self.timestamp(request)

    def timestamp(self, request):
        font_size = 35
        text_color = (255, 255, 255)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        bg_color = (0, 0, 0)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        with MappedArray(request, "main") as m:
            image = Image.fromarray(m.array)
            draw = ImageDraw.Draw(image)

            bbox = draw.textbbox((0, 0), timestamp, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            img_width, img_height = image.size
            text_x = (img_width - text_width) // 2
            text_y = 10

            draw.rectangle(
                [text_x, text_y, text_x + text_width, text_y + text_height],
                fill=bg_color
            )

            draw.text((text_x, text_y), timestamp, fill=text_color, font=font)

            m.array[:] = np.array(image)
