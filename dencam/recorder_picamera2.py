import logging
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from datetime import datetime
import os
import time
from dencam.recorder import Recorder

log = logging.getLogger(__name__)


class Picam2:
    def __init__(self, configs):
        self.configs = configs
        self.encoder = H264Encoder()
        
        self.camera = Picamera2()
        self.camera.preview_configuration.enable_lores()
        self.camera.preview_configuration.lores.size = (320, 240)
        self.camera.configure("preview")
        self.camera.start_preview(Preview.NULL)
        self.camera.start()

    def start_preview(self):
        self.camera.stop_preview()
        self.camera.start_preview(Preview.QT, x=-2, y=-28, width=320, height=240)
        log.info('Started Preview')

    def stop_preview(self):
        self.camera.stop_preview()
        self.camera.start_preview(Preview.NULL)
        log.info('Stopped Preview')


    def start_recording(self, filename, quality=None):
        self.camera.start_recording(self.encoder, filename)

    def stop_recording(self):
        self.camera.stop_recording()

class Picamera2Recorder(Recorder):
    """Recorder that uses picamera2

    """
    def __init__(self, configs):
        super().__init__(configs)
        log.info('Set up camera per configurations')
        self.camera = Picam2(configs)
        self.configs = configs

    '''def start_recording(self):
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
            encoder = H264Encoder()
            self.camera.start_recording(encoder, filename)
            self.record_start_time = time.time()'''
