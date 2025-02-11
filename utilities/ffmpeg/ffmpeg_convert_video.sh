#!/bin/sh

## ================
## ffmpeg_convert_video.sh
## version 0.2
## 
## Convert Pi camera recordings from .h264 to .mp4
## either from individual files (/path/to/video.h264)
## or batch convert entire folders (/path/to/directory/)
##
## Start with:
## >    ffmpeg_convert_video.sh --help
##
## This script was developed using ffmpeg version 7.1
## and has not been tested on earlier versions.
##
## Dependencies:
## *	[ffmpeg](https://www.ffmpeg.org/)
##


## ================
## TODO LIST
## 
## handle ffmpeg success/error codes separately
## ex. we have received "Decoding error: Invalid data found when processing input"
## 
## handle directory paths with spaces/unusual characters
## 
## handle directory symbolic links
## 
## handle has_argument function with more system-agnostic code
##


## ================
## DATA / FLAGS

# default values and processing variables
dryrun_mode=false
verbose_mode=false
force_overwrite=false
mediasource=""
mediasource_has_results=false
next_mediasource=""
video_input_framerate=25
video_output_framerate=25

# Display script usage
usage() {
	echo "Usage:"
	echo "    ffmpeg_convert_video.sh [OPTIONS]"
	echo "Command line examples:"
	echo "    For a single video file"
	echo "    >    ffmpeg_convert_video.sh --dry-run -m /path/to/video/folder/YYYY-MM-DD/video.h264"
	echo "    For batch converting a directory:"
	echo "    >    ffmpeg_convert_video.sh --dry-run -fpsi 15 -fpso 15 -m /path/to/video/folder/YYYY-MM-DD/"
	echo "Options:"
	echo "    --dry-run        Enable dryrun_mode to check files but exit before processing"
	echo "    -fpsi            Input video frame rate (integer, ex. default 25)"
	echo "    -fpso            Output video frame rate (integer, ex. default 25)"
	echo "    -h, --help       Display this help message"
	echo "    -m, --media      (required)"
	echo "                     Path to individual video (/path/to/video.h264)"
	echo "                     or to directory for batch convert (/path/to/directory/)"
	echo "    -o, --overwrite  Force overwrite of any existing converted file"
	echo "                     (Default is to skip already converted files)"
	echo "    -v, --verbose    Enable verbose mode"
	echo "Outcome:"
	echo "    ffmpeg will convert each video (filename.h264) to a new format (filename.mp4)"
	echo "    New files are saved beside originals in the same directory"
}

has_argument() {
	[[ ("$1" == *=* && -n ${1#*=}) || ( ! -z "$2" && "$2" != -*)  ]];
}

extract_argument() {
	echo "${2:-${1#*=}}"
}

# Function to handle options and arguments
handle_options() {
	while [ $# -gt 0 ]; do
		case $1 in

			# display usage guide and exit
			-h | --help)
				usage
				exit 0
				;;

			# mediasource argument is required
			-m | --media*)
				# return error if not provided
				if ! has_argument $@; then
					echo "ERROR: Specify file or directory to convert." >&2
					usage
					exit 1
				fi
				# if argument provided then update variable
				mediasource=$(extract_argument "$@")
				shift
				;;

			# enable "dry-run" which always uses verbose comments
			--dry-run)
				dryrun_mode=true
				verbose_mode=true
				;;

			# define framerate for video input
			--fpsi)
				video_input_framerate=$(extract_argument "$@")
				shift
				;;

			# define framerate for video output
			--fpso)
				video_output_framerate=$(extract_argument "$@")
				shift
				;;

			# enable force_overwrite
			-o | --overwrite)
				force_overwrite=true
				;;

			# enable verbose comments
			-v | --verbose)
				verbose_mode=true
				;;

			# no other parameters are recognized
			*)
				echo "ERROR: Invalid option: $1" >&2
				usage
				exit 1
				;;

		esac
		shift
	done
}

## ================
## Primary video conversion function
## relies on global variable $next_mediasource
## being reset before function is called

