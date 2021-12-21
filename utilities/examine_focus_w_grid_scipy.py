import io
import argparse

import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk

import numpy as np
from scipy import ndimage

import picamera
from screeninfo import screeninfo


parser = argparse.ArgumentParser()
parser.add_argument('-r',
                    '--rows',
                    default=4,
                    help='number of rows in grid. 8 can be nice.')
parser.add_argument('-c',
                    '--cols',
                    default=4,
                    help='number of columns in grid. 8 can be nice.')
args = parser.parse_args()


class ImageObject:
    def __init__(self):
        pass

    def set_image(self, image):
        self.image = image

    def get_image(self):
        return self.image


monitor = screeninfo.get_monitors()
display_width = monitor[0].width
display_height = monitor[0].height

window = tk.Tk()

# Set window size
window.geometry('{}x{}'.format(display_width, display_height))

# Make window fullscreen
window.attributes('-fullscreen', True)

window.title('DenCam Focus Utility')

def close_window(event):
    window.destroy()

# Close window when Escape key pressed
window.bind('<Escape>', lambda event: close_window(event))

canvas = tk.Canvas(window, width=display_width, height=display_height)
canvas.pack(side='top', fill='both', expand=True)

stream = io.BytesIO()
camera = picamera.PiCamera()
camera.rotation = 180
image_object = ImageObject()

def variance_of_laplacian(image):
    return ndimage.laplace(image).var()

def update():
    image = canvas.create_image(0, 0, image=image_object.get_image(), anchor='nw')
    canvas.tag_lower(image)
    canvas.update()
    canvas.delete('all')

for _ in camera.capture_continuous(stream, format='rgb'):
    stream.truncate()
    stream.seek(0)
    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    frame = Image.frombuffer('RGB', (display_width, display_height), data)
    color_image = np.array(frame)

    rgb_weights = [0.299, 0.587, 0.114] # RGB[A] to Gray formula from OpenCV
    gray = np.dot(color_image[...,:3], rgb_weights)

    height, width = gray.shape
    num_cols = int(args.cols)
    num_rows = int(args.rows)
    sector_width = int(width/num_cols)
    sector_height = int(height/num_rows)

    img = ImageTk.PhotoImage(image=Image.fromarray(color_image))
    image_object.set_image(img)

    for i in range(num_cols):
        for j in range(num_rows):
            left = int(sector_width * i)
            right = left + sector_width
            top = int(sector_height * j)
            bottom = top + sector_height

            sector = gray[top:bottom, left:right]
            laplacian_value = variance_of_laplacian(sector)
            
            font = tkFont.Font(family='Helvetica', size=15, weight='normal')
            canvas.create_text(left + 80, top + 60, text='{:.0f}'.format(laplacian_value), fill='red', font=font)

            canvas.create_rectangle(left + 2, top + 2, right - 2, bottom - 2, outline='red', width=1)

    update()

# Run the tkinter event loop
window.mainloop()