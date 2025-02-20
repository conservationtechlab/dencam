"""Redefining picamera2 class to fit into recorder.py

"""
import logging
import time
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview, MappedArray
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import collections
from scipy.ndimage import laplace

from dencam.recorder import Recorder

log = logging.getLogger(__name__)


def draw_timestamp(size, draw):
    """Draw current timestamp onto a frame

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
    """Class for initializing picamera2 and following recorder.py api

    """
    def __init__(self, configs):
        self.configs = configs
        self.encoder = H264Encoder()

        self.camera = Picamera2()
        self.camera.configure("preview")
        self.camera.start_preview(Preview.NULL)
        self.camera.start()

    def detect_blur(self, image_array):
        """
        Computes the blur variance for an image array using the
        Laplacian method.

        Args:
            image_array (numpy.ndarray): Grayscale image array to analyze.

        Returns:
            float: Variance of the Laplacian, where a lower variance
            indicates more blur.
        """
        laplacian_result = laplace(image_array)
        return laplacian_result.var()


    def update_frame(self, image_array, grid_dim, variance_history,
                     font_size, font_transparency):
        """
        Updates each frame by calculating and overlaying blur
        variance values for each cell in a grid.

        Args:
            image_array (numpy.ndarray): The PiCamera2 object for video capture.
            grid_dim (int): Number of cells per row/column for the
            grid overlay.
            variance_history (list): 2D list of deque buffers storing
            variance history for each grid cell.
            font_size (int): Font size for the overlay text.
            font_transparency (int): Alpha transparency for overlay text.

        Returns:
            numpy.ndarray: Updated overlay with the new blur
            variance display.
        """
        gray_image = Image.fromarray(image_array).convert('L')

        width, height = self.camera.camera_configuration()['main']['size']
        block_height, block_width = height//grid_dim, width//grid_dim

        overlay_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay_img)

        # Load a default font with the specified text size
        font = ImageFont.truetype(
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                   font_size)

        for i in range(grid_dim):
            for j in range(grid_dim):
                gray_array = np.array(gray_image)
                block = gray_array[i*block_height:(i+1)*block_height,
                                   j*block_width:((j+1)*block_width)-1]

                variance = self.detect_blur(block)

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

        return np.array(overlay_img)

    def focus_score(self, focus_score_on):
        """Toggle focus score overlay

        """
        grid_size = 5
        text_size = 50
        text_alpha = 150
        resolution = (640, 480)
        N=15
        history_buffer = [[collections.deque(maxlen=N)
                          for _ in range(grid_size)]
                          for _ in range(grid_size)]

        while focus_score_on == True:
            image = self.camera.capture_array()

            overlay = self.update_frame(image,
                                        grid_size,
                                        history_buffer,
                                        text_size,
                                        text_alpha)
            self.camera.set_overlay(overlay)


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
        with MappedArray(request, "main") as streams:
            image = Image.fromarray(streams.array)
            draw = ImageDraw.Draw(image)
            draw_timestamp(image.size, draw)
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
