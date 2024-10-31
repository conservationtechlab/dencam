"""Functions to interface with SunSaver

"""
import csv
import os
from datetime import datetime
from io import StringIO
import argparse
import yaml

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
    """Read the solar data from CSV file and format it for display"""
    path = get_file_path()
    solar_log = os.path.join(path, "solar.csv")
    if not os.path.exists(solar_log):
        error_msg = "Solar information\nnot found.\nPress " + \
                    "second\nbutton and refer to \nset-up" + \
                    " instructions"
        return error_msg
    with open(solar_log, newline='',
              encoding='utf8') as solar:
        parsed_csvfile = solar.read()
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
    usb_error = last_row['MPPT_Error']
    if usb_error == "USB PORT ERROR":
        solar_text = "Check USB connection\nfrom solar charge\n" + \
                     "controller to Pi\nand press second\nbutton"
    return solar_text


def float_to_string(value):
    """Turn numerical input to string for display"""
    return f"{value:.1f}"


def log_solar_info():
    """Read solar data from the SunSaver and write it to a CSV file"""
    usb_error = False
    solar_list = ['init']
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    time_string = now.strftime('%Hh%Mm%Ss')
    try:
        sunsaver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    except SerialException:
        usb_error = True
        solar_list = [date_string, time_string,
                      'N/A', 'N/A', 'N/A', 'N/A',
                      'N/A', 'N/A', 'N/A', 'N/A',
                      'N/A', 'N/A', 'N/A',
                      'USB PORT ERROR']
    if not usb_error:
        sunsaver.serial.baudrate = 9600
        sunsaver.serial.stopbits = 2
        try:
            volt_batt = sunsaver.read_register(8) * 100 * 2**-(15)
            volt_arr = sunsaver.read_register(9) * 100 * 2**-(15)
            volt_ld = sunsaver.read_register(10) * 100 * 2**-(15)
            curr_chrg = sunsaver.read_register(11) * 79.16 * 2**-(15)
            curr_ld = sunsaver.read_register(12) * 79.16 * 2**-(15)
            temp_amb = sunsaver.read_register(15)
            temp_rts = sunsaver.read_register(16)
            charge_state = sunsaver.read_register(17)
            ah_charge = sunsaver.read_register(45) * 0.1
            ah_load = sunsaver.read_register(46) * 0.1
            alarm = sunsaver.read_register(50)
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
        sunsaver.serial.close()
    path = get_file_path()
    solar_log = os.path.join(path, "solar.csv")
    if not os.path.exists(solar_log):
        with open(solar_log, 'w', newline='',
                  encoding='utf8') as csvfile:
            csvwriter = csv.DictWriter(csvfile, fieldnames=field_names)
            csvwriter.writeheader()
    with open(solar_log, 'a', newline='',
              encoding='utf8') as csv_file:
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


def get_file_path():
    '''Function to read config file and obtain directory
    for solar log

    Returns: string containing file path of solar directory
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file',
                        help='Filename of configuration file')
    args = parser.parse_args()
    with open(args.config_file, encoding='utf-8') as config:
        configs = yaml.load(config, Loader=yaml.SafeLoader)
    path_to_dir = configs['SOLAR_DIR']
    return path_to_dir
