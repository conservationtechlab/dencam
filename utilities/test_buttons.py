"""Tests functioning of DenCam buttons

Test script for testing the functioning of the interface buttons on
the DenCam. These are the buttons integrated on the Adafruit PiTFT
screen PCB which itself is directly attached to the GPIO-header on the
Raspberry Pi.

"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    buttonState_0 = GPIO.input(17)
    buttonState_1 = GPIO.input(22)
    buttonState_2 = GPIO.input(23)
    buttonState_3 = GPIO.input(27)

    print("Button Output:" +
          str(buttonState_0) +
          str(buttonState_1) +
          str(buttonState_2) +
          str(buttonState_3))

    time.sleep(.3)
