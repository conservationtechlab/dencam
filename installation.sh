#!/bin/bash

# Disable screen saver blanking, turn off DPMS, and disable blanking
# the video device (in that order)
sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart > /dev/null << EOF
@xset s off
@xset -dpms
@xset s noblank
EOF

# Display the values of all current X Window System preferences.
# Under the 'Screen Saver' section, 'prefer blanking' should be set to 'no'.
# Under the 'DPMS (Energy Star)' section, it should say 'DPMS is Disabled'.
xset -q