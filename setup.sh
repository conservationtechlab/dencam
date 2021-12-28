#!/bin/bash

# Disable screen saver blanking, turn off DPMS,
# and disable blanking the video device
sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart > /dev/null << EOF
@xset s off
@xset -dpms
@xset s noblank
EOF

# Display the values of all current X Window
# System preferences
xset -q
