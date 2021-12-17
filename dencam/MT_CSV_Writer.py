import threading
import time
import minimalmodbus
import math
import csv
import os
import getpass
import sys
from serial import SerialException
from datetime import datetime



class CSV_Writer(threading.Thread):
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.filename = filename


    def get_Solarlog_info(self):
        try:   # checks USB connection
            SunSaver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
        except SerialException:
            return "SUNSAVER NOT CONNECTED TO USB"
        SunSaver.serial.baudrate = 9600
        SunSaver.serial.stopbits = 2
        try:   # checks for SunSaver connection
            V_batt = math.trunc(SunSaver.read_register(8) * 100 * 2**-(15))
        except minimalmodbus.NoResponseError:
            return "CANNOT READ FROM SUNSAVER"
        # date time, to be replaced with pi clock
        date = datetime.now().strftime("%d/%m/%Y")
        time = datetime.now().strftime("%H:%M:%S")
        # voltage
        V_array = math.trunc(SunSaver.read_register(9) * 100 * 2**-(15))
        V_load = math.trunc(SunSaver.read_register(10) * 100 * 2**-(15))
        # current
        C_charge = math.trunc(SunSaver.read_register(11) * 79.16 * 2**-(15))
        C_load = math.trunc(SunSaver.read_register(12) * 79.16 * 2**-(15))
        # temps
        T_hs = SunSaver.read_register(13)
        T_amb = SunSaver.read_register(15)
        T_rts = SunSaver.read_register(16)

        # charge state
        c_state = SunSaver.read_register(17)

        # Ah(dailys)
        Ah_c = SunSaver.read_register(45) * 0.1
        Ah_l = SunSaver.read_register(45) * 0.1
        # alarm
        alarm = SunSaver.read_register(49)
        alarm_list = ["RTS open", "RTS shorted" , "RTS disconnected",
                     "Ths open", "Ths shorted", "SSMPTT hot", "Current limit",
                     "Current offset", "Undefind", "Undefined", "Uncalibrated",
                     "RTS miswire", "Undefined", "Undefined", "miswire",
                     "PET open", "P12", "High Va current limit", "Alarm 19",
                     "Alarm 20", "Alarm 21" , "Alarm 22", "Alarm 23", "Alarm 24"]
        log = [date, time, V_batt, V_array, V_load,
           C_charge, C_load, T_hs, T_amb, T_rts,
           c_state, Ah_c, Ah_l, alarm_list[alarm]]
        return log
        
    def run(self):
        while(True):
            line = self.get_Solarlog_info()
            with open("/home/pi/"+ self.filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter='\t')
                csvwriter.writerow(line)
            time.sleep(43200) # should be 12 hoursish
             
'''
    def get_path(self):
        STORAGE_LIMIT = 0.5
        user = getpass.getuser()
        log.debug("User is '{}'".format(user))
        media_dir = os.path.join('/media', user)

    # this try block protects against the user not even having a folder in
    # /media which can happen if no media has ever been attached under
    # that user
        try:
            media_devices = os.listdir(media_dir)
        except FileNotFoundError:
            media_devices = []

        default_path = os.path.join('/home', user)
        if media_devices:
            media_devices.sort()
            strg = ', '.join(media_devices)
            
        
        free_space = recorder.get_free_space()
        
    '''

        