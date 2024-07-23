import tkinter as tk
from time import sleep

def show_error_screen():
    screen = tk.Tk()
    screen.attributes('-fullscreen', True)
    screen.configure(background='black')

    label = tk.Label(screen, text="Camera connection error\nplease check connection to camera",
                     fg="white", bg="black", font=("Helvetica", 28))
    label.pack(expand=True)

    screen.update()
    return screen

def hide_error_screen(screen):
    screen.destroy()
