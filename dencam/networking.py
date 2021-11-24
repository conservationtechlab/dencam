"""Networking module

This module contains code related to networking.  As DenCam currently
does not actively use any available networks this is restricted to
tools for getting information about the network, mostly to display
them on the Networking Page so users can easily access this
information.

"""

import socket
import subprocess

import netifaces as ni


def get_network_info():
    """Function to acquire networking information

    Allows DenCam to get information about its networking state,
    including the SSID of the wireless AP it is attached to, and its
    own IP address on the various networking interfaces it is
    currently using.

    """
    interfaces = ni.interfaces()
    text = (socket.gethostname() + '\n')
    for interface in interfaces:
	if interface == 'lo':
	    continue
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
        except KeyError:
            # This try block is a quick way to just skip an
            # interface if it isn't connected.
            continue

        text += ('{}: {}\n'.format(interface, ip))
        if interface == 'wlan0':
            ssid = subprocess.check_output(['iwgetid'])
            text += (ssid.decode('utf-8').split('ESSID:')[-1].replace('"', ''))

    return text
