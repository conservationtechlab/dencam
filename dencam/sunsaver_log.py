import minimalmodbus
import math
import csv
import os
from serial import SerialException
from datetime import datetime


def get_free_space(media_path):
    try:
        statvfs = os.statvfs(media_path)
        bytes_available = statvfs.f_frsize * statvfs.f_bavail
        gigabytes_available = bytes_available/1000000000
        return gigabytes_available
    except FileNotFoundError:
        return 0


def log_solar_info():
    solar_list = ['init']
    now = datetime.now()
    date_time_string = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    try:
        SunSaver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    except SerialException:
        solar_list = [date_time_string + ' USB PORT ERROR']
    SunSaver.serial.baudrate = 9600
    SunSaver.serial.stopbits = 2
    try:
        volt_batt = str(math.trunc(SunSaver.read_register(8) * 100 * 2**-(15)))
        volt_arr = str(SunSaver.read_register(9) * 100 * 2**-(15))
        volt_ld = str(math.trunc(SunSaver.read_register(10) * 100 * 2**-(15)))
        curr_chrg = str(math.trunc(SunSaver.read_register(11) * 79.16 * 2**-(15)))
        curr_ld = str(math.trunc(SunSaver.read_register(12) * 79.16 * 2**-(15)))
        temp_amb = str(SunSaver.read_register(15))
        temp_rts = str(SunSaver.read_register(16))
        charge_state = str(SunSaver.read_register(17))
        ah_charge = str(SunSaver.read_register(45) * 0.1)
        ah_load = str(SunSaver.read_register(46) * 0.1)
        alarm = SunSaver.read_register(50)
        alarm_list = ["RTS open", "RTS shorted", "RTS disconnected",
                      "Ths open", "Ths shorted", "SSMPTT hot", "Current limit",
                      "Current offset", "Undefind", "Undefined", "Uncalibrated",
                      "RTS miswire", "Undefined", "Undefined", "miswire",
                      "PET open", "P12", "High Va current limit", "Alarm 19",
                      "Alarm 20", "Alarm 21", "Alarm 22", "Alarm 23", "Alarm 24"]
        solar_list = ['Date:' + date_time_string,
                      ' Batt Volts:' + volt_batt, ' Array volts:' + volt_arr,
                      ' Load volts:' + volt_ld,
                      ' curr Charge:' + curr_chrg, ' Load:' + curr_ld,
                      ' Amb temp(c):' + temp_amb, ' RTS temp(c):' + temp_rts,
                      ' Charge state:' + charge_state,
                      ' Ah charge:' + ah_charge, ' Ah load:' + ah_load,
                      ' Alarm:' + alarm_list[alarm]]
    except (minimalmodbus.NoResponseError,
            minimalmodbus.InvalidResponseError,
            SerialException):
        solar_list = [date_time_string + ' ERROR READING FROM SUNSAVER']
    SunSaver.serial.close()
    if True:
        if not os.path.exists('/home/pi/dencam/solar.csv'):
            header_row = ['Date', 'Time', 'Batt Volts',
                          'Array volts', 'Load volts',
                          'Charge curr.', 'Load curr',
                          'Ambient Temp', 'RTS Temp',
                          'Charge state', 'Ah charge',
                          'Ah load', 'Alarm']
            with open('/home/pi/dencam/solar.csv', 'a') as csv_file:
                csvwriter = csv.writer(csv_file, delimiter=' ')
                csvwriter.writerow(header_row)
        with open('/home/pi/dencam/solar.csv', 'a') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            csvwriter.writerow(solar_list)


log_solar_info()
