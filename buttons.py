import time
from threading import Thread

import RPi.GPIO as GPIO

# Button pin number mappings
SCREEN_BUTTON = 27
PREVIEW_BUTTON = 23
RECORD_BUTTON = 22
ZOOM_BUTTON = 17


class ButtonHandler(Thread):
    """Handles the GPIO pins on the pi that are being used.

    Includes the 4 buttons on PiTFT that are connected to Pi GPIO
    pins and the pin that control the brightness of the backlight
    on the screen.

    """

    def __init__(self, recorder):
        super().__init__()

        self.recorder = recorder

        self.latch_screen_button = False
        self.latch_record_button = False
        self.latch_preview_button = False
        self.latch_zoom_button = False

        GPIO.setmode(GPIO.BCM)

        # button pins
        GPIO.setup(SCREEN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(RECORD_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PREVIEW_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ZOOM_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # screen backlight control pin and related
        GPIO.setup(18, GPIO.OUT)
        self.backlight_pwm = GPIO.PWM(18, 1000)
        self.backlight_pwm.start(0)
        self.screen_on = False

        self.off_countdown = 0

    def run(self):

        while True:
            self._handle_buttons()
            time.sleep(.05)

    def _handle_buttons(self):
        """Handles button presses and the associated responses.
        """
        if not GPIO.input(SCREEN_BUTTON):
            if not self.latch_screen_button:
                self.latch_screen_button = True
                if self.screen_on:
                    # turn off screen
                    self.backlight_pwm.ChangeDutyCycle(0)
                else:
                    # turn on screen
                    self.backlight_pwm.ChangeDutyCycle(100)
                self.screen_on = not self.screen_on
        else:
            self.latch_screen_button = False

        if ((not GPIO.input(RECORD_BUTTON)
             and self.recorder.initial_pause_complete)):
            if not self.latch_record_button:
                self.recorder.toggle_recording()
                self.latch_record_button = True
        else:
            self.latch_record_button = False

        if not GPIO.input(ZOOM_BUTTON):
            if not self.latch_zoom_button:
                self.recorder.toggle_zoom()
                self.latch_zoom_button = True
        else:
            self.latch_zoom_button = False

        if not GPIO.input(PREVIEW_BUTTON):
            if not self.latch_preview_button:
                self.recorder.toggle_preview()
                self.latch_preview_button = True
        else:
            self.latch_preview_button = False
