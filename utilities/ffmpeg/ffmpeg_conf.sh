#!/bin/sh

## ================
## ffmpeg_conf.sh
## 
## Set unique values for your machine
##

video_input_framerate=15
video_output_framerate=15


# ================================
# Todo List

# ffmpeg_convert_file.sh will currently run for any file...
# test whether file is actually a video
# or at least has the expected ".h264" extension?

# handle directory paths with spaces/unusual characters

# handle directory symbolic links

# add flag to force overwrite
# for cases where previous conversion failed
# but now a .mp4 file already exists
