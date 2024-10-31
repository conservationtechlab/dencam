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

# pylint: disable=import-self
from dencam import __version__
from dencam.logs import setup_logger
from dencam.buttons import ButtonHandler
from dencam.recorder_picamera2 import Picamera2Recorder
from dencam.gui import ErrorScreen, Controller, State
from dencam.networking import AirplaneMode

log = setup_logger(logging.INFO)


def main():
    """Run main DenCam program

    """
    log.info('*** MINIDENCAM v%s STARTING UP ***', __version__)
    # clearly below line only reports for debug and info levels
    log.info("Logging level is %s",
             logging.getLevelName(log.getEffectiveLevel()))

    parser = argparse.ArgumentParser()
    parser.add_argument('config_file',
                        help='DenCam configuration file (YAML)')
    args = parser.parse_args()
    with open(args.config_file, 'r', encoding='utf8') as config_file:
        configs = yaml.load(config_file, Loader=yaml.SafeLoader)
    log.info('Ingested configuration settings')

    flags = {'stop_buttons_flag': False}
    state_list = ['OffPage',
                  'NetworkPage',
                  'RecordingPage',
                  "SolarPage",
                  "BlankPage"]

    try:
        checking_camera = True
        error_screen = None
        while checking_camera:
            try:
                recorder = Picamera2Recorder(configs)
                checking_camera = False
            except RunimeError as cam_error:
                log.warning(cam_error)
                if error_screen is None:
                    error_screen = ErrorScreen()
                time.sleep(.5)
        if error_screen is not None:
            error_screen.hide()

        number_of_states = len(state_list)
        state = State(number_of_states)
        airplane_mode = AirplaneMode(configs)
        button_handler = ButtonHandler(recorder,
                                       state,
                                       state_list,
                                       airplane_mode,
                                       lambda: flags['stop_buttons_flag'])
        button_handler.daemon = True
        button_handler.start()

        controller = Controller(configs, recorder, state_list,
                                state, airplane_mode)
        controller.daemon = True
        controller.start()

        while True:
            time.sleep(.1)

    except KeyboardInterrupt:
        log.info('Keyboard interrupt received.')
        flags['stop_buttons_flag'] = True
        time.sleep(.1)


if __name__ == "__main__":
    main()
