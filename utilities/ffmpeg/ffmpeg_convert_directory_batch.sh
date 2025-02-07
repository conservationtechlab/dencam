#!/bin/sh

## ================
## ffmpeg_convert_directory_batch.sh
## 
## Batch convert a folder of Pi camera recordings
## from .h264 to .mp4
##
## Dependencies:
## *	[ffmpeg](https://www.ffmpeg.org/)
## *	ffmpeg_convert_file.sh
##
## For a single batch from the command line:
## >    ffmpeg_convert_directory_batch.sh --dry-run -d /path/to/video/folder/YYYY-MM-DD/
##
## For a prepared batch file use:
## >    "${ffmpeg_convert_directory_batch}" --dry-run -d "/path/to/video/folder/YYYY-MM-DD/"


## ================
## DATA / FLAGS

# default variable values
dryrun_mode=false
verbose_mode=false
directory=""
video_input_framerate=25
video_output_framerate=25

# load any settings unique to this machine
source=ffmpeg_conf.sh

# find script files beside this one
ffmpeg_convert_file_script="$(dirname "$0")/ffmpeg_convert_file.sh"


# Display script usage
usage() {
	echo "Usage:"
	echo "    ffmpeg_batch_convert_directory.sh [OPTIONS]"
	echo "Options:"
	echo "    -h, --help       Display this help message"
	echo "    -d, --directory  All videos within will be batch converted."
	echo "                     Use /path/to/directory/ (including trailing slash, escape spaces)"
	echo "    --dry-run        Enable dryrun_mode to check all files but exit before processing"
	echo "    -v, --verbose    Enable verbose mode"
	echo "Outcome:"
	echo "    Use ffmpeg will convert each video (filename.h264) to a new format (filename.mp4)"
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

for filepath in $(find "${directory}" -type f -name "*.h264");
do

	# extract names
	f_dirname=$(dirname -- "$filepath")
	f_basename=$(basename -- "$filepath")
	f_shortname="${f_basename%.*}"
	#f_extension="${f_basename##*.}"
	
	if( "$dryrun_mode" = true) then
		echo "Data processing review:"
		echo "    filepath    = ${filepath}"
		echo "    f_dirname   = ${f_dirname}"
		echo "    f_basename  = ${f_basename}"
		echo "    f_shortname = ${f_shortname}"
		#echo "    f_extension = ${f_extension}"
	fi

	# if a matching mp4 already exists then skip file
	if [ -f "${f_dirname}/${f_shortname}.mp4" ]
	then
		echo "SKIP - $f_shortname - mp4 file already exists";
		continue;
	fi;

	# if dry-run mode enabled then stop before processing anything
	if("$dryrun_mode" == true) then
		echo "SKIP - dry-run mode";
		continue;
	fi

	if("$verbose_mode" == true) then
		echo "READY - $f_shortname";
	fi;

	# run conversion
	# todo check for script exit code for success/failure
	"${ffmpeg_convert_file_script}" "$filepath"

done;

printf "BATCH COMPLETED";
echo "";

exit;