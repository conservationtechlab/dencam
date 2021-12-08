#!/bin/bash

# Disable screensaver and screen blanking
sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart > /dev/null << EOF
@xset s off
@xset -dpms
@xset s noblank
EOF

# Display the values of all current X Window
# System preferences
xset -q

# Run setup.py to install Dencam dependencies
python setup.py install