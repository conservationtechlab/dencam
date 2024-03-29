import csv
import os
from datetime import datetime
from io import StringIO

import minimalmodbus
from serial import SerialException


alarm_list = ["RTS open", "RTS shorted", "RTS disconnected",
              "Ths open", "Ths shorted", "SSMPTT hot",
              "Current limit", "Current offset",
              "Undefind", "Undefined", "Uncalibrated",
              "RTS miswire", "Undefined", "Undefined", "miswire",
              "PET open", "P12", "High Va current limit",
              "Alarm 19", "Alarm 20", "Alarm 21",
              "Alarm 22", "Alarm 23", "Alarm 24"]

field_names = ['Date', 'Time', 'Battery_Voltage', 'Array_Voltage',
               'Load_Voltage', 'Charge_Current', 'Load_Current',
               'Ambient_Temp', 'RTS_Temp', 'Charge_State',
               'Ah_Charge', 'Ah_Load', 'Alarm', 'MPPT_Error']


def get_solardisplay_info():
    if not os.path.exists('/home/pi/dencam/solar.csv'):
        return 'File Does Not Exist'
    with open('/home/pi/dencam/solar.csv', newline='', encoding='utf8') as cf:
        parsed_csvfile = cf.read()
        parsed_csvfile = parsed_csvfile.replace('\x00', '')
        reader = csv.DictReader(StringIO(parsed_csvfile))
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


def float_to_string(value):
    return "{:.1f}".format(value)


def log_solar_info():
    usb_error = False
    solar_list = ['init']
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    time_string = now.strftime('%Hh%Mm%Ss')
    try:
        SunSaver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    except SerialException:
        usb_error = True
        solar_list = [date_string, time_string,
                      'N/A', 'N/A', 'N/A', 'N/A',
                      'N/A', 'N/A', 'N/A', 'N/A',
                      'N/A', 'N/A', 'N/A',
                      'USB PORT ERROR']
    if not usb_error:
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
            solar_list = [date_string,
                          time_string,
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
