import socket
import subprocess

import netifaces as ni


def get_network_info():
    interfaces = ni.interfaces()
    text = (socket.gethostname() + '\n')
    for interface in interfaces:
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
        except KeyError:
            # This try block is a quick way to just skip an
            # interface if it isn't connected.
            continue

        text += ('{}: {}\n'.format(interface, ip))
        if interface == 'wlan0':
            ssid = subprocess.check_output(['iwgetid'])
            text += (ssid.decode('utf-8').split(' ')[-1])

    return text
