import minimalmodbus
import csv
import os
from serial import SerialException
from datetime import datetime


def get_solardisplay_info():
    if not os.path.exists('/home/pi/dencam/solar.csv'):
        return 'File Does Not Exist'
    with open('/home/pi/dencam/solar.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            last_row = row
    solar_text = last_row['Date'] + '\n' + last_row['Time']
    solar_text += '\nBattery Voltage: ' + last_row['Battery_Voltage']
    solar_text += '\nArray Voltage: ' + last_row['Array_Voltage']
    solar_text += '\nCharge Current: ' + last_row['Charge_Current']
    solar_text += '\nLoad Current: ' + last_row['Load_Current']
    solar_text += '\nAh Charge: ' + last_row['Ah_Charge']
    solar_text += '\nAh Load: ' + last_row['Ah_Load']
    solar_text += '\nAlarm: ' + last_row['Alarm']
    solar_text += '\nMPPT_Error: ' + last_row['MPPT_Error']
    return solar_text


def get_free_space(media_path):
    try:
        statvfs = os.statvfs(media_path)
        bytes_available = statvfs.f_frsize * statvfs.f_bavail
        gigabytes_available = bytes_available/1000000000
        return gigabytes_available
    except FileNotFoundError:
        return 0


alarm_list = ["RTS open", "RTS shorted", "RTS disconnected",
              "Ths open", "Ths shorted", "SSMPTT hot", "Current limit",
              "Current offset", "Undefind", "Undefined", "Uncalibrated",
              "RTS miswire", "Undefined", "Undefined", "miswire",
              "PET open", "P12", "High Va current limit", "Alarm 19",
              "Alarm 20", "Alarm 21", "Alarm 22", "Alarm 23", "Alarm 24"]


def float_to_string(value):
    return "{:.1f}".format(value)


def fill_solar_list():
    solar_list = ['init']
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    time_string = now.strftime('%Hh%Mm%Ss')
    try:
        SunSaver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    except SerialException:
        solar_list = [date_string, time_string,
                      'N/A', 'N/A', 'N/A', 'N/A',
                      'N/A', 'N/A', 'N/A', 'N/A',
                      'N/A', 'N/A', 'N/A',
                      'USB PORT ERROR']
        return solar_list
    SunSaver.serial.baudrate = 9600
    SunSaver.serial.stopbits = 2
    try:
        volt_batt = SunSaver.read_register(8) * 100 * 2**-(15)
        volt_arr = SunSaver.read_register(9) * 100 * 2**-(15)
        volt_ld = SunSaver.read_register(10) * 100 * 2**-(15)
        curr_chrg = SunSaver.read_register(11) * 79.16 * 2**-(15)
        curr_ld = SunSaver.read_register(12) * 79.16 * 2**-(15)
        temp_amb = SunSaver.read_register(15)
        temp_rts = SunSaver.read_register(16)
        charge_state = SunSaver.read_register(17)
        ah_charge = SunSaver.read_register(45) * 0.1
        ah_load = SunSaver.read_register(46) * 0.1
        alarm = SunSaver.read_register(50)
        solar_list = [float_to_string(date_string),
                      float_to_string(time_string),
                      float_to_string(volt_batt),
                      float_to_string(volt_arr),
                      float_to_string(volt_ld),
                      float_to_string(curr_chrg),
                      float_to_string(curr_ld),
                      float_to_string(temp_amb),
                      float_to_string(temp_rts),
                      float_to_string(charge_state),
                      float_to_string(ah_charge),
                      float_to_string(ah_load),
                      alarm_list[alarm],
                      'N/A']
    except (minimalmodbus.NoResponseError,
            minimalmodbus.InvalidResponseError,
            SerialException):
        solar_list = [date_string, time_string, 'N/A',
                      'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                      'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                      'NO CONNECTION TO  SUNSAVER']
    SunSaver.serial.close()
    return solar_list


field_names = ['Date', 'Time', 'Battery_Voltage', 'Array_Voltage',
               'Load_Voltage', 'Charge_Current', 'Load_Current',
               'Ambient_Temp', 'RTS_Temp', 'Charge_State',
               'Ah_Charge', 'Ah_Load', 'Alarm', 'MPPT_Error']


def log_solar_info():
    solar_list = fill_solar_list()
    if True:
        if not os.path.exists('/home/pi/dencam/solar.csv'):
            with open('/home/pi/dencam/solar.csv', 'w', newline='') as csvfile:
                csvwriter = csv.DictWriter(csvfile, fieldnames=field_names)
                csvwriter.writeheader()
        with open('/home/pi/dencam/solar.csv', 'a', newline='') as csv_file:
            csvwriter = csv.DictWriter(csv_file, fieldnames=field_names)
            csvwriter.writerow({'Date': solar_list[0],
                                'Time': solar_list[1],
                                'Battery_Voltage': solar_list[2],
                                'Array_Voltage': solar_list[3],
                                'Load_Voltage': solar_list[4],
                                'Charge_Current': solar_list[5],
                                'Load_Current': solar_list[6],
                                'Ambient_Temp': solar_list[7],
                                'RTS_Temp': solar_list[8],
                                'Charge_State': solar_list[9],
                                'Ah_Charge': solar_list[10],
                                'Ah_Load': solar_list[11],
                                'Alarm': solar_list[12],
                                'MPPT_Error': solar_list[13]})


log_solar_info()
