#!/usr/bin/env python
"""Aim PTZ camera using a PS4 Controller

Useful for testing connection: RTSP stream capture and display, ONVIF
control of PTZ, mechanical functioning of PTZ, etc.

"""
import time
import argparse
from threading import Thread

import yaml
import cv2

from ptzipcam.camera import Camera
from ptzipcam.ptz_camera import PtzCam
from ptzipcam import ui, convert

from pyPS4Controller.controller import Controller

parser = argparse.ArgumentParser()
parser.add_argument('config',
                    help='Filename of configuration file')
parser.add_argument('-s',
                    '--stream',
                    default=None,
                    help='Stream to use if want to override config file.')
parser.add_argument("-r",
                    "--replace",
                    action="store_true",
                    help='Toggle replacing of init PTZ values in config file.')
args = parser.parse_args()
CONFIG_FILE = args.config

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    configs = yaml.load(f, Loader=yaml.SafeLoader)

# ptz camera networking constants
IP = configs['IP']
PORT = configs['PORT']
USER = configs['USER']
PASS = configs['PASS']
if args.stream is None:
    STREAM = configs['STREAM']
else:
    STREAM = int(args.stream)

HEADLESS = configs['HEADLESS']

# ptz camera setup constants
# INIT_POS = configs['INIT_POS']
ORIENTATION = configs['ORIENTATION']

INFINITE_PAN = configs['INFINITE_PAN']
CAM_TILT_MIN = configs['CAM_TILT_MIN']
CAM_TILT_MAX = configs['CAM_TILT_MAX']
CAM_PAN_MIN = configs['CAM_PAN_MIN']
CAM_PAN_MAX = configs['CAM_PAN_MAX']
CAM_ZOOM_MIN = configs['CAM_ZOOM_MIN']
CAM_ZOOM_MAX = configs['CAM_ZOOM_MAX']
CAM_ZOOM_POWER = configs['CAM_ZOOM_POWER']

Y_DELTA = .05
Y_DELTA_FINE = Y_DELTA/3
X_DELTA = .05
X_DELTA_FINE = X_DELTA/3
#Z_DELTA = configs['CAM_ZOOM_STEP']
Z_DELTA = .07
Z_DELTA_FINE = Z_DELTA / 3
E_DELTA = 1000.0
E_DELTA_FINE = 100.0
G_DELTA = 5.0
G_DELTA_FINE = 1.0
I_DELTA = 5.0
I_DELTA_FINE = 1.0
F_TIME = 1
F_TIME_FINE = .05

Z_SPEED = 0.1
if ORIENTATION == 'down':
    Y_DELTA = -Y_DELTA
    Y_DELTA_FINE = -Y_DELTA_FINE
    X_DELTA = -X_DELTA
    X_DELTA_FINE = -X_DELTA_FINE

ptz = PtzCam(IP, PORT, USER, PASS)


class CamView(Thread):
    """Grabs and displays stream from camera

    """

    def run(self):
        """Thread function of CamView class

        """
        cam = Camera(ip=IP, user=USER, passwd=PASS, stream=STREAM)

        while True:
            # retrieve and display frame
            frame = cam.get_frame()
            if frame is not None:
                frame = ui.orient_frame(frame, ORIENTATION)
                if not HEADLESS:
                    cv2.namedWindow('Control PTZ Camera', cv2.WINDOW_NORMAL)
                    #cv2.resizeWindow('Control PTZ Camera', 640, 420)
                    cv2.resizeWindow('Control PTZ Camera', 320, 210)
                    cv2.imshow('Control PTZ Camera', frame)
                    _ = cv2.waitKey(33)
                else:
                    time.sleep(.033)

