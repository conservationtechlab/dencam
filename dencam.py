"""Control code for polar bear maternal den monitoring device.

Target is a Raspberry Pi single board computer with a Picamera-style
camera and the AdaFruit PiTFTscreen (2.8" resistive touch model with 4
GPIO-connected buttons) attached.

"""
import argparse
import os
import time
import tkinter as tk
import tkinter.font as tkFont
from threading import Thread

import yaml

from buttons import ButtonHandler
from recorder import Recorder

parser = argparse.ArgumentParser()
parser.add_argument('config_file',
                    help='Filename of a YAML Mini Den Cam configuration file.')
args = parser.parse_args()

with open(args.config_file) as f:
    configs = yaml.load(f, Loader=yaml.SafeLoader)

PAUSE_BEFORE_RECORD = configs['PAUSE_BEFORE_RECORD']
RECORD_LENGTH = configs['RECORD_LENGTH']


class DenCamApp(Thread):
    def __init__(self, recorder):
        super().__init__()
        self.recorder = recorder

    def run(self):
        self.record_start_time = time.time()  # also used in initial countdown
        # tkinter setup
        self.window = tk.Tk()
        self._layout_window()
        self.window.attributes('-fullscreen', True)

        self.window.after(200, self._update)
        self.window.mainloop()

    def _layout_window(self):
        """Layout the information elements to be rendered to the screen.

        """
        self.window.title('DenCam Control')
        frame = tk.Frame(self.window, bg='black')
        frame.pack(fill=tk.BOTH, expand=1)
        frame.configure(bg='black')

        scrn_height = self.window.winfo_screenheight()
        small_font = tkFont.Font(family='Courier New',
                                 size=-int(scrn_height/9))

        error_font = tkFont.Font(family='Courier New',
                                 size=-int(scrn_height/12))

        big_font = tkFont.Font(family='Courier New',
                               size=-int(scrn_height/5))

        self.vid_count_label = tk.Label(frame,
                                        text='|',
                                        font=small_font,
                                        fg='blue',
                                        bg='black')
        self.vid_count_label.pack(fill=tk.X)

        self.storage_label = tk.Label(frame,
                                      text='|',
                                      font=small_font,
                                      fg='blue',
                                      bg='black')
        self.storage_label.pack(fill=tk.X)

        self.time_label = tk.Label(frame,
                                   text='|',
                                   font=small_font,
                                   fg='blue',
                                   bg='black')
        self.time_label.pack(fill=tk.X)

        self.recording_label = tk.Label(frame,
                                        text='|',
                                        font=big_font,
                                        fg='blue',
                                        bg='black')
        self.recording_label.pack(fill=tk.X)

        self.error_label = tk.Label(frame,
                                    text=' ',
                                    font=error_font,
                                    fg='red',
                                    bg='black')
        self.error_label.pack(fill=tk.X)

    def _get_free_space(self):
        """Get the remaining space on SD card in gigabytes

        """
        try:
            statvfs = os.statvfs(self.recorder.video_path)
            bytes_available = statvfs.f_frsize * statvfs.f_bavail
            gigabytes_available = bytes_available/1000000000
            return gigabytes_available
        except FileNotFoundError:
            return 0

    def _get_time(self):
        """Retrieve current time and format it for screen display

        """
        local_time = time.localtime()

        hours = local_time.tm_hour
        mins = local_time.tm_min
        secs = local_time.tm_sec

        shours = str(hours)
        smins = str(mins)
        ssecs = str(secs)

        if hours < 10:
            shours = '0' + shours
        if mins < 10:
            smins = '0' + smins
        if secs < 10:
            ssecs = '0' + ssecs

        return shours + ':' + smins + ':' + ssecs

    def _update(self):
        """Core loop method run at 10 Hz

        """

        self.elapsed_time = time.time() - self.record_start_time

        if ((self.elapsed_time > PAUSE_BEFORE_RECORD
             and not self.recorder.initial_pause_complete)):
            self.recorder.initial_pause_complete = True
            self.recorder.start_recording()
        elif (self.elapsed_time > RECORD_LENGTH
              and self.recorder.recording):
            self.recorder.stop_recording()
            self.recorder.start_recording()

        self._draw_readout()
        self.window.after(100, self._update)

    def _draw_readout(self):
        """Draw the readout for the user to the screen.

        """

        self.vid_count_label['text'] = ("Vids this run: "
                                        + str(self.recorder.vid_count))

        free_space = self._get_free_space()
        storage_string = 'Free: ' + '{0:.2f}'.format(free_space) + ' GB'
        self.storage_label['text'] = storage_string

        self.time_label['text'] = 'Time: ' + self._get_time()

        if not self.recorder.initial_pause_complete:
            remaining = PAUSE_BEFORE_RECORD - self.elapsed_time
            rec_text = '{0:.0f}'.format(remaining)
        else:
            state = 'Recording' if self.recorder.recording else 'Idle'
            rec_text = '{}'.format(state)
        self.recording_label['text'] = rec_text


def main():
    recorder = Recorder(configs)

    app = DenCamApp(recorder)
    app.start()

    button_handler = ButtonHandler(recorder)
    button_handler.start()


if __name__ == "__main__":
    main()
