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
ports on the Pi (e.g. uSD card readers). This hardware is typically
integrated into a larger assembly that includes a weatherproof
enclosure, batteries, charger controller, and external solar panels.


# Installing from PyPI

    pip install dencam

# Installing from GitHub repository

### Install virtualenvwrapper

     pip3 install virtualenvwrapper

### Create a .virtualenvs folder to hold all virtual environments

     mkdir ~/.virtualenvs

### Add python path and source to ~/.bashrc file

     export WORKON_HOME=$HOME/.virtualenvs
     export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
     export VIRTUALENVWRAPPER_VIRTUALENV=/home/pi/.local/bin/virtualenv
     source ~/.local/bin/virtualenvwrapper.sh

### Create virtual environment

     mkvirtualenv dencam

Note that DenCam requires Python 3 so if the default on your system is
Python 2, make sure the virtual environment will use Python 3:

      mkvirtualenv dencam -p python3

### Activate virtual environment

     workon dencam

### Clone the dencam repository

     git clone https://github.com/icr-ctl/dencam.git

### Update apt package sources list

     sudo apt update

### Install dencam dependencies

     cd ~/dencam
     python setup.py install

# Usage

## On Raspberry Pi 

The core program in the project is `dencam.py` which runs on the
Raspberry Pi which is controlling the field device. It accepts a YAML
configuration file as a command line argument. There is an example
config file `./cfgs/example_config.yaml`

You can copy this example file and modify it to your specific purposes
and thus then run DenCam on a properly set up system (see Setup
section above for how to set up system) via:

```
Usage:
    ./dencam.py cfgs/YOUR_CONFIG_FILE.yaml
    
```