convert_next_mediasource() {

	# Check that file exists
	if [ ! -f "$next_mediasource" ]
	then
		echo "ERROR: This does not appear to be a file:"
		echo ">   $next_mediasource"
		exit 1
	fi

	# extract names
	mediasource_dirname=$(dirname -- "$next_mediasource")
	mediasource_basename=$(basename -- "$next_mediasource")
	mediasource_shortname="${mediasource_basename%.*}"
	#mediasource_extension="${mediasource_basename##*.}"
	
	# form destination filepath
	destination_filepath="${mediasource_dirname}/${mediasource_shortname}.mp4"

	if [ "$dryrun_mode" = true ] ; then
		echo "Data processing review:"
		echo "    filepath              = ${next_mediasource}"
		echo "    mediasource_dirname   = ${mediasource_dirname}"
		echo "    mediasource_basename  = ${mediasource_basename}"
		echo "    mediasource_shortname = ${mediasource_shortname}"
		echo "    destination_filepath  = ${destination_filepath}"
	fi

	printf "    $mediasource_shortname [√] file found";

	# if a matching mp4 already exists then skip file
	if [ -f "${destination_filepath}" ] && test "${force_overwrite}" = false ; then
		printf " ... SKIP since mp4 file already exists \n";
		return 1;
	fi;
	# if force_overwrite matching mp4
	if [ -f "${destination_filepath}" ] && test "${force_overwrite}" = true ; then
		printf " ... force overwrite existing mp4";
	fi;

	# if dry-run mode enabled then stop before processing anything
	if [ "$dryrun_mode" = true ] ; then
		printf " ... SKIP - dry-run mode \n";
		return 1;
	fi

	## ================================
	## CONVERT
	##
	## specify framerate of input with "-r" before "-i"
	## specify framerate of output with "-r" after "-i"
	## -an = no audio
	## -f  = force format
	## -y  = overwrite output
	## -copyts = Copy timestamps from input to output
	## -map_metadata
	
	## hide ffmpeg logs by default
	ffmpeg_hide_banner=" -hide_banner "
	ffmpeg_loglevel=" -loglevel error "
	## show ffmpeg logs if in verbose_mode
	if [ "$verbose_mode" = true ] ; then
	 	ffmpeg_hide_banner=""
	 	ffmpeg_loglevel=""
	fi;

	# convert now
	ffmpeg \
		-r ${video_input_framerate} \
		-i "${next_mediasource}" \
		-r ${video_output_framerate} \
		-filter:v fps=fps=${video_output_framerate}:round=near \
		-c:v libx264 \
		-pass 1 \
		-an \
		-copyts \
		-map_metadata 0 \
		-y \
		${ffmpeg_hide_banner} ${ffmpeg_loglevel} \
		"${destination_filepath}"
	
	# copy metadata between files from source to destination
	touch -r "${next_mediasource}" "${destination_filepath}" 

	printf " [√] DONE \n";

	# reset global variable to blank
	next_mediasource=""

}

## ================
# Begin execution and handle main script commands
handle_options "$@"

if [ "$dryrun_mode" = true ] ; then
	echo "Beginning dry-run...";
fi

# ----------------
# Review data

# Check that mediasource is specified
if [ -z "${mediasource}" ] ; then

	echo "ERROR: Specify the media source";
	usage;
	exit 0;

else

	if [ "$verbose_mode" = true ] ; then
		echo "Preparing to process media source:";
		echo "    ${mediasource}";
	fi

fi

# ----------------
# Check if mediasource is a single file
if [ -f "${mediasource}" ] ; then

	# note that results were found
	mediasource_has_results=true
	# queue this item as next media source to be converted
	next_mediasource=${mediasource}
	# run conversion now
	convert_next_mediasource
	
else

	if [ "$verbose_mode" = true ] ; then
		echo "WARNING: Media source is not a file.";
	fi

fi

# ----------------
# Check if mediasource is a directory
if [ -d "${mediasource}" ] ; then

	echo "BATCH CONVERT ${mediasource}"
	if [ "$verbose_mode" = true ] ; then
		count=$(find "$mediasource" -type f -name "*.h264" | wc -l);
		echo "FOUND:   Directory does exist, and matching .h264 file count = $count";
	fi

	# note that results were found
	mediasource_has_results=true

	# run individual convert command for each .h264 file
	for directory_item in $(find "${mediasource}" -type f -name "*.h264");
	do
		# queue this item as next media source to be converted
		next_mediasource=${directory_item}
		# run conversion now
		convert_next_mediasource
	done;

	echo "BATCH COMPLETED";

else

	if test "$verbose_mode" = true  && test "$mediasource_has_results" = false ; then
		echo "WARNING: Media source is not a directory.";
	fi

fi


if test "$mediasource_has_results" = false ; then
	echo "ERROR:   Nothing could be converted!";
	echo "";
fi

exit;