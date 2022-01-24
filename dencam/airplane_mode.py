import os


class AirplaneMode:

    def __init__(self, configs):
        APM = configs['AIRPLANEMODE']
        if APM:
            self.AP_Mode_ON()
        else:
            self.AP_Mode_OFF()

    def AP_Mode_ON(self):
        os.system("rfkill block wlan")
        os.system("rfkill block bluetooth")
        self.Enabled = True

    def AP_Mode_OFF(self):
        os.system("rfkill unblock wlan")
        os.system("rfkill unblock bluetooth")
        self.Enabled = False

    def get_Enabled(self):
        return self.Enabled