class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

        self.fineMovementOn = False
        self.toggleOn = False
        self.focusMode = False

        self.yJoystickReleased = False
        self.t = time.time()
        self.timeout = .5

    def send_command(self, x_delta, y_delta, z_delta):
        cmds = {}
        pan, tilt, zoom = ptz.get_position()
        cmds['pan'] = pan + x_delta
        cmds['tilt'] = tilt + y_delta
        cmds['zoom'] = zoom + z_delta
        drive_ptz(cmds)
        return cmds

    def display_status(self, cmds):
        print(f'Pan: {cmds["pan"]} | Tilt: {cmds["tilt"]} | Zoom: {cmds["zoom"]}')

    def scale_joystick_value(self, v):
        # scales joystick value to be within 0-1 range
        return v/35000

    def ready_for_next(self):
        # checks timeout time to send new command
        return (time.time() - self.t > self.timeout)

    # Arrow Buttons - step pan/tilt
    # TODO: scale fine movement by zoom amount
    def on_left_arrow_press(self):
        if self.ready_for_next():
            if self.fineMovementOn:
                commands = self.send_command(X_DELTA_FINE, 0 , 0)
                self.t = time.time()
            else:
                commands = self.send_command(X_DELTA, 0, 0)
            #self.display_status(commands)

    def on_right_arrow_press(self):
        if self.ready_for_next():
            if self.fineMovementOn:
                commands = self.send_command(-X_DELTA_FINE, 0, 0)
                self.t = time.time()
            else:
                commands = self.send_command(-X_DELTA, 0, 0)
            #self.display_status(commands)

    def on_up_arrow_press(self):
        if self.ready_for_next():
            if self.fineMovementOn:
                commands = self.send_command(0, -Y_DELTA_FINE, 0)
                self.t = time.time()
            else:
                commands = self.send_command(0, -Y_DELTA, 0)
            #self.display_status(commands)

    def on_down_arrow_press(self):
        if self.ready_for_next():
            if self.fineMovementOn:
                commands = self.send_command(0, Y_DELTA_FINE, 0)
                self.t = time.time()
            else:
                commands = self.send_command(0, Y_DELTA, 0)
            #self.display_status(commands)

    def on_left_right_arrow_release(self):
        pass
    def on_up_down_arrow_release(self):
        pass

    # Left Joystick - continuous motion
    def on_L3_up(self, value):
       if self.ready_for_next():
           v = max(-1, self.scale_joystick_value(value))
           self.t = time.time()
           ptz.move(0, v)

    def on_L3_down(self, value):
        if self.ready_for_next():
            v = min(1, self.scale_joystick_value(value))
            self.t = time.time()
            ptz.move(0, v)

    def on_L3_right(self, value):
        if self.ready_for_next():
            v = max(-1, self.scale_joystick_value(value))
            #v = min(1, self.scale_joystick_value(value))
            self.t = time.time()
            ptz.move(-v, 0)

    def on_L3_left(self, value):
        if self.ready_for_next():
            #v = max(-1, self.scale_joystick_value(value))
            v = min(1, self.scale_joystick_value(value))
            self.t = time.time()
            ptz.move(-v, 0)

    def on_L3_x_at_rest(self):
        ptz.stop()

    def on_L3_y_at_rest(self):
        ptz.stop()

    # Right Joystic - continuous Zoom 
    def on_R3_up(self, value):
        if self.ready_for_next():
            ptz.move_w_zoom(0,0, self.scale_joystick_value(value))
            self.t = time.time()

    def on_R3_down(self, value):
        if self.ready_for_next():
            ptz.move_w_zoom(0,0, self.scale_joystick_value(-value))
            self.t = time.time()

    def on_R3_right(self, value):
        pass

    def on_R3_left(self, value):
        pass

    def on_R3_y_at_rest(self):
        ptz.stop()

    # Fine Movement Toggle
    def on_L1_press(self):
        self.fineMovementOn = True

    def on_L1_release(self):
        self.fineMovementOn = False

    # Exposure/Focus Toggle
    def on_R1_press(self):
        self.toggleOn = True

    def on_R1_release(self):
        self.toggleOn = False

    def on_triangle_press(self):
        # zoom in
        self.send_command(0, 0, Z_DELTA)

    def on_square_press(self):
        ptz.zoom_in_full()
        #if self.fineMovementOn:
        #    ptz.update_iris(I_DELTA_FINE)
        #else:
        #    ptz.update_iris(I_DELTA)
        #print(f'IRIS: {ptz.get_imaging_settings().Exposure["Iris"]}')

    def on_circle_press(self):
        ptz.zoom_out_full()        # if toggle is on, toggle  auto focus/manual focus
        #if self.toggleOn:
        #    focusMode = ptz.get_imaging_settings().Focus['AutoFocusMode']
        #    if focusMode == 'AUTO':
        #        ptz.set_focus_to_manual()
        #    else:
        #        ptz.set_focus_to_auto()
        #else:
        #    pass
        #print(f'Focus Mode: {ptz.get_imaging_settings().Focus["AutoFocusMode"]}')

    def on_x_press(self):
        # if toggle is on, set exposure to AUTO
        if self.toggleOn:
            ptz.set_exposure_to_auto()
        # else decrease zoom
        else:
            #if self.fineMovementOn:
            #    ptz.update_iris(-I_DELTA_FINE)
            #else:
            #    ptz.update_iris(-I_DELTA)
            self.send_command(0, 0, -Z_DELTA)
        #print(f'IRIS: {ptz.get_imaging_settings().Exposure["Iris"]}')

