#!/bin/sh

# ================================
## ffmpeg_convert_file.sh
##
## Convert a single video file via ffmpeg
##
## Dependencies:
## *	[ffmpeg = 7.1](https://www.ffmpeg.org/)
##
## Parameters:
## $1 string = /path/to/directory/video.h264
##
## Usage:
## bash ffmpeg_convert_file.sh /path/to/video.h264


# default variable values
video_input_framerate=25
video_output_framerate=25

# load any settings unique to this machine
source=ffmpeg_conf.sh

# ================================
# Review Data

source_filepath=${1}

# Check that file is specified
if [ -z "$source_filepath" ]
then
	echo "Specify the file to be converted:"
	echo ">   ffmpeg_convert_file.sh /path/to/directory/video.h264"
	exit 1
fi

# Check that file exists
if [ ! -f "$source_filepath" ]
then
	echo "This does not appear to be a file:"
	echo ">   $source_filepath"
	exit 1
fi

# extract names
source_dirname=$(dirname -- "$source_filepath")
source_basename=$(basename -- "$source_filepath")
source_shortname="${source_basename%.*}"
#source_extension="${source_basename##*.}"

# form destination filepath
destination_filepath="${source_dirname}/${source_shortname}.mp4"

# DEBUG
# echo "  Data processing review:"
# echo "    filepath    = ${1}"
# echo "    source_dirname   = ${source_dirname}"
# echo "    source_basename  = ${source_basename}"
# echo "    source_shortname = ${source_shortname}"
# echo "    source_extension = ${source_extension}"
# echo "    destination_filepath = ${destination_filepath}"

# if a matching mp4 already exists then skip file
if [ -f "${destination_filepath}" ]
then
	echo "SKIP - $source_shortname - mp4 file already exists";
	exit;
fi;


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
	-r ${video_input_framerate} \
	-i "${source_filepath}" \
	-r ${video_output_framerate} \
	-filter:v fps=fps=${video_output_framerate}:round=near \
	-c:v libx264 \
	-pass 1 \
	-an \
	-copyts \
	-map_metadata 0 \
	-y \
	"${destination_filepath}"

# copy metadata between files from source to destination
touch -r "${source_filepath}" "${destination_filepath}" 

echo "√ DONE";
