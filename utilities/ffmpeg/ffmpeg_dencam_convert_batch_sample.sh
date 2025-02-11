#!/bin/sh

## find batch script (beside this file)
ffmpeg_dencam_convert="$(dirname "$0")/ffmpeg_dencam_convert.sh"

## batch convert all .h264 inside a folder
## Use --fpsi and --fpso flags to set framerate (default is 25)
"${ffmpeg_dencam_convert}" \
	--dry-run \
	--fpsi 15 --fpso 15 \
	-m "/path/to/video/folder/2024-02-26/"

## force re-encode one specific file
"${ffmpeg_dencam_convert}" \
	--dry-run \
	--overwrite \
	--fpsi 15 --fpso 15 \
	-m "/path/to/video/folder/2024-02-26/video.h264"
