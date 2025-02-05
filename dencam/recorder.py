"""Recorder module

This module contains code associated with controlling the recording of
video captured from the picamera.

"""
import logging
import os
import getpass
import time
from datetime import datetime
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)


class BaseRecorder(ABC):
    """Abstract base class for recording handlers

    This includes finding attached media to record to, setting up
    picamera configurations, and abstract methods for methods that
    would do what a child recorder needs to when starting and stopping
    recordings.

    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, configs):
        self.configs = configs

        # state: could be combined into a dict but accesses directly
        # by other code so would have to update in those places
        self.preview_on = False
        self.initial_pause_complete = False
        self.zoom_on = False
        self.recording = False

        self.record_start_time = time.time()  # also used in initial countdown

        # self.camera should be initialized in derived classes
        self.camera = None

        # storage setup
        self.reserved_storage = (configs['PI_RESERVED_STORAGE']
                                 / 1000)  # in gigabytes
        file_size = configs['AVG_VIDEO_FILE_SIZE']/1000  # in gigabytes
        self.vid_file_size = file_size * configs['FILE_SIZE_SAFETY_FACTOR']
        self.last_known_video_path = None
        self.video_path = self._video_path_selector()

    def finish_setup(self):
        """Complete set up in derived class constructurs

        Used in derived classes to do steps required to set up camera
        configuration that must occur after the camera object is
        initialized.

        """
        self.camera.rotation = self.configs['CAMERA_ROTATION']
        self.camera.resolution = self.configs['CAMERA_RESOLUTION']

    @abstractmethod
    def stop_recording(self):
        """Abstract method: used by derived class for recording stop logic

        """
        return

    @abstractmethod
    def start_recording(self):
        """Abstract method: used by derived class for recording start logic

        """
        return

    def toggle_zoom(self):
        """Toggle whether display is digitally zoomed

        This functionality allows user to look at a smaller patch of
        video during deployment to aid in focusing the lens.

        """
        if not self.zoom_on:
            width, _ = self.camera.resolution
            # zoom_factor = 1/float(ZOOM_FACTOR)
            zoom_factor = self.configs['DISPLAY_RESOLUTION'][0]/width
            left = 0.5 - zoom_factor/2.
            top = 0.5 - zoom_factor/2.
            self.camera.zoom = (left, top, zoom_factor, zoom_factor)
        else:
            self.camera.zoom = (0, 0, 1.0, 1.0)
        self.zoom_on = not self.zoom_on

    def toggle_recording(self):
        """Toggle whether system is recording

        """
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def toggle_preview(self):
        """Toggle whether displaying video or not

        """
        if not self.preview_on:
            self.camera.start_preview()
        else:
            self.camera.stop_preview()
        self.preview_on = not self.preview_on

    def start_preview(self):
        """Start display of video on screen

        """
        self.camera.start_preview()
        self.preview_on = True

    def stop_preview(self):
        """Stop display of video on screen

        """
        self.camera.stop_preview()
        self.preview_on = False

    def _video_path_selector(self):
        user = getpass.getuser()
        log.debug("User is '%s'", user)
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
            log.info("Found media in /media: %s", strg)
            for media_device in media_devices:
                media_path = os.path.join(media_dir, media_device)
                free_space = self.get_free_space(media_path)
                if free_space >= self.vid_file_size:
                    log.info("Using external media: %s", media_device)
                    log.debug("Free space on device: %.2f", free_space)
                    break
                log.info("Device %s is full or unwritable.", media_device)
                log.info("Advancing to next device.")
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
        if free_space >= (self.vid_file_size + self.reserved_storage):
            log.info('Using home directory.')
            log.debug("Free space in home directory: %.2f GB", free_space)
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
        """Update timestamp string on camera capture

        """
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
            self.camera.start_recording(filename,
                                        quality=self.configs['VIDEO_QUALITY'])
            self.record_start_time = time.time()

    def stop_recording(self):
        """Stops currently ongoing recording

        """
        log.info('Ending current recording')
        self.recording = False
        self.camera.stop_recording()
