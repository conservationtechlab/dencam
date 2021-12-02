#had to install minimalmodbus

import minimalmodbus
import math
import os
import getpass
import csv 
from datetime import datetime

SunSaver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
SunSaver.serial.baudrate = 9600
SunSaver.serial.stopbits = 2
def get_solar_info():
    #voltage
  
    V_battery = math.trunc(SunSaver.read_register(8) * 100 * 2 **-(15))
    V_array = SunSaver.read_register(9) * 100 * 2 **-(15)
    V_load = math.trunc(SunSaver.read_register(10) * 100 * 2 **-(15))
    #current
    C_charge = SunSaver.read_register(11) * 79.16  * 2**-(15)
    C_load = SunSaver.read_register(12)  * 79.16  * 2**-(15)
    #temperature, 'C
    T_heatsink = SunSaver.read_register(13)
    # daily amp-hours
    # resets after dark
    Ah_charge = SunSaver.read_register(45) * 0.1
    Ah_load = SunSaver.read_register(46) * 0.1
    list = [V_battery,V_array,V_load,C_charge,C_load,
            T_heatsink,Ah_charge,Ah_load]
    V = 'V_Battery:' + str(V_battery)+ ' V_array:'+ str(V_array)+ '\nV_load:' + str(V_load)
    C = 'C_Charge:' + str(C_charge) + ' c_load:' + str(C_load)
    T = 'T_heatsink: ' +  str(T_heatsink) + 'C'
    Ah= 'Ah_Charge:' + str(Ah_charge) +' Ah_Load:' + str(Ah_load)
    cvs_w(list)        
    return V,C,T,Ah
def cvs_w(list):
    feild_names = ['Battery voltage', 'Voltage array','Load voltage',
                   'Battery charge', 'Load charge', 'HeatSink temp(C)'
                   'Ah charge', 'Ah load']
    
    date = datetime.now().strftime("%d/%m/%Y")
    time = datetime.now().strftime("%H:%M:%S")
    user = getpass.getuser()
    default_path = os.path.join('/home', user)
    if not os.path.exists(default_path):
        os.mkdirs(default_path)
    with open(default_path + '/solar_log.cvs', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([i for i in feild_names])
        for j in map(str,list):
            writer.writerow(j)
        
                
        
        
    
    
    
    
    