#!/usr/bin/env python

"""Control code for polar bear maternal den monitoring device.

Target is a Raspberry Pi single board computer with a Picamera-style
camera and the AdaFruit PiTFTscreen (2.8" resistive touch model with 4
GPIO-connected buttons) attached.

"""
import logging
import argparse
import time
import tkinter as tk
from threading import Thread

import yaml

import logs
import networking
from buttons import ButtonHandler
from recorder import Recorder
from gui import RecordingPage, NetworkPage

LOGGING_LEVEL = logging.DEBUG
log = logs.setup_logger(LOGGING_LEVEL)
log.info('*** MINIDENCAM STARTING UP ***')
strg = logging.getLevelName(log.getEffectiveLevel())
log.critical('Logging level is {}'.format(strg))

parser = argparse.ArgumentParser()
parser.add_argument('config_file',
                    help='Filename of a YAML Mini Den Cam configuration file.')
args = parser.parse_args()

with open(args.config_file) as f:
    configs = yaml.load(f, Loader=yaml.SafeLoader)

PAUSE_BEFORE_RECORD = configs['PAUSE_BEFORE_RECORD']
RECORD_LENGTH = configs['RECORD_LENGTH']

log.info('Parsed arguments and read configurations')


class DenCamApp(Thread):
    def __init__(self, recorder, state):
        super().__init__()
        self.recorder = recorder
        self.state = state

    def run(self):
        self._setup()
        self.window.after(200, self._update)
        self.window.mainloop()

    def _setup(self):
        # GUI setup
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True)
        self.window.title('DenCam Control')

        self.vid_count_text = tk.StringVar()
        self.vid_count_text.set('|')
        self.storage_text = tk.StringVar()
        self.storage_text.set('|')
        self.device_text = tk.StringVar()
        self.device_text.set('|')
        self.recording_text = tk.StringVar()
        self.recording_text.set('|')
        self.time_text = tk.StringVar()
        self.time_text.set('|')
        self.error_text = tk.StringVar()
        self.error_text.set(' ')
        self.ip_text = tk.StringVar()
        self.ip_text.set('|')

        container = tk.Frame(self.window, bg='black')
        container.pack(side='top', fill='both', expand=True)
        # container.pack(fill=tk.BOTH, expand=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.configure(bg='black')

        self.frames = {}

        for Page in (RecordingPage, NetworkPage):
            page_name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('RecordingPage')

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

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
        self.elapsed_time = time.time() - self.recorder.record_start_time

        if ((self.elapsed_time > PAUSE_BEFORE_RECORD
             and not self.recorder.initial_pause_complete)):
            self.recorder.initial_pause_complete = True
            self.recorder.start_recording()
        elif (self.elapsed_time > RECORD_LENGTH
              and self.recorder.recording):
            self.recorder.stop_recording()
            self.recorder.start_recording()

        if self.state.value <= 1:
            self.show_frame('NetworkPage')
        elif self.state.value == 2:
            self.show_frame('RecordingPage')

        self._update_strings()
        self.window.after(100, self._update)

    def _update_strings(self):
        """Draw the readout for the user to the screen.

        """
        strg = "Vids this run: " + str(self.recorder.vid_count)
        self.vid_count_text.set(strg)

        # prepare storage info text
        free_space = self.recorder.get_free_space()
        storage_string = 'Free: ' + '{0:.2f}'.format(free_space) + ' GB'
        self.storage_text.set(storage_string)

        strg = 'To: {}'.format(self.recorder.video_path)
        self.device_text.set(strg)

        strg = 'Time: ' + self._get_time()
        self.time_text.set(strg)

        # prepare record state info text
        if not self.recorder.initial_pause_complete:
            remaining = PAUSE_BEFORE_RECORD - self.elapsed_time
            rec_text = '{0:.0f}'.format(remaining)
        else:
            state = 'Recording' if self.recorder.recording else 'Idle'
            rec_text = '{}'.format(state)
        self.recording_text.set(rec_text)

        # prep network text
        network_info = networking.get_network_info()
        self.ip_text.set(network_info)


class State():
    def __init__(self, num_states):
        self.value = 0
        self.num_states = num_states

    def goto_next(self):
        self.value += 1
        if self.value >= self.num_states:
            self.value = 0


def main():

    flags = {'stop_buttons_flag': False}
    def cleanup(flags):
        flags['stop_buttons_flag'] = True
        time.sleep(.1)
    
    try:
        recorder = Recorder(configs)

        state = State(3)

        button_handler = ButtonHandler(recorder,
                                       state,
                                       lambda : flags['stop_buttons_flag'])
        button_handler.setDaemon(True)
        button_handler.start()

        app = DenCamApp(recorder, state)
        app.setDaemon(True)
        app.start()

        while(True):
            pass
            time.sleep(.1)
            
    except KeyboardInterrupt:
        log.debug('Keyboard interrupt')
        cleanup(flags)
    except Exception:
        log.exception('Exception in primary try block')
        cleanup(flags)
        
if __name__ == "__main__":
    main()
