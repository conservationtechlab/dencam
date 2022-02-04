# Overview

This repository contains control code for Mini DenCam, a polar bear
maternal den observation device.  The project is a collaboration
between the Conservation Technology Lab at the San Diego Zoo Wildlife
Alliance and Polar Bears International.

# Hardware

The target hardware is a Raspberry Pi 4 Model B single board computer
with a Picamera-style camera and the AdaFruit PiTFT screen (2.8"
resistive touch model with 4 GPIO-connected buttons)
attached. Typically several storage devices are connected via the USB
ports on the Pi (e.g. microSD card readers). 

This hardware is typically integrated into a larger assembly that
includes a weatherproof enclosure, batteries, solar charge controller,
and external solar panels.  Documentation of the full mechanical and
electrical design and construction of the DenCam system is not
included here but it is hoped that this code (which only needs the
components explicitly mentioned in the preceding paragraph) can still
be useful to others who are pursuing related projects or want to
contribute to the DenCam project.

# Operating System

Currently DenCam runs on Raspian Stretch and Buster.  Problems have
been encountered with Bullseye (specifically with interfacing with the
picamera).

# Screen setup

TODO: add instructions for setting up PiTFT screen using script from
adafruit.  Possibly we should include the script in the repo.

# Installing from PyPI

    pip install dencam

# Installing from GitHub repository

### Install virtualenvwrapper

     sudo pip3 install virtualenv virtualenvwrapper

### Setup virtual environment  ~/.bashrc file

     echo -e "\n# Virtual environment setup" >> ~/.bashrc
     echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
     echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
     echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
     source ~/.bashrc

### Create virtual environment for dencam project

    mkvirtualenv dencam_env

Note that DenCam requires Python 3 so if the default on your system is
Python 2, make sure the virtual environment will use Python 3:

       mkvirtualenv dencam_env -p python3

### Activate virtual environment (not necessary if you just made it)

    workon dencam_env

### Clone the dencam repository

    git clone https://github.com/icr-ctl/dencam.git

### Update apt package sources list

    sudo apt update

### Install dencam dependencies

    cd dencam
    python setup.py install

# Usage

## On Raspberry Pi 

The core program in the project is `dencam.py` which runs on the
Raspberry Pi that is controlling the field device. It accepts a YAML
configuration file as a command line argument. There is an example
config file `./cfgs/example_config.yaml`

You can copy this example file and modify it to your specific purposes
and thus then run DenCam on a properly set up system (see Setup
section above for how to set up system) via:

```
Usage:
    ./dencam.py cfgs/YOUR_CONFIG_FILE.yaml
    
```

If you are connected to the Raspberry Pi via SSH, then first do:
```
   export DISPLAY=:0
```
## Explanation of parameters in the configuration file

TODO

## Using the DenCam user interface

The DenCam user interface is through the PiTFT screen.  It does not
use the touchscreen functionality of the screen: the screen itself is
only used for display and the top two physical buttons beside the
screen are used for control.  DenCam will start with the screen blank.
The top button will advance the display through a series of status
pages:

* Networking Information Page
* Recording Status Page
* Camera Preview Page
* Blank page with screen illumination disabled
* Solar Display Page

On the Recording Status Page, the second button will toggle recording
on and off (recording will begin automatically after the countdown set
in the configuration file without needing to use this control).

On the Camera Preview Page, the same second button will toggle between
the full resolution camera view and a one-to-one pixel view intended
to aid in focusing the camera (the camera is focused manually).

## Setting up DenCam to run on boot

TODO

## Setting up RTC

For RPi's not connected to the internet a suitable battery powered hardware
clock will be required.

Install clock overhanging the board farthest away from the USB plugs.Follow
directions on the website exactly.

Adafruit RTC 1st Steps 
https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-up-and-test-i2c

Adafruit RTC 2nd Steps
https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time



Enter the following

    sudo i2cdetect -y 1

Be sure you see the device 68 show up in the matrix as seen below. If not,
double check your connections.

    $   0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- 
    70: -- -- -- -- -- -- -- --
    
After the hardware checks out add support for the RTC by adding a device
tree overlay. Run

    sudo nano /boot/config.txt

to the end of the file add

    dtoverlay=i2c-rtc,ds3231
 
Control x, and Y to save the file. Run the following to reboot

    sudo reboot
    
Log in and run the following to see if the UU shows up where 0x68 should be

    sudo i2cdetect -y 1

UU should show as it does in the matrix below

    $   0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- UU -- -- -- -- -- -- -- 
    70: -- -- -- -- -- -- -- --
    
Disable the "fake hwclock" which interferes with the 'real' hwclock by
entering the following

    sudo apt-get -y remove fake-hwclock
    sudo update-rc.d -f fake-hwclock remove
    sudo systemctl disable fake-hwclock
    
Now with the fake-hwclock off, you can start the original 'hardware clock'
script

Run the following

    sudo nano /lib/udev/hwclock-set

comment out these lines:

    #if[-e/run/systemmd/system];then
    #exit 0
    #fi
    #/sbin/hwclock --rtc=$dev --systz --badyear
    #/sbin/hwclock --rtc=$dev --systz

Run 

    date

to verify the time is correct. If not, double check your internet connection
and reboot to allow the NTP to pull the correct date and time from the 
internet.

When date reads correctly run

    sudo hwclock -w
    sudo hwclock -r
    sudo reboot
    
 
