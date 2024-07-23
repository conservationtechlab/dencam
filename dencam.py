#!/usr/bin/env python

"""Control code for polar bear maternal den observation device.

The target hardware is a Raspberry Pi 4 Model B single board computer
with a Picamera-style camera and the AdaFruit PiTFTscreen (2.8"
resistive touch model with 4 GPIO-connected buttons)
attached. Typically several storage devices are connected via the USB
ports on the Pi (e.g. uSD card readers). This hardware is typically
integrated into a larger assembly that includes a weatherproof
enclosure, batteries, charger controller, and an external solar
panels.

"""
import logging
import argparse
import time

import yaml
from error_handling import show_error_screen, hide_error_screen
from dencam import logs
from dencam.buttons import ButtonHandler
from dencam.recorder import Recorder
from dencam.gui import Controller, State
from dencam.networking import AirplaneMode
from picamera.exc import PiCameraMMALError

parser = argparse.ArgumentParser()
parser.add_argument('config_file',
                    help='Filename of a YAML Mini DenCam configuration file.')
args = parser.parse_args()

LOGGING_LEVEL = logging.INFO
log = logs.setup_logger(LOGGING_LEVEL)
log.info('*** MINIDENCAM STARTING UP ***')
strg = logging.getLevelName(log.getEffectiveLevel())
# clearly below line only reports for debug and info levels
log.info('Logging level is {}'.format(strg))

with open(args.config_file) as f:
    configs = yaml.load(f, Loader=yaml.SafeLoader)
log.info('Read in configuration settings')


def main():
    error_screen_shown = 0

    flags = {'stop_buttons_flag': False}
    STATE_LIST = ['OffPage', 'NetworkPage', 'RecordingPage', "SolarPage", "BlankPage"]

    def cleanup(flags):
        flags['stop_buttons_flag'] = True
        time.sleep(.1)

    try:
        while True:
            try:  
                recorder = Recorder(configs)
                if error_screen_shown == 1:
                    hide_error_screen(error_screen)
                    error_screen_shown = 0
            except PiCameraMMALError as e:
                print("Camera failed to initialize, check cable connection")
                if error_screen_shown == 0:
                    error_screen = show_error_screen()
                    error_screen_shown = 1
                time.sleep(5)
                continue
            number_of_states = len(STATE_LIST)
            state = State(number_of_states)
            airplane_mode = AirplaneMode(configs)
            button_handler = ButtonHandler(recorder,
                                           state,
                                           STATE_LIST,
                                           airplane_mode,
                                           lambda: flags['stop_buttons_flag'])
            button_handler.setDaemon(True)
            button_handler.start()

            controller = Controller(configs, recorder, STATE_LIST, state, airplane_mode)
            controller.setDaemon(True)
            controller.start()

            while(True):
                pass
                time.sleep(.1)

    except KeyboardInterrupt:
        log.debug('Keyboard interrupt received.')
        cleanup(flags)
    except Exception:
        log.exception('An Exception in primary try block')
        cleanup(flags)


if __name__ == "__main__":
    main()
