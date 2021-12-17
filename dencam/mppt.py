import minimalmodbus
import math
from serial import SerialException

<<<<<<< HEAD

=======
>>>>>>> Write CSV file
def get_solardisplay_info():
    try:   # checks USB connection
        SunSaver = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    except SerialException:
        return "SUNSAVER NOT CONNECTED TO USB"
    SunSaver.serial.baudrate = 9600
    SunSaver.serial.stopbits = 2
    try:   # checks for SunSaver connection
        V_battery = math.trunc(SunSaver.read_register(8) * 100 * 2**-(15))
    except minimalmodbus.NoResponseError:
        return "CANNOT READ FROM SUNSAVER"

    V_array = SunSaver.read_register(9) * 100 * 2**-(15)

    C_charge = math.trunc(SunSaver.read_register(11) * 79.16 * 2**-(15))
    C_load = math.trunc(SunSaver.read_register(12) * 79.16 * 2**-(15))

    T_amb = SunSaver.read_register(15)

    Ah_charge = SunSaver.read_register(45) * 0.1
    Ah_load = SunSaver.read_register(45) * 0.1

    V = "Battery Volt:" + str(V_battery)
    V += " Array Volt:" + str(V_array)
    A = 'Charge current:' + str(C_charge)
    A += ' Load Current:' + str(C_load)
    T = " Ambient Temp:" + str(T_amb) + "c"
    Ah = "Ah charge:" + str(Ah_charge)
    Ah += " Ah load:" + str(Ah_load)
    return V + '\n' + A + '\n' + T + '\n' + Ah
