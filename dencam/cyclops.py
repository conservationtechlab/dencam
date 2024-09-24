"""Recorder module

This module contains code associated with controlling the recording of
video captured from the picamera.

"""

import logging
import os
import getpass
import time
from abc import ABC, abstractmethod


from datetime import datetime
from dencam.ptz_control_and_display import PTZControlSystem


log = logging.getLogger(__name__)


class BaseRecorder(ABC):
    """Abstract base class for recording handlers

    This includes finding attached media to record to, setting up
    picamera configurations, and abstract methods for methods that
    would do what a child recorder needs to when starting and stopping
    recordings.

    """

    def __init__(self, configs):
        self.preview_on = False

        self.record_start_time = time.time()  # also used in initial countdown

        # PiTFT characteristics
        self.DISPLAY_RESOLUTION = configs['DISPLAY_RESOLUTION']

        # Camera settings
        CAMERA_RESOLUTION = configs['CAMERA_RESOLUTION']
        CAMERA_ROTATION = configs['CAMERA_ROTATION']
        FRAME_RATE = configs['FRAME_RATE']

        self.VIDEO_QUALITY = configs['VIDEO_QUALITY']

        log.info('Read recording configurations')

        self.initial_pause_complete = False

        # recording setup
        self.SAFETY_FACTOR = configs['FILE_SIZE_SAFETY_FACTOR']
        self.RESERVED_STORAGE = (configs['PI_RESERVED_STORAGE']
                                 / 1000)  # in gigabytes
        self.FILE_SIZE = configs['AVG_VIDEO_FILE_SIZE']/1000  # in gigabytes
        self.VID_FILE_SIZE = self.FILE_SIZE * self.SAFETY_FACTOR
        self.recording = False
        self.last_known_video_path = None
        self.video_path = self._video_path_selector()

        self.camera = PTZControlSystem(configs)

    @abstractmethod
    def stop_recording(self):
        return

    @abstractmethod
    def start_recording(self):
        return

    def toggle_ptz_control(self):
        return

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def toggle_preview(self):
        if not self.preview_on:
            self.camera.start_system()
        else:
            self.camera.stop_system()
        self.preview_on = not self.preview_on

    def start_preview(self):
        self.camera.start_system()
        print("start_preview in cyclops.py is starting system function")
        self.preview_on = True

    def stop_preview(self):
        self.camera.stop_system()
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
                if free_space >= self.VID_FILE_SIZE:
                    log.info('Using external media: '
                             + '{}'.format(media_device))
                    log.debug('Free space on device: '
                              + '{:.2f} GB'.format(free_space))
                    break
                else:
                    log.info('Device {} is '.format(media_device)
                             + 'full or unwritable. '
                             + 'Advancing to next device.')
            else:
                log.warning('No external device worked. '
                            + 'Checking home directory for free space.')
                media_path = self._check_home_storage_capacity(default_path)
        else:
            log.warning('Unable to find external media. '
                        + 'Checking home directory for free space.')
            media_path = self._check_home_storage_capacity(default_path)

        return media_path

    def _check_home_storage_capacity(self, media_path):
        free_space = self.get_free_space(media_path)
        if free_space >= (self.VID_FILE_SIZE + self.RESERVED_STORAGE):
            log.info('Using home directory.')
            log.debug('Free space in home directory: '
                      + '{:.2f} GB'.format(free_space))
        else:
            log.info('Home directory is full or unwritable.')
            self.last_known_video_path = media_path
            media_path = None

        return media_path

    def get_free_space(self, media_path=None):
        """Get the remaining space on SD card in gigabytes

        """
        if media_path is None and self.video_path is not None:
            media_path = self.video_path
        elif media_path is None and self.video_path is None:
            self.video_path = self.last_known_video_path
            media_path = self.video_path

        try:
            statvfs = os.statvfs(media_path)
            bytes_available = statvfs.f_frsize * statvfs.f_bavail
            gigabytes_available = bytes_available/1000000000
            return gigabytes_available
        except FileNotFoundError:
            return 0

    def update_timestamp(self):
        date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.camera.annotate_text = date_string


class Recorder(BaseRecorder):
    """DenCam's Recorder class

    The concrete recorder class used by DenCam.

    """

    def __init__(self, configs):
        super().__init__(configs)

        self.vid_count = 0

    def start_recording(self):
        """Prepares for and starts a new recording

        """
        log.info('Looking for free space on external media.')
        self.video_path = self._video_path_selector()

        if self.video_path:
            log.info('Starting new recording.')
            self.recording = True
            self.vid_count += 1

            now = datetime.now()
            date_string = now.strftime("%Y-%m-%d")

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
        """Stops currently ongoing recording

        """
        log.info('Ending current recording')
        self.recording = False
        #have to add this function in to make the ptz cam stop recording
