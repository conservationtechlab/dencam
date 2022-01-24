# Overview

This repository contains control code for Mini DenCam, a polar bear
maternal den observation device.  The project is a collaboration
between the Conservation Technology Lab at the San Diego Zoo Wildlife
Alliance and Polar Bears International.

# Hardware

The target hardware is a Raspberry Pi 4 Model B single board computer
with a Picamera-style camera and the AdaFruit PiTFT screen (2.8"
resistive touch model with 4 GPIO-connected buttons) attached.
Typically, several storage devices are connected via the USB
ports on the Pi (e.g. microSD card readers).

This hardware is typically integrated into a larger assembly that
includes a weatherproof enclosure, batteries, solar charge controller,
and external solar panels. Documentation of the full mechanical and
electrical design and construction of the DenCam system is not
included here but it is hoped that this code (which only needs the
components explicitly mentioned in the preceding paragraph) can still
be useful to others who are pursuing related projects or want to
contribute to the DenCam project.

# Operating System

Currently, DenCam runs on Raspian Stretch and Buster. Problems have
been encountered with Bullseye (specifically with interfacing with the
picamera).

# Install from PyPI

    pip install dencam

# Install from GitHub repository

## Install virtualenvwrapper

    sudo pip3 install virtualenv virtualenvwrapper

## Setup virtual environment ~/.bashrc file

```sh
echo -e "\n# Virtual environment setup" >> ~/.bashrc
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc
```

## Create virtual environment for dencam project

    mkvirtualenv dencam_env

Note that DenCam requires Python 3 so if the default on your system is
Python 2, make sure the virtual environment will use Python 3:

    mkvirtualenv dencam_env -p python3

## Activate virtual environment (not necessary if you just made it)

    workon dencam_env

## Clone the dencam repository

    git clone https://github.com/icr-ctl/dencam.git

## Update apt package sources list

    sudo apt update

## Install dencam dependencies

    cd dencam
    python setup.py install

## Execute install.sh

    sudo chmod u+x install.sh
    ./install.sh

The above terminal commands give execution permission to the current user
and then executes the `install.sh` script. When the script asks if you'd like
to reboot, enter 'Y' for yes. Rebooting is necessary for the settings to take
effect. Note: this script should only be ran once. The script will do the
following:

* Disable screen saver
* Setup PiTFT screen

# Usage

## On Raspberry Pi 

The core program in the project is `dencam.py` which runs on the
Raspberry Pi that is controlling the field device. It accepts a YAML
configuration file as a command line argument. There is an example
config file `./cfgs/example_config.yaml`

You can copy this example file and modify it to your specific purposes
and thus then run DenCam on a properly set up system (see Setup
section above for how to set up system) via:

    Usage:
        ./dencam.py cfgs/YOUR_CONFIG_FILE.yaml

If you are connected to the Raspberry Pi via SSH, then first do:

    export DISPLAY=:0

## Explanation of parameters in the configuration file

The configuration file stores variables used throughout the dencam 
code.

### RECORD_LENGTH

Takes a positive integer value of the length each recording will be
(in seconds). Passing a value of 300 will make each recording 5 min.

### STORAGE_LIMIT
Takes in a positive float value which will be the minimum amount of storage
(in gigabytes) necessary in order to start a recording.

### DISPLAY_RESOLUTION

Takes two integer values, used to set the resolution of the display 
pages of the Dencam.

### PAUSE_BEFORE_RECORD

Takes in a positive integer value which will be the seconds to wait
after the dencam has initially started until the first recording begins

### POWER_OFF_DELAY

Controls the amount of time the off button needs to be held down for, until 
the Pi shuts down.

### CAMERA_RESOLUTION

Takes in two positive integers that will be used to dictate the resolution
of the camera.

### VIDEO_QUALITY

Takes in a positive integer in the range from 1-40, 1 being the highest, 
40 being the lowest.

### FRAME_RATE

Controls the frame rate of the recordings, taking in a postive integer 
from the range 1-60. The higher the number the smoother the recording, 
but the quality of the recording reduces.We found through testing that 30 
is a decent halfway point, where the recording is smooth enough and the 
change in quality is not as noticable.

### CAMERA_ROTATION

Controls the rotation of the Camera display by taking in a positve integere
representing the oreintation in degrees. To have the camera display in
landscape, pass values 0 or 180.

## Using the DenCam user interface

The DenCam user interface is through the PiTFT screen.  It does not
use the touchscreen functionality of the screen: the screen itself is
only used for display and the top two physical buttons beside the
screen are used for control.  DenCam will start on the Recording Page.
The top button will advance the display through a series of status
pages:

* Networking Information Page
* Recording Status Page
* Solar Display Page
* Camera Preview Page
* Blank page with screen illumination disabled

On the Recording Status Page, the second button will toggle recording
on and off (recording will begin automatically after the countdown set
in the configuration file without needing to use this control).

On the Camera Preview Page, the same second button will toggle between
the full resolution camera view and a one-to-one pixel view intended
to aid in focusing the camera (the camera is focused manually).

# Dencam Pages

The Dencam user interface has 5 pages, which are traversed using the 
top button. Each page is displaying information designated to itself.
(i.e. Solar Display Page displays information recieved from Sun Saver)

## Networking Information Page

This page displays Raspberry Pi username, wLan0 IP address, and the name of 
the wifi signal it is connected to.

## Recording Status Page

Displays the current number of video recordings saved and stores, the file
directory they are currently being stored to, the amount of available
storage, time stamp, and a countdown for the recording to start.

## Solar Display Page

This page displays data recieved from the SunSaver decive in realtime.
Currently it displays Battery Voltage(V), Array Voltage(V),
Charge current(A), Load current(A), Ah charge(Daily)(Ah), and
Ah load(Daily)(Ah).

## Camera Preview Page

Displays timestamp and current feed of the Camera, note this feed is 
not necessarily being recorded.

## Blank page with screen illumination disabled

Is a blank page that displays no information, mainly used as a 
background for the Camera Preview Page.

## Setting up DenCam to run on boot

TODO

## Setting up RTC

TODO
