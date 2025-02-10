"""Redefining picamera2 class to fit into recorder.py

"""
import logging
import time
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview, MappedArray
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from dencam.recorder import Recorder

log = logging.getLogger(__name__)


class Picam2:
    """Class for initializing picamera2 and following recorder.py api

    """
    def __init__(self, configs):
        self.configs = configs
        self.encoder = H264Encoder()

        self.camera = Picamera2()
        self.camera.configure("preview")
        self.camera.start_preview(Preview.NULL)
        self.camera.start()

    def start_preview(self):
        """Stop null preview, start QT preview and log

        """
        self.camera.stop_preview()
        self.camera.start_preview(Preview.QT,
                                  x=0,
                                  y=-30,
                                  width=320,
                                  height=240)
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
        # pylint: disable=unused-argument
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
        self.camera.camera.pre_callback = self.timestamp

    def timestamp(self, request):
        """Update timestamp on video and preview

        This method relies on the .pre_callback method
        from picamera2 docs, which applies the overlay onto
        all screens. This means the preview contains the same
        overlay. The entire implementation would need to change
        if only one stream was to have an overlay.

        """
        font_size = 30
        text_color = (255, 255, 255)
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            font_size
        )
        bg_color = (0, 0, 0)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        with MappedArray(request, "main") as streams:
            image = Image.fromarray(streams.array)
            draw = ImageDraw.Draw(image)

            bbox = draw.textbbox((0, 0), timestamp, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            padding = 10
            img_width, _ = image.size
            text_x = (img_width - text_width) // 2
            text_y = 10

            draw.rectangle(
                [text_x - padding // 2,
                 text_y,
                 text_x + text_width + padding // 2,
                 text_y + text_height + padding],
                fill=bg_color
            )

            draw.text((text_x, text_y), timestamp, fill=text_color, font=font)

            streams.array[:] = np.array(image)

    def toggle_zoom(self):
        """Toggle zoom

        """
        num_crop_steps = 25

        size = self.camera.camera.capture_metadata()['ScalerCrop'][2:]
        full_res = self.camera.camera.camera_properties['PixelArraySize']

        for _ in range(num_crop_steps):
            self.camera.camera.capture_metadata()

            if not self.zoom_on:
                size = [int(s * 0.95) for s in size]
            else:
                size = [int(s * 1.05) for s in size]
                size = [min(s, r) for s, r in zip(size, full_res)]

            offset = [(r - s) // 2 for r, s in zip(full_res, size)]
            self.camera.camera.set_controls({"ScalerCrop": offset + size})

        # make sure is fully zoomed out
        if self.zoom_on:
            bot_right = list(full_res)
            self.camera.camera.set_controls({"ScalerCrop": [0, 0] + bot_right})

        self.zoom_on = not self.zoom_on
