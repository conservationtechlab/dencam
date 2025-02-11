#!/bin/sh

## ================
## SETUP
##
## Install [ffmpeg](https://www.ffmpeg.org/)
## 
## This script was developed using ffmpeg version 7.1
## and has not been tested on earlier versions.
##

# find batch script (beside this file)
ffmpeg_dencam_convert="$(dirname "$0")/ffmpeg_dencam_convert.sh"

## ================
## PREP COMMANDS

## Step 1 - Start with:
## >   "${ffmpeg_dencam_convert}" --help

## Step 2 - Then test your folder structure:
## Call the batch command with the path to the directory
## which contains all of the media files
##
## So, for:
## >   /path/to/video/folder/YYYY-MM-DD/video001.h264
## >   /path/to/video/folder/YYYY-MM-DD/video002.h264
## >   /path/to/video/folder/YYYY-MM-DD/video003.h264
##
## For a single batch from the command line:
## >   ffmpeg_dencam_convert.sh --dry-run -d /path/to/video/folder/YYYY-MM-DD/
##
## For a prepared batch shell file use:
## >   "${ffmpeg_dencam_convert}" --dry-run -d "/path/to/video/folder/YYYY-MM-DD/"
##


## Use the related "ffprobe" if you need to analyze video files
# ffprobe \
# 	-v error \
# 	-show_format \
# 	-show_streams \
# 	/path/to/media/folder/video.h264 \
# 	> /path/to/media/folder/video-ffprobe.txt


## ================
## RUN

## Step 3 - run a batch command per folder:

# "${ffmpeg_dencam_convert}" -d "/path/to/video/folder/2024-02-26/"
# "${ffmpeg_dencam_convert}" -d "/path/to/video/folder/2024-02-27/"
# "${ffmpeg_dencam_convert}" -d "/path/to/video/folder/2024-02-28/"

## default framerate is currently 25 fps
## to set a custom rate use --fpsi and --fpso flags
# "${ffmpeg_dencam_convert}" --fpsi 15 --fpso 15 -d "/path/to/video/folder/2024-02-28/"
