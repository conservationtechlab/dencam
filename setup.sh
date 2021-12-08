#!/bin/bash

# Disable screensaver and screen blanking
sudo bash -c 'cat >> /etc/xdg/lxsession/LXDE-pi/autostart << EOL
@xset s off
@xset -dpms
@xset s noblank
EOL'

# Display the values of all current X Window
# System preferences
xset -q

# Run setup.py to install Dencam dependencies
python setup.py install