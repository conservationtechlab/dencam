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

from dencam import logs
from dencam.buttons import ButtonHandler
from dencam.recorder import Recorder
from dencam.gui import Controller, State

parser = argparse.ArgumentParser()
parser.add_argument('config_file',
                    help='Filename of a YAML Mini DenCam configuration file.')
args = parser.parse_args()

LOGGING_LEVEL = logging.INFO
log = logs.setup_logger(LOGGING_LEVEL, 'dencam.log')
log.info('*** MINIDENCAM STARTING UP ***')
strg = logging.getLevelName(log.getEffectiveLevel())
# clearly below line only reports for debug and info levels
log.info('Logging level is {}'.format(strg))  

with open(args.config_file) as f:
    configs = yaml.load(f, Loader=yaml.SafeLoader)
log.info('Read in configuration settings')


def main():

    flags = {'stop_buttons_flag': False}

    def cleanup(flags):
        flags['stop_buttons_flag'] = True
        time.sleep(.1)

    try:
        recorder = Recorder(configs)
        state = State(4)
        button_handler = ButtonHandler(recorder,
                                       state,
                                       lambda: flags['stop_buttons_flag'])
        button_handler.setDaemon(True)
        button_handler.start()

        controller = Controller(configs, recorder, state)
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
