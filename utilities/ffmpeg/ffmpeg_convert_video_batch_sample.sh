#!/bin/sh

## find batch script (beside this file)
ffmpeg_convert_video="$(dirname "$0")/ffmpeg_convert_video.sh"

## batch convert all .h264 inside a folder
## framerate default is 25, use --fpsi and --fpso flags to set other
"${ffmpeg_convert_video}" \
	--dry-run \
	--fpsi 15 --fpso 15 \
	-m "/path/to/video/folder/2024-02-26/"

## force re-encode one specific file
"${ffmpeg_convert_video}" \
	--dry-run \
	--overwrite \
	--fpsi 15 --fpso 15 \
	-m "/path/to/video/folder/2024-02-26/video.h264"
