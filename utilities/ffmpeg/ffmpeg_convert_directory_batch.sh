#!/bin/sh

## ================
## ffmpeg_convert_directory_batch.sh
##
## Batch convert a folder of Pi camera recordings
## from .h264 to .mp4
##
## Dependencies:
## *	[ffmpeg = 7.1](https://www.ffmpeg.org/)
##
## For a single batch from the command line:
## >    bash ffmpeg_convert_directory_batch.sh --dry-run -d /path/to/video/folder/YYYY-MM-DD/
##
## For a prepared batch file use:
## >    bash "${ffmpeg_convert_directory_batch}" --dry-run -d "/path/to/video/folder/YYYY-MM-DD/"


## ================
## DATA / FLAGS

# default variable values
dryrun_mode=false
verbose_mode=false
directory=""
video_input_framerate=25
video_output_framerate=25

# load any settings unique to this machine
#source=ffmpeg_conf.sh


# Display script usage
usage() {
	echo "Usage:"
	echo "    ffmpeg_batch_convert_directory.sh [OPTIONS]"
	echo "Options:"
	echo "    -h, --help       Display this help message"
	echo "    -d, --directory  Folder containing all videos to be batch converted (required data)"
	echo "                     Use /path/to/directory/ (including trailing slash, escape spaces)"
	echo "    --dry-run        Enable dryrun_mode to check all files but exit before processing"
	echo "    -fpsi            Input video frame rate (integer, ex. default 25)"
	echo "    -fpso            Output video frame rate (integer, ex. default 25)"
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

			-d | --directory*)
				# directory argument is required
				# return error if not provided
				if ! has_argument $@; then
					echo "ERROR: Directory was not specified." >&2
					usage
					exit 1
				fi
				# if argument provided then update variable
				directory=$(extract_argument "$@")
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
# Handle main script commands
handle_options "$@"

# ----------------
# Review data

if("$dryrun_mode" = true) then echo "Beginning dry-run..."; fi

# Check that directory is specified
if [ -z "${directory}" ]
then
	echo "ERROR: Specify the media directory as in:"
	echo ">    ffmpeg_batch_convert_directory.sh /path/to/directory/including\ escaped\ spaces/"
	exit 0
else
	if("$verbose_mode" = true) then
		echo "Preparing to process directory:";
		echo "    ${directory}";
	fi
fi

# Check if directory exists
if [ -d "${directory}" ]
then
	if("$verbose_mode" = true) then
		count=$(find "$directory" -type f -name "*.h264" | wc -l);
		echo "Directory does exist, and matching .h264 file count = $count";
	fi
else
	echo "ERROR: directory not found"
	echo "    ${directory}"
	exit 0
fi


## ================
## CONVERT EACH FILE

for source_filepath in $(find "${directory}" -type f -name "*.h264");
do

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


	if( "$dryrun_mode" = true) then
		echo "Data processing review:"
		echo "    filepath    = ${filepath}"
		echo "    source_dirname   = ${source_dirname}"
		echo "    source_basename  = ${source_basename}"
		echo "    source_shortname = ${source_shortname}"
		#echo "    source_extension = ${source_extension}"
	fi

	# if a matching mp4 already exists then skip file
	if [ -f "${destination_filepath}" ]
	then
		echo "SKIP - $source_shortname - mp4 file already exists";
		continue;
	fi;

	# if dry-run mode enabled then stop before processing anything
	if("$dryrun_mode" == true) then
		echo "SKIP - dry-run mode";
		continue;
	fi

	if("$verbose_mode" == true) then
		printf "READY - $source_shortname";
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

done;

echo "BATCH COMPLETED";

exit;
