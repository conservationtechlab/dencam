"""Tool to examine focus in view of DenCam.

A tool for numerically examining how well the DenCam's camera is
focused. A number displayed in each grid element of a grid (grid
defaults to 4x4) can be used to judge focus for the grid element and
in aggregate for the scene.  The number's value is a function of both
the degree of focus *and* complexity of what is in view within that
grid element so it has to be treated as a relative focus tool i.e. as
focus is adjusted on the lens, the number will peak at best focus
(provided the view itself is unchanged) but that peak could be a very
different number for one scene (or grid element) versus another.

"""

import argparse

import cv2
import numpy as np
from screeninfo import get_monitors

import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk

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


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


# Get display information
monitor = get_monitors()
display_width = monitor[0].width
display_height = monitor[0].height

# Setup grid calculation
num_cols = int(args.cols)
num_rows = int(args.rows)
sector_width = int(display_width / num_cols)
sector_height = int(display_height / num_rows)

# Setup tkinter
window = tk.Tk()
window.geometry(f'{display_width}x{display_height}')  # Set window size
window.attributes('-fullscreen', True)  # Make window fullscreen
font = tkFont.Font(family='Helvetica', size=15, weight='normal')

# Setup frame
container = tk.Frame(window)
container.pack(expand=True, fill='both')

# Setup canvas
canvas = tk.Canvas(container, width=display_width, height=display_height, highlightthickness=0)
canvas.pack(expand=True, fill='both')
image_on_canvas = canvas.create_image(0, 0, anchor='nw')
canvas.tag_lower(image_on_canvas)
text_array = [[None for x in range(num_rows)] for y in range(num_cols)]
rectangle_array = [[None for x in range(num_rows)] for y in range(num_cols)]

# Setup moving average for laplace
mv_avg = None
mv_avg_count = 0
mv_avg_freq = 5  # Number of frames to perform moving average on
laplace_array = np.full((num_rows, num_cols, mv_avg_freq), None)

# Open a camera for video capturing
cap = cv2.VideoCapture(0)

def show_frame():
    global tkinter_image, mv_avg_count

    ret, frame = cap.read()
    frame = cv2.resize(frame, (display_width, display_height))
    frame = cv2.flip(frame, 0)
    color_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    gray_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY)
    
    image_data = Image.fromarray(color_image)
    tkinter_image = ImageTk.PhotoImage(image=image_data)
    canvas.itemconfig(image_on_canvas, image=tkinter_image)

    for i in range(num_cols):
        for j in range(num_rows):
            left = int(sector_width * i)
            right = left + sector_width
            top = int(sector_height * j)
            bottom = top + sector_height

            sector = gray_image[top:bottom, left:right]
            laplace = variance_of_laplacian(sector)

            mv_avg_count %= mv_avg_freq
            depth = laplace_array[i][j]
            depth[mv_avg_count] = laplace
            if None in np.array(depth):
                mv_avg = round(depth[mv_avg_count] / 10) * 10
            else:
                mv_avg = np.mean(depth)
                mv_avg = round(mv_avg / 10) * 10

            if rectangle_array[i][j] is None:
                canvas.create_rectangle(left + 2,
                                        top + 2,
                                        right - 2,
                                        bottom - 2,
                                        outline='red',
                                        width=1)

            if text_array[i][j] is None:
                text_array[i][j] = canvas.create_text(left + 80,
                                                      top + 60,
                                                      text=f'{mv_avg}',
                                                      fill='red',
                                                      font=font)
            else:
                canvas.itemconfig(text_array[i][j], text=f'{mv_avg}')

    mv_avg_count += 1

    window.after(1, show_frame)

show_frame()

# Run the tkinter event loop
window.mainloop()
