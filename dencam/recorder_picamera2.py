"""Recorder classes for picamera2-based systems.

Implements derived class from the recorder.Recorder class intended to
work on systems (i.e. lesehest) using picamera2 instead of the
original picamera.  Implements other pieces of related functionality.

"""
import logging
import time
import collections

from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview, MappedArray
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from dencam.recorder import Recorder
from dencam.calculations import calculate_blur

log = logging.getLogger(__name__)

GRID_SIZE = 5
TEXT_SIZE = 50
ALPHA_VALUE = 150
HISTORY_LENGTH = 15


def draw_timestamp(size, draw):
    """Draw current timestamp onto a frame.

    Args:
        size (tuple of int): The resolution of the frame
        draw (pillow.ImageDraw.Draw): The drawing object
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    font_size = 30
    text_color = (255, 255, 255)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        font_size
    )
    bg_color = (0, 0, 0)

    bbox = draw.textbbox((0, 0), timestamp, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding = 10
    img_width, _ = size
    text_x = (img_width - text_width) // 2
    text_y = 10

    draw.rectangle(
        [text_x - padding // 2,
         text_y,
         text_x + text_width + padding // 2,
         text_y + text_height + padding],
        fill=bg_color
    )

    draw.text((text_x, text_y),
              timestamp,
              fill=text_color,
              font=font)


class Picam2:
    """Class for initializing picamera2 and following recorder.py api."""

    def __init__(self, configs):
        self.configs = configs
        self.encoder = H264Encoder()

        self.camera = Picamera2()
        self.camera.configure("preview")
        self.camera.start_preview(Preview.NULL)
        self.camera.start()

    def draw_focus_score_display(self,
                                 image,
                                 draw,
                                 grid_dim,
                                 variance_history,
                                 font_size,
                                 font_transparency):
        """Calculate and render focus scores.

        For each grid element in a grid laid out over the video frame,
        calculates the focus score value (filtered over a frame
        window) and renders their display onto image.

        Args:
            image (pillow.Image): The current frame
            draw (pillow.ImageDraw.Draw): The drawing object
            grid_dim (int): The number of cells per row/column for the
                grid overlay.
            variance_history (list): 2D list of deque buffers storing
                variance history for each grid cell.
            font_size (int): The font size for the score text.
            font_transparency (int): The alpha transparency for overlay text.

        """
        gray_image = image.convert('L')

        width, height = self.camera.camera_configuration()['main']['size']
        block_height, block_width = height//grid_dim, width//grid_dim

        # Load a default font with the specified text size
        font = ImageFont.truetype(
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                   font_size)

        for i in range(grid_dim):
            for j in range(grid_dim):
                gray_array = np.array(gray_image)
                block = gray_array[i*block_height:(i+1)*block_height,
                                   j*block_width:((j+1)*block_width)-1]

                variance = calculate_blur(block)

                variance_history[i][j].append(variance)
                avg_variance = np.mean(variance_history[i][j])

                # Round variance to nearest ones digit
                avg_variance = int(avg_variance)

                x1_pos, y1_pos = j * block_width, i * block_height
                x2_pos, y2_pos = x1_pos + block_width, y1_pos + block_height

                color = (0, 0, 0)  # Change as needed for visible text
                draw.rectangle([x1_pos, y1_pos, x2_pos - 1, y2_pos - 1],
                               outline=color + (255,),
                               width=1)

                text = f"{avg_variance}"

                # Position text in center of each box
                center_x = x1_pos + block_width // 2
                center_y = y1_pos + block_height // 2

                draw.text(
                    (center_x, center_y),
                    text,
                    fill=color + (font_transparency,),
                    font=font,
                    anchor="mm"
                    )

    def start_preview(self):
        """Stop null preview, start QT preview and log."""
        self.camera.stop_preview()
        self.camera.start_preview(Preview.QT,
                                  x=0,
                                  y=-30,
                                  width=320,
                                  height=240)
        log.info('Started Preview')

    def stop_preview(self):
        """Stop preview, start null preview and log."""
        self.camera.stop_preview()
        self.camera.start_preview(Preview.NULL)
        log.info('Stopped Preview')

    def start_recording(self, filename, quality=None):
        """Start recording and log.

        Args:
            filename (str): The path to write the recording video to
            quality (): NOT YET MADE USE OF
        """
        # pylint: disable=unused-argument
        self.camera.start_recording(self.encoder, filename)
        log_message = 'Started Recording: ' + str(filename)
        log.info(log_message)

    def stop_recording(self):
        """Stop recording and log."""
        self.camera.stop_recording()
        log.info('Stopped Recording"')


class Picamera2Recorder(Recorder):
    """Recorder that uses picamera2."""

    def __init__(self, configs):
        super().__init__(configs)
        log.info('Set up camera per configurations')
        self.camera = Picam2(configs)
        self.configs = configs

        self.history_buffer = [[collections.deque(maxlen=HISTORY_LENGTH)
                                for _ in range(GRID_SIZE)]
                               for _ in range(GRID_SIZE)]

        super().finish_setup()

    def update_timestamp(self):
        """Update timestamp display.

        In reality other rendering onto preview and video is done in
        this method but retains this name for legacy compatibility.

        """
        self.camera.camera.pre_callback = self._draw_overlay

    def _draw_overlay(self, request):
        """Render overlay on video and preview.

        Renders the timestamp onto the frames of the video. Or, if
        focus score display enabled, draws that display instead.

        This method relies on the .pre_callback method
        from picamera2 docs, which applies the overlay onto
        all screens. This means the preview contains the same
        overlay. The entire implementation would need to change
        if only one stream was to have an overlay.

        Args:
            request ():

        """
        with MappedArray(request, "main") as streams:
            image = Image.fromarray(streams.array)
            draw = ImageDraw.Draw(image)
            if self.focus_score_on:
                self.camera.draw_focus_score_display(image,
                                                     draw,
                                                     GRID_SIZE,
                                                     self.history_buffer,
                                                     TEXT_SIZE,
                                                     ALPHA_VALUE)
            else:
                draw_timestamp(image.size, draw)
            streams.array[:] = np.array(image)

    def toggle_zoom(self):
        """Toggle cropping into video."""
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
