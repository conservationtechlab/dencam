#!/bin/sh

## ================
## SETUP
##
## Install [ffmpeg](https://www.ffmpeg.org/)
##
## Keep these ffmpeg shell script files beside one another.
## Ensure scripts are executable:
## — ffmpeg_convert_directory_batch.sh
## — ffmpeg_convert_file.sh
##
## Update variables in ffmpeg_conf.sh (if needed)
## — video framerates
##

# find batch script (beside this file)
ffmpeg_convert_directory_batch="$(dirname "$0")/ffmpeg_convert_directory_batch.sh"


## ================
## PREP COMMANDS

## Step 1 - Start with:
## >   "${ffmpeg_convert_directory_batch}" --help

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
## >   ffmpeg_convert_directory_batch.sh --dry-run -d /path/to/video/folder/YYYY-MM-DD/
##
## For a prepared batch shell file use:
## >   "${ffmpeg_convert_directory_batch}" --dry-run -d "/path/to/video/folder/YYYY-MM-DD/"
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

# "${ffmpeg_convert_directory_batch}" -d "/path/to/video/folder/2024-02-26/"
# "${ffmpeg_convert_directory_batch}" -d "/path/to/video/folder/2024-02-27/"
# "${ffmpeg_convert_directory_batch}" -d "/path/to/video/folder/2024-02-28/"

## default framerate is currently 25 fps
## to set a custom rate use --fpsi and --fpso flags
# "${ffmpeg_convert_directory_batch}" --fpsi 15 --fpso 15 -d "/path/to/video/folder/2024-02-28/"
