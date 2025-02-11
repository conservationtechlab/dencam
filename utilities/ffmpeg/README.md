# ffmpeg_dencam_convert README

Convert Pi camera recordings from .h264 to .mp4
either from individual files (/path/to/video.h264)
or batch convert entire folders (/path/to/directory/)

Start with:

>  ffmpeg_dencam_convert.sh --help

Dependencies:

* [ffmpeg](https://www.ffmpeg.org/) version 7.1 (not tested on earlier versions)


## ================
## Prepare data

Gather data from your file structure:

* avoid spaces in file names
* if you are using a cloud storage service, make sure files are already synced locally

Convert a single video to determine your intended frame rate and duration.

Use the ffmpeg's related tool "ffprobe" if you need to analyze video files:

>	ffprobe \
>		-v error \
>		-show_format \
>		-show_streams \
>		/path/to/media/folder/video.h264 \
>		> /path/to/media/folder/video-ffprobe.txt


## ================
## Examples


For a sample video series like this:

>   /path/to/video/folder/YYYY-MM-DD/video001.h264
>   /path/to/video/folder/YYYY-MM-DD/video002.h264
>   /path/to/video/folder/YYYY-MM-DD/video003.h264


Convert an individual file, from the command line:

>   ffmpeg_dencam_convert.sh \
>		--dry-run \
>		-m /path/to/video/folder/YYYY-MM-DD/video001.h264


Batch convert a folder, from the command line:

>   ffmpeg_dencam_convert.sh \
>		--dry-run \
>		-m /path/to/video/folder/YYYY-MM-DD/


Use --fpsi and --fpso flags to set framerate (default is 25):

>   ffmpeg_dencam_convert.sh \
>		--dry-run \
>		--fpsi 15 --fpso 15 \
>		-m /path/to/video/folder/YYYY-MM-DD/


From within a prepared batch shell file use quotes, and run a batch command per folder:

>	"${ffmpeg_dencam_convert}" --dry-run -m "/path/to/video/folder/2024-02-26/"
>	"${ffmpeg_dencam_convert}" --dry-run -m "/path/to/video/folder/2024-02-27/"
>	"${ffmpeg_dencam_convert}" --dry-run -m "/path/to/video/folder/2024-02-28/"


Default behaviour is to skip any files that have already been encoded. If you need to force overwrite on specific command use the "-o" or "--overwrite" flag.

>	"${ffmpeg_dencam_convert}" \
>		--dry-run \
>		--overwrite \
>		--fpsi 15 --fpso 15 \
>		-m "/path/to/video/folder/2024-02-26/video.h264"
