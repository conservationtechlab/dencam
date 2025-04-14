'''
Use sun altitude to trigger camera relay and turn
off camera when dark. Camera will stay on during
daylight and astonomical twilight.

To be used as a systemd service.
'''

import time
from datetime import datetime
from RPi import GPIO
import ephem

LAT, LON = 72.2232, 15.6267 # svalbard
ON, OFF = 0, 1
RELAY_PIN = 19
SUN_ANGLE = -18 # astonomical twilight

def main():

    # GPIO Setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)

    # ephem setup
    observer = ephem.Observer()
    observer.lat = str(LAT)
    observer.lon = str(LON)
    sun = ephem.Sun()

    while True:
        observer.date = datetime.now()
        sun.compute(observer)

        if sun.alt > SUN_ANGLE:
            GPIO.output(RELAY_PIN, ON)
        else:
            GPIO.output(RELAY_PIN, OFF)

        time.sleep(60) # check every min

if __name__ == '__main__':
    main()
