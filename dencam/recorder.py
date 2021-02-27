import logging
import os
import getpass
import time
from abc import ABC, abstractmethod

import picamera
from datetime import datetime
from picamera import PiCamera


log = logging.getLogger(__name__)


class BaseRecorder(ABC):

    def __init__(self, configs):
        self.preview_on = False

        self.record_start_time = time.time()  # also used in initial countdown
        self.video_path = self._video_path_selector()

        # PiTFT characteristics
        self.DISPLAY_RESOLUTION = configs['DISPLAY_RESOLUTION']

        # Camera settings
        CAMERA_RESOLUTION = configs['CAMERA_RESOLUTION']
        CAMERA_ROTATION = configs['CAMERA_ROTATION']
        FRAME_RATE = configs['FRAME_RATE']

        self.VIDEO_QUALITY = configs['VIDEO_QUALITY']

        log.info('Read recording configurations')

        self.initial_pause_complete = False

        # camera setup
        self.camera = PiCamera(framerate=FRAME_RATE)
        self.camera.rotation = CAMERA_ROTATION
        self.camera.resolution = CAMERA_RESOLUTION
        self.camera.annotate_text_size = 80
        self.camera.annotate_foreground = picamera.color.Color('white')
        self.camera.annotate_background = picamera.color.Color('black')

        self.zoom_on = False
        # recording setup
        self.recording = False

    @abstractmethod
    def stop_recording(self):
        return

    @abstractmethod
    def start_recording(self):
        return

    def toggle_zoom(self):
        if not self.zoom_on:
            width, height = self.camera.resolution
            # zoom_factor = 1/float(ZOOM_FACTOR)
            zoom_factor = self.DISPLAY_RESOLUTION[0]/width
            left = 0.5 - zoom_factor/2.
            top = 0.5 - zoom_factor/2.
            self.camera.zoom = (left, top, zoom_factor, zoom_factor)
        else:
            self.camera.zoom = (0, 0, 1.0, 1.0)
        self.zoom_on = not self.zoom_on

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def toggle_preview(self):
        if not self.preview_on:
            self.camera.start_preview()
        else:
            self.camera.stop_preview()
        self.preview_on = not self.preview_on

    def start_preview(self):
        self.camera.start_preview()
        self.preview_on = True

    def stop_preview(self):
        self.camera.stop_preview()
        self.preview_on = False

    def _video_path_selector(self):
        user = getpass.getuser()
        log.debug("User is '{}'".format(user))
        media_dir = os.path.join('/media', user)

        # this try block protects against the user not even having a folder in
        # /media which can happen if no media has ever been attached under
        # that user
        try:
            media_devices = os.listdir(media_dir)
        except FileNotFoundError:
            media_devices = []

        default_path = os.path.join('/home', user)
        if media_devices:
            media_devices.sort()
            strg = ', '.join(media_devices)
            log.info('Found media in /media: {}'.format(strg))
            for media_device in media_devices:
                media_path = os.path.join(media_dir, media_device)
                free_space = self.get_free_space(media_path)
                if free_space >= 0.5:  # half a gig
                    log.info('Using external media: '
                             + '{}'.format(media_device))
                    log.debug('Free space on device: '
                              + '{:.2f} GB'.format(free_space))
                    break
                else:
                    log.info('Device {} is '.format(media_device)
                             + 'full or unwritable.'
                             + ' Advancing to next device.')
            else:
                log.warning('No external device worked. '
                            + 'Using home directory.')
                media_path = default_path
        else:
            log.warning('Did not find external media. '
                        + 'Using home directory.')
            media_path = default_path

        return media_path

    def get_free_space(self, card_path=None):
        """Get the remaining space on SD card in gigabytes

        """
        if card_path is None:
            card_path = self.video_path

        try:
            statvfs = os.statvfs(card_path)
            bytes_available = statvfs.f_frsize * statvfs.f_bavail
            gigabytes_available = bytes_available/1000000000
            return gigabytes_available
        except FileNotFoundError:
            return 0

    def update_timestamp(self):
        date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.camera.annotate_text = date_string


class Recorder(BaseRecorder):
    def __init__(self, configs):
        super().__init__(configs)

        self.vid_count = 0

    def start_recording(self):
        log.info('Starting new recording.')
        self.recording = True
        self.vid_count += 1

        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")

        log.info('Looking for free space on external media.')
        self.video_path = self._video_path_selector()

        # if not os.path.exists(self.video_path):
        #     strg = ("ERROR: Video path broken. " +
        #             "Recording to {}".format(DEFAULT_PATH))
        #     self.error_label['text'] = strg
        #     self.video_path = DEFAULT_PATH
        #     log.error("Video path doesn't exist. "
        #           + "Writing files to /home/pi")

        todays_dir = os.path.join(self.video_path, date_string)

        if not os.path.exists(todays_dir):
            os.makedirs(todays_dir)
        date_time_string = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        filename = os.path.join(todays_dir, date_time_string + '.h264')
        self.camera.start_recording(filename, quality=self.VIDEO_QUALITY)
        self.record_start_time = time.time()

    def stop_recording(self):
        log.info('Ending current recording')
        self.recording = False
        self.camera.stop_recording()
