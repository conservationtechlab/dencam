#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
new_focus_tool to detect the blur level
'''
import cv2
import numpy as np


def detect_blur(image_array): 
    laplacian_result = cv2.Laplacian(image_array, cv2.CV_64F) 
    variance_of_laplacian = laplacian_result.var() 
    return variance_of_laplacian


def update_frame():
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image_array = np.array(gray_frame)

        height, width = image_array.shape
        block_height = height // grid_size
        block_width = width // grid_size

        
        display_frame = frame.copy()

        
        for i in range(grid_size):
            for j in range(grid_size):
                block = image_array[i*block_height:(i+1)*block_height, j*block_width:(j+1)*block_width]
                variance = detect_blur(block)

                
                x1, y1 = j * block_width, i * block_height
                x2, y2 = x1 + block_width, y1 + block_height

                
                color = (0, 0, 255) if variance < threshold else (0, 255, 0)

                
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(display_frame, f"{variance:.2f}", 
                            ((x1 + x2) // 2, (y1 + y2) // 2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        
        cv2.imshow('Live Camera Blur Detection with Grid', display_frame)

        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break



cap = cv2.VideoCapture(0)


threshold = 150
grid_size = 3


update_frame()

cap.release()
cv2.destroyAllWindows()

