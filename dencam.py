#!/usr/bin/env python

"""Control code for polar bear maternal den monitoring device.

Target is a Raspberry Pi single board computer with a Picamera-style
camera and the AdaFruit PiTFTscreen (2.8" resistive touch model with 4
GPIO-connected buttons) attached.

"""
import logging
import argparse
import time

import yaml

from dencam import logs
from dencam.buttons import ButtonHandler
from dencam.recorder import Recorder
from dencam.gui import Controller, State

LOGGING_LEVEL = logging.INFO
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

log.info('Parsed arguments and read configurations')


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
        log.debug('Keyboard interrupt')
        cleanup(flags)
    except Exception:
        log.exception('Exception in primary try block')
        cleanup(flags)


if __name__ == "__main__":
    main()