def drive_ptz(cmds):
    """Prep and send actual pan, tilt, zoom commands to camera

    """
    def keep_in_bounds(command, minn, maxx):
        if command <= minn:
            command = minn
        elif command >= maxx:
            command = maxx
        return command

    def wrap_pan(command, minn, maxx):
        if command <= minn:
            command = maxx - minn + command
        elif command >= maxx:
            command = minn - maxx + command
        return command

    if INFINITE_PAN:
        cmds['pan'] = wrap_pan(cmds['pan'], CAM_PAN_MIN, CAM_PAN_MAX)
    else:
        cmds['pan'] = keep_in_bounds(cmds['pan'], CAM_PAN_MIN, CAM_PAN_MAX)
    cmds['tilt'] = keep_in_bounds(cmds['tilt'], CAM_TILT_MIN, CAM_TILT_MAX)
    cmds['zoom'] = keep_in_bounds(cmds['zoom'], CAM_ZOOM_MIN, CAM_ZOOM_MAX)

#    print(f'prepped zoom command - {cmds["zoom"]}')

    ptz.absmove_w_zoom(cmds['pan'],
                       cmds['tilt'],
                       cmds['zoom'])




def main():
    """Main function of the program

    """
    if not HEADLESS:
        camview = CamView()
        camview.setDaemon(True)
        camview.start()

    controller = MyController(interface='/dev/input/js0', connecting_using_ds4drv=False)
    controller.listen()

    # after curses closed print out PTZ values on CLI
    pan, tilt, zoom = ptz.get_position()
    pan_deg = convert.command_to_degrees(pan, 360.0)
    tilt_deg = convert.command_to_degrees(tilt, 90.0)
    zoom_power = convert.zoom_to_power(zoom, CAM_ZOOM_POWER)

    print(f'Pan: {pan_deg:.2f} Tilt: {tilt_deg:.2f}, Zoom: {zoom_power:.1f}')

    if args.replace:
        print("Writing new PTZ coordinates into config file.")
        ptzstr = f"INIT_POS: [{pan_deg:.2f}, {tilt_deg:.2f}, {zoom_power:.2f}]"
        with open(CONFIG_FILE, "r+", encoding='utf-8') as file:
            lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith("INIT_POS:"):
                    lines[i] = ptzstr + "\n"
                    file.seek(0)  # Move the file pointer to the beginning
                    file.writelines(lines)  # Write the modified lines
                    file.truncate()  # Truncate any remaining content
                    break  # Stop searching once the line is found


if __name__ == "__main__":
    main()
