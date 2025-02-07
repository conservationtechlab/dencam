#!/bin/sh

# ================================
## ffmpeg_convert_file.sh
## 
## Convert a single video file via ffmpeg
##
## Dependencies:
## *	[ffmpeg](https://www.ffmpeg.org/)
##
## Parameters:
## $1 string = /path/to/directory/video.h264
##


# ================================
# Review Data

# Check that file is specified
if [ -z "$1" ]
then
	echo "Specify the file to be converted:"
	echo ">   ffmpeg_convert_file.sh /path/to/directory/video.h264"
	exit 1
fi

# Check that file exists
if [ ! -f "$1" ]
then
	echo "This does not appear to be a file:"
	echo ">   $1"
	exit 1
fi

# interpret path
source_filepath=${1}
source_dirname=$(dirname -- "$source_filepath")
source_basename=$(basename -- "$source_filepath")
source_shortname="${source_basename%.*}"
#source_extension="${source_basename##*.}"

# form target destination
target_filepath="${source_dirname}/${source_shortname}.mp4"

# DEBUG
# echo "  Data processing review:"
# echo "    filepath    = ${1}"
# echo "    source_dirname   = ${source_dirname}"
# echo "    source_basename  = ${source_basename}"
# echo "    source_shortname = ${source_shortname}"
# echo "    source_extension = ${source_extension}"
# echo "    target_filepath = ${target_filepath}"


# ================================
# CONVERT
#
# specify framerate of input with "-r" before "-i"
# specify framerate of output with "-r" after "-i"
# -an = no audio
# -f  = force format
# -y  = overwrite output
# -copyts = Copy timestamps from input to output
# -map_metadata

# convert now
ffmpeg \
	-r 15 \
	-i "${source_filepath}" \
	-r 15 \
	-filter:v fps=fps=15:round=near \
	-c:v libx264 \
	-pass 1 \
	-an \
	-copyts \
	-map_metadata 0 \
	-y \
	"${target_filepath}"

# copy metadata from original file
touch -r "${source_filepath}" "${target_filepath}" 