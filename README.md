# Overview

This repository contains control code for Mini DenCam, a polar bear
maternal den observation device. The project is a collaboration
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
picamera). Buster must be 32 bit and not 64 bit otherwise there is an issue
with the libmmal.so library

# Install from PyPI

    pip3 install dencam

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
Python 2 (it is if you are using Buster OS), make sure the virtual environment will use Python 3:

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

## Install dencam dependencies with optional dependencies

Any functionality that is not integrated into the core dencam project requires
optional dependencies to be installed. At the moment, there are two tools that
haven't been integrated: `utilities/examine_focus_w_grid_scipy.py` and
`utilities/examine_focus_w_grid.py`. In order to run either of the files, you
must first install the dencam dependencies with optional dependencies.

    cd dencam
    pip install .[all]

## Execute install.sh

Check if your screen is resistive touch or capacitive touch: If you're unsure,
look on the backside of the screen, there will be two dotted off areas, one
labeled resistive, one labeled capacitive. If the capacitors are connected and the
resistors are not, it is capacitive and you will need to adjust the respective command
within install.sh. If the resistors are connected and the capacitors are not, it is 
resistive and you can keep install.sh how it is. If switching from resistive to capacitive,
you'll change the --display28r command to --display=28c instead. The fbcp parameter
indicates that the screen will mirror onto a monitor if connected via hdmi, which
is preferrable for debugging but feel free to change that as well if you do not
need hdmi mirroring. For more information about the screen setup see [here.](https://learn.adafruit.com/adafruit-2-8-pitft-capacitive-touch/easy-install-2)

    sudo chmod u+x install.sh
    ./install.sh

The above terminal commands give execution permission to the current user
and then executes the `install.sh` script. When the script asks if you'd like
to reboot, enter <kbd>Y</kbd> for yes. Rebooting is necessary for the
settings to take effect. Note: this script should only be run once. The
script will do the following:

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
        ./dencam.py dencam/example_config.yaml

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

Takes in a positive integer in the range of 10 to 40 where 10 is extremely
high quality, and 40 is extremely low. The recommended value should be in the
range of 20 to 25. 

### FRAME_RATE

Controls the frame rate of the recordings, taking in a positive integer in the
range of 1 to 60. The higher the number, the smoother the recording at the
expense of quality. We found through testing that 30 is a decent halfway
point between a smooth recording and an unnoticeable change in quality.

### CAMERA_ROTATION

Controls the rotation of the camera display by taking in a positive integer,
which represents the orientation in degrees. To have the camera display in
landscape, set the value to 0 or 180.

## Using the DenCam user interface

The DenCam user interface is through the PiTFT screen. It does not
use the touchscreen functionality of the screen: the screen itself is
only used for display and the top two physical buttons beside the
screen are used for control. DenCam will start on the OffPage, which
is in the middle of our traversal. DenCam will boot into the OffPage
automatically for power saving purposes. The top button will advance the
display through a series of status pages:

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

On the Network page, the second button will toggle on/off airplane mode.
Note that airplane mode will be enabled or disabled on boot depending on
the variable AIRPLANE_MODE in the config file.

On the Solar page, the second button will allow user to manually log info.
This will also update the information being displayed on the page as well.

## SunSaver device setup

The SunSaver device is able to connect to any usb port on the rasberry pi,
prior to the dencam being booted that is. After which it is not advised to
disconnect while dencam is running. The SunSaver is able to be turned on
and off while dencam is running, the SolarPage will display errors when
SunSaver may be off or there is an errro with the usb connection.


## Setting up cronjobs

Dencam uses a few cronjobs for varying purposes. To set up the cronjob 
for rebooting the dencam every day at 1am use:

    $ sudo nano /etc/crontab

    @reboot         root    hwclock --hctosys --utc
    30 *    * * *   root    hwclock --hctosys --utc
    0  1    * * *   root    /sbin/shutdown -r now

The cronjob that logs SunSaver data every hour uses:

     * * * * * python /home/pi/dencam/dencam/sunsaver_log.py
     
where 'pi' can be interchange with the device's hostname.

## Setting up DenCam to run on boot

TODO

## Setting up RTC

TODO

# Dencam Pages

The Dencam user interface has 5 pages, which are traversed using the 
top button. Each page is displaying information designated to itself.
(i.e. Solar Display Page displays information received from Sun Saver)

## Networking Information Page

This page displays the hostname of the device along with wifi network
information.

## Recording Status Page

This page displays the current number of video recordings that have been
saved and stored, the file directory where the recordings are currently
being written to, the amount of available storage, the timestamp, and a
countdown for the recording to start (which is only used for the initial
dencam boot). When the countdown is complete, the countdown text will be
replaced with the recording status text. The second button is used to
toggle the recording on this page.

## Solar Display Page

This page displays data received from the SunSaver device in real time.
Currently it displays the date and time, Battery Voltage(V), Array Voltage(V),
Charge current(A), Load current(A), Ah charge(Daily)(Ah), and
Ah load(Daily)(Ah).

## Camera Preview Page

This page displays the timestamp and current feed of the Camera. Note that
this feed is not necessarily being recorded. The second button will toggle
the one-to-one pixel tool to aid focusing.

## Blank page with screen illumination disabled

This page is a blank page that displays no information. Its sole purpose
is for power saving.

# Focus Score Tool

## Purpose

The purpose of a focus score tool is to help the user easily focus the
camera. In order to do so, this tool displays a grid over the camera feed
with values in each section of the grid that denote how in focus the camera
is for that given section. Generally, a higher value for a given section
indicates that the section is more in focus, while a lower value indicates
that the section is more out of focus. In order for the camera to be in
focus, you need to manually adjust the lens and see how the values react.
The goal is to have the object or landscape that you're focusing on have the
highest value(s) possible.

## Usage
There are two focus score tools which are each implemented differently.
`utilities/examine_focus_w_grid.py` is an OpenCV-based implementation, while
`utilities/examine_focus_w_grid_scipy.py` is a SciPy-based implementation.
At the moment, the OpenCV-based implementation runs the best out of the two
versions.

### Execute focus score tool

In order to execute the focus score tool, make sure to follow the steps
below in order.

1. SSH into the Raspberry Pi
2. cd into the root directory of the dencam repository\
   i.e. `cd dencam`
3. Activate the virtual environment\
   i.e. `workon dencam_env`
4. Install dencam dependencies with optional dependencies\
   i.e. `pip install .[all]`
5. Execute the focus score tool\
   i.e. `python utilities/examine_focus_w_grid.py` or\
   `python utilities/examine_focus_w_grid_scipy.py`

### Terminate focus score tool

In order to terminate the focus score tool, press
<kbd>Ctrl</kbd> + <kbd>C</kbd> twice. If the program hasn't closed on the
Pi, then perform one of the following actions:

- Tap the PiTFT touchscreen on the Raspberry Pi
- Shake the mouse connected to the Raspberry Pi
- Press any key on the keyboard connected to the Raspberry Pi
