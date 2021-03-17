"""Program that tests preview (and thus view) of a picamera.


"""
import argparse
import time

import yaml
from picamera import PiCamera

parser = argparse.ArgumentParser()
parser.add_argument('config_file')
parser.add_argument('num_seconds')
args = parser.parse_args()

num_seconds = int(args.num_seconds)

with open(args.config_file) as f:
    configs = yaml.load(f, Loader=yaml.SafeLoader)

camera = PiCamera()

camera.resolution = configs['CAMERA_RESOLUTION']
camera.rotation = configs['CAMERA_ROTATION']

print(f'Running preview for {num_seconds} seconds.')
camera.start_preview()
time.sleep(num_seconds)
camera.stop_preview()
