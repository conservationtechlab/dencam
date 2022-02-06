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


class AirplaneMode:

    def __init__(self, configs):
        apm = configs['AIRPLANE_MODE']
        if apm is True:
            self.ap_mode_on()
        if apm is False:
            self.ap_mode_off()
        self.enabled = apm

    def ap_mode_off(self):
        subprocess.call("rfkill unblock wlan", shell=True)
        subprocess.call("rfkill unblock bluetooth", shell=True)

    def ap_mode_on(self):
        subprocess.call("rfkill block wlan", shell=True)
        subprocess.call("rfkill block bluetooth", shell=True)

    def toggle(self):
        if self.enabled:
            self.ap_mode_off()
            self.enabled = False
        elif self.enabled is False:
            self.ap_mode_on()
            self.enabled = True
