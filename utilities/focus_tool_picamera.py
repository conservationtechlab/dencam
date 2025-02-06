#!/usr/bin/env python
# coding: utf-8


"""
Real-time blur detection tool for Raspberry Pi with PiCamera.

This module captures video frames from the PiCamera, divides
each frame into grid cells,and calculates a blur variance score
for each cell. An overlay grid displays the blur scoreon top of
the live camera feed, with transparency and text options loaded
from a configuration file.
"""

import time
import collections
import picamera
from picamera.array import PiRGBArray
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import yaml
import cv2


def load_config(config_file='config.yaml'):
    """
    Loads configuration settings from a YAML file.

    Parameters:
    config_file (str): Path to the configuration YAML file.
    Defaults to 'config.yaml'.

    Returns:
    dict: Configuration settings loaded from the file.
    """

    with open(config_file, 'r', encoding='utf8') as file:
        return yaml.safe_load(file)


def detect_blur(image_array):
    """
    Computes the blur variance for an image array using
    the Laplacian method.

    Parameters:
    image_array (numpy.ndarray): Grayscale image array
    to analyze.

    Returns:
    float: Variance of the Laplacian, where a lower
    variance indicates more blur.
    """

    laplacian_result = cv2.Laplacian(image_array, cv2.CV_64F)
    variance_of_laplacian = laplacian_result.var()
    return variance_of_laplacian


def update_frame(camera, overlay_frame, grid_dim,
                 variance_history, font_size, font_transparency):
    """
    Updates each frame by calculating and overlaying blur
    variance values for each cell in a grid.

    Parameters:
    camera (PiCamera): The PiCamera object for video capture.
    overlay (PiOverlayRenderer): Previous overlay to be updated
        or removed.
    grid_dim (int): Number of cells per row/column for the
       grid overlay.
    variance_history (list): 2D list of deque buffers storing
        variance history for each grid cell.
    font_size (int): Font size for the overlay text.
    font_transparency (int): Alpha transparency for overlay text.

    Returns:
    PiOverlayRenderer: Updated overlay with the new blur
        variance display.
    """

    raw_capture = PiRGBArray(camera, size=camera.resolution)

    for frame in camera.capture_continuous(raw_capture,
                                           format="bgr",
                                           use_video_port=True):
        image = frame.array
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_array = np.array(gray_frame)

        height, width = image_array.shape
        block_height = height // grid_dim
        block_width = width // grid_dim

        overlay_img = Image.new('RGBA', camera.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay_img)

        # Load a default font with the specified text size
        font = ImageFont.truetype(
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   font_size)

        for i in range(grid_dim):
            for j in range(grid_dim):
                block = image_array[i*block_height:(i+1)*block_height,
                                    j*block_width:((j+1)*block_width)-1]
                variance = detect_blur(block)

                variance_history[i][j].append(variance)
                avg_variance = np.mean(variance_history[i][j])

                # Round to the nearest tens digit
                avg_variance = int(round(avg_variance, -1))

                x1_pos, y1_pos = j * block_width, i * block_height
                x2_pos, y2_pos = x1_pos + block_width, y1_pos + block_height

                color = (0, 0, 0)  # Change as needed for visible text
                draw.rectangle([x1_pos, y1_pos, x2_pos, y2_pos],
                               outline=color + (255,),
                               width=1)

                text = f"{avg_variance}"

                # Calculate text size
                text_width, text_height = draw.textsize(text, font=font)

                # Calculate center position of the text
                center_x = (x1_pos + x2_pos) // 2 - text_width // 2
                center_y = (y1_pos + y2_pos) // 2 - text_height // 2

                draw.text(
                    (center_x, center_y),
                    text,
                    fill=color + (font_transparency,),
                    font=font
                )

        img_bytes = overlay_img.tobytes()

        new_overlay = camera.add_overlay(img_bytes,
                                         format='rgba',
                                         size=overlay_img.size,
                                         layer=3,
                                         alpha=128)

        if overlay_frame:
            camera.remove_overlay(overlay_frame)

        overlay_frame = new_overlay

        raw_capture.truncate(0)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    return overlay_frame


# Main code
if __name__ == "__main__":

    # Load Configuration
    config = load_config()

    grid_size = config.get('grid_size', 4)
    threshold = config.get('threshold', 150)
    text_size = config.get('text_size', 20)
    text_alpha = config.get('text_alpha', 128)

    # Create a history buffer to store the variance value
    N = 15
    history_buffer = [[collections.deque(maxlen=N)
                      for _ in range(grid_size)]
                      for _ in range(grid_size)]

    with picamera.PiCamera() as picam:
        picam.resolution = (640, 480)
        picam.framerate = 30
        picam.start_preview()

        time.sleep(1)

        overlay = None
        try:
            overlay = update_frame(picam,
                                   overlay,
                                   grid_size,
                                   history_buffer,
                                   text_size,
                                   text_alpha)
        finally:
            if overlay:
                picam.remove_overlay(overlay)
