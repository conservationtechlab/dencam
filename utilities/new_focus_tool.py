#!/usr/bin/env python
# coding: utf-8

# In[2]:


import time
import collections
import picamera
from picamera.array import PiRGBArray
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import yaml
import cv2
"""
Real-time blur detection tool for Raspberry Pi with PiCamera.

This module captures video frames from the PiCamera, divides each frame into grid cells,
and calculates a blur variance score for each cell. An overlay grid displays the blur score
on top of the live camera feed, with transparency and text options loaded from a configuration file.
"""

def load_config(config_file='config.yaml'):
    """
    Loads configuration settings from a YAML file.

    Parameters:
    config_file (str): Path to the configuration YAML file. Defaults to 'config.yaml'.

    Returns:
    dict: Configuration settings loaded from the file.
    """
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def detect_blur(image_array):
    """
    Computes the blur variance for an image array using the Laplacian method.

    Parameters:
    image_array (numpy.ndarray): Grayscale image array to analyze.

    Returns:
    float: Variance of the Laplacian, where a lower variance indicates more blur.
    """
    laplacian_result = cv2.Laplacian(image_array, cv2.CV_64F)
    variance_of_laplacian = laplacian_result.var()
    return variance_of_laplacian

def update_frame(camera, overlay, grid_size, threshold, 
                 history_buffer, text_size, text_alpha):
    """
    Updates each frame by calculating and overlaying blur variance values for each cell in a grid.

    Parameters:
    camera (PiCamera): The PiCamera object for video capture.
    overlay (PiOverlayRenderer): Previous overlay to be updated or removed.
    grid_size (int): Number of cells per row/column for the grid overlay.
    threshold (int): Blur threshold value (currently unused).
    history_buffer (list): 2D list of deque buffers storing variance history for each grid cell.
    text_size (int): Font size for the overlay text.
    text_alpha (int): Alpha transparency for overlay text.

    Returns:
    PiOverlayRenderer: Updated overlay with the new blur variance display.
    """
    raw_capture = PiRGBArray(camera, size=camera.resolution)

    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        image = frame.array
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_array = np.array(gray_frame)

        height, width = image_array.shape
        block_height = height // grid_size
        block_width = width // grid_size

        overlay_img = Image.new('RGBA', camera.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay_img)

        # Load a default font with the specified text size
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", text_size)

        for i in range(grid_size):
            for j in range(grid_size):
                block = image_array[i*block_height:(i+1)*block_height,
                                    j*block_width:((j+1)*block_width)-1]
                variance = detect_blur(block)
                
                history_buffer[i][j].append(variance)
                avg_variance = np.mean(history_buffer[i][j])
                
                # Round to the nearest tens digit
                avg_variance = int(round(avg_variance, -1))

                x1_pos, y1_pos = j * block_width, i * block_height
                x2_pos, y2_pos = x1_pos + block_width, y1_pos + block_height

                color = (0, 0, 0)  # Change as needed for visible text
                draw.rectangle([x1_pos, y1_pos, x2_pos, y2_pos], outline=color + (255,), width=1)
                
                text = f"{avg_variance}"
                text_width, text_height = draw.textsize(text, font=font)  # Calculate text size

                # Calculate center position of the text
                center_x = (x1_pos + x2_pos) // 2 - text_width // 2
                center_y = (y1_pos + y2_pos) // 2 - text_height // 2

                draw.text(
                    (center_x, center_y),
                    text,
                    fill=color + (text_alpha,),
                    font=font
                )

        img_bytes = overlay_img.tobytes()

        new_overlay = camera.add_overlay(img_bytes,
                                         format='rgba',
                                         size=overlay_img.size,
                                         layer=3,
                                         alpha=128)

        if overlay:
            camera.remove_overlay(overlay)

        overlay = new_overlay

        raw_capture.truncate(0)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    return overlay

# Main code
if __name__ == "__main__":
    """
    Main function to initialize the camera and start the real-time blur detection overlay.

    This function loads configuration settings, initializes a history buffer for blur values,
    and continuously updates the overlay with the current frame's blur variance in each grid cell.
    """
    config = load_config()

    grid_size = config.get('grid_size', 4)
    threshold = config.get('threshold', 150)
    text_size = config.get('text_size', 20)
    text_alpha = config.get('text_alpha', 128)

    # Create a history buffer to store the variance value
    N = 15
    history_buffer = [[collections.deque(maxlen=N) for _ in range(grid_size)] for _ in range(grid_size)]

    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        camera.start_preview()

        time.sleep(1)

        overlay = None
        try:
            overlay = update_frame(camera,
                                   overlay,
                                   grid_size,
                                   threshold,
                                   history_buffer, 
                                   text_size,
                                   text_alpha)
        finally:
            if overlay:
                camera.remove_overlay(overlay)



# In[ ]:




