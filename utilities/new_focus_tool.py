#!/usr/bin/env python
# coding: utf-8

# In[11]:


import time
import picamera
from picamera.array import PiRGBArray
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import yaml
import cv2
import collections

def load_config(config_file='config.yaml'):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def detect_blur(image_array): 
    laplacian_result = cv2.Laplacian(image_array, cv2.CV_64F) 
    variance_of_laplacian = laplacian_result.var() 
    return variance_of_laplacian


def update_frame(camera, overlay, grid_size, threshold, history_buffer):
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        
        
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_array = np.array(gray_frame)

        height, width = image_array.shape
        block_height = height // grid_size
        block_width = width // grid_size

        
        overlay_img = Image.new('RGBA', camera.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay_img)

        for i in range(grid_size):
            for j in range(grid_size):
                block = image_array[i*block_height:(i+1)*block_height, j*block_width:((j+1)*block_width)-1]
                variance = detect_blur(block)
                
                history_buffer[i][j].append(variance)
                
                avg_variance=np.mean(history_buffer[i][j])

                x1, y1 = j * block_width, i * block_height
                x2, y2 = x1 + block_width, y1 + block_height

                   
#                 color = (255, 0, 0) if avg_variance < threshold else (0, 255 ,0)
                color = (0, 0, 0) 

                
                draw.rectangle([x1, y1, x2, y2], outline=color + (255,), width=2)

                
                draw.text(((x1 + x2) // 2, (y1 + y2) // 2), f"{int(avg_variance)}", fill=color + (255,))

        
        img_bytes = overlay_img.tobytes()

        
        new_overlay = camera.add_overlay(img_bytes, format='rgba', size=overlay_img.size, layer=3, alpha=128)

        
        if overlay:
            camera.remove_overlay(overlay)
        
        overlay = new_overlay

        rawCapture.truncate(0)

        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    return overlay

# Main code
if __name__ == "__main__":
    config = load_config()

    
    grid_size = config.get('grid_size', 4)
    threshold = config.get('threshold', 150)
    
    
    #create a history buffer to store te variance value
    N=15
    history_buffer = [[collections.deque(maxlen=N) for _ in range(grid_size)] for _ in range(grid_size)]

    
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        camera.start_preview()
        
        time.sleep(1)  

        overlay = None
        try:
            overlay = update_frame(camera, overlay, grid_size, threshold, history_buffer)
        finally:
            if overlay:
                camera.remove_overlay(overlay)



# In[ ]:




