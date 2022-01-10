import minimalmodbus
import math
import csv
import os
import getpass
from serial import SerialException
from datetime import datetime



# filename = "Log_2021_HalfDay.csv"


def get_Solarlog_info():
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
    log = ["Date: " + str(date), "Time: " + str(time),
	"Battery voltage: " + V_batt,"Voltage array: " +  V_array,
	"Load Voltage: " + V_load,"Charge curent: " + C_charge,
	"Charge load: " + C_load, "HeatSink: " + T_hs, "Ambient" + T_amb,
	"Remote sensor: "+ T_rts,"Charge" + c_state,"AH charge:" + Ah_c,
	"Ah load: " + Ah_l, "Alarm: " + alarm_list[alarm]]
    return log

# def MPPT_LOGGER():
line = get_Solarlog_info()
user = getpass.getuser()
user_dir = os.path.join('/home',user)
media_dir = os.path.join(user_dir,'/dencam')
path = '/home/' + user +'/dencam/'
with open(path + 'SOLARLOG_HD.csv', 'a') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='\t')
    csvwriter.writerow(line)

#MPPT_LOGGER()
