import time
import yaml
import cv2
from threading import Thread
import threading
from ptzipcam.camera import Camera
from ptzipcam.ptz_camera import PtzCam
from ptzipcam import ui
from pyPS4Controller.controller import Controller
import RPi.GPIO as GPIO
import numpy as np


class CamView:
    """Class to manage camera stream display."""
    
    def __init__(self, ip, user, passwd, stream, orientation, headless):
        self.cam = Camera(ip=ip, user=user, passwd=passwd, stream=stream)
        self.orientation = orientation
        self.headless = headless
        self.running = False
        pin = 27
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.window_created = False

        self.last_button_state = GPIO.input(pin)
        self.last_press_time = time.time()


    def start_stream(self):
        self.running = True
        if not self.headless and not self.window_created:
            print("6.5, checked if headless or not and will now attempt to create windows i guess")
            cv2.namedWindow("Control PTZ Camera", cv2.WINDOW_NORMAL)
            print("6.6 apparently but not really, should have just created the named window")
            cv2.setWindowProperty("Control PTZ Camera", cv2.WND_PROP_TOPMOST, 1)
            cv2.setWindowProperty("Control PTZ Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.moveWindow("Control PTZ Camera", 0, -30)
            cv2.resizeWindow("Control PTZ Camera", 320, 240)
            print("7. inside ptz_control start stream, window should have been created")


        while self.running:
            frame = self.cam.get_frame()
            if frame is not None:
                frame = ui.orient_frame(frame, self.orientation)
                if not self.headless:
                    cv2.imshow('Control PTZ Camera', frame)
                    cv2.waitKey(33)
            if self.check_button_press():
                self.stop_stream()
                break

    def check_button_press(self):
        current_state = GPIO.input(27)
        current_time = time.time()

        if current_state == GPIO.LOW and self.last_button_state == GPIO.HIGH and (current_time - self.last_press_time) >0.2:
            self.last_press_time = current_time
            self.last_button_state = current_state
            return True

        self.last_button_state = current_state
        return False

    def stop_stream(self):
        self.running = False
        cv2.destroyAllWindows()
        print("inside cambiew class in ptz_control, should have stopped stream function and closed windows")
        time.sleep(1)

class PS4Controller(Controller):
    """Class to manage PTZ control via PS4 controller."""
    
    def __init__(self, ptz, stop_flag, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ptz = ptz
        self.fine_movement = False
        self.toggleOn = False
        self.stop_flag = stop_flag
        self.t = time.time()  # Initialize time tracking for command delays
        self.timeout = 0.5  # Delay between commands
        self.Y_DELTA = .05
        self.X_DELTA = .05
        self.Z_DELTA = .07
        self.X_DELTA_FINE = self.X_DELTA/3
        self.Y_DELTA_FINE = self.Y_DELTA/3
        self.Z_DELTA_FINE = self.Z_DELTA/3

    def ready_for_next(self):
        """Check if enough time has passed to issue the next command."""
        return (time.time() - self.t) > self.timeout

    def send_command(self, x_delta, y_delta, z_delta):
        """Send movement commands to the PTZ camera only if there is a change."""
        pan, tilt, zoom = self.ptz.get_position()

        # Calculate new positions
        cmds = {
            'pan': pan + x_delta,
            'tilt': tilt + y_delta,
            'zoom': zoom + z_delta
        }

        # Send the new pan, tilt, and zoom commands to the PTZ camera
        self.drive_ptz(cmds)

        # Update the time for the next command
        self.t = time.time()

    def scale_joystick_value(self, v):
        """Scale joystick value to be within the 0-1 range."""
        return v / 35000

    # Arrow buttons - handle movement commands with time check and fine movement
    def on_right_arrow_press(self):
        if self.ready_for_next():
            x_delta = -self.X_DELTA_FINE if self.fine_movement else -self.X_DELTA
            self.send_command(x_delta, 0, 0)

    def on_left_arrow_press(self):
        if self.ready_for_next():
            x_delta = self.X_DELTA_FINE if self.fine_movement else self.X_DELTA
            self.send_command(x_delta, 0, 0)

    def on_up_arrow_press(self):
        if self.ready_for_next():
            y_delta = -self.Y_DELTA_FINE if self.fine_movement else -self.Y_DELTA
            self.send_command(0, y_delta, 0)

    def on_down_arrow_press(self):
        if self.ready_for_next():
            y_delta = self.Y_DELTA_FINE if self.fine_movement else self.Y_DELTA
            self.send_command(0, y_delta, 0)

    def on_left_right_arrow_release(self):
        pass

    def on_up_down_arrow_release(self):
        pass

    # Left Joystick - continuous motion for pan/tilt
    def on_L3_up(self, value):
        if self.ready_for_next():
            v = max(-1, self.scale_joystick_value(value))
            self.send_command(0, v, 0)

    def on_L3_down(self, value):
        if self.ready_for_next():
            v = min(1, self.scale_joystick_value(value))
            self.send_command(0, v, 0)

    def on_L3_right(self, value):
        if self.ready_for_next():
            v = max(-1, self.scale_joystick_value(value))
            self.send_command(-v, 0, 0)

    def on_L3_left(self, value):
        if self.ready_for_next():
            v = min(1, self.scale_joystick_value(value))
            self.send_command(-v, 0, 0)

    def on_L3_x_at_rest(self):
        self.ptz.stop()

    def on_L3_y_at_rest(self):
        self.ptz.stop()

    # Right Joystick - continuous zoom
    def on_R3_up(self, value):
        if self.ready_for_next():
            self.ptz.move_w_zoom(0, 0, self.scale_joystick_value(value))

    def on_R3_down(self, value):
        if self.ready_for_next():
            self.ptz.move_w_zoom(0, 0, self.scale_joystick_value(-value))

    def on_R3_right(self, value):
        pass

    def on_R3_left(self, value):
        pass

    def on_R3_y_at_rest(self):
        self.ptz.stop()

    # Fine Movement Toggle (L1 button press)
    def on_L1_press(self):
        self.fine_movement = True

    def on_L1_release(self):
        self.fine_movement = False

    # Exposure/Focus Toggle
    def on_R1_press(self):
        self.toggleOn = True

    def on_R1_release(self):
        self.toggleOn = False

    # Zoom in
    def on_triangle_press(self):
        self.send_command(0, 0, self.Z_DELTA)

    # Zoom out fully
    def on_square_press(self):
        self.ptz.zoom_in_full()

    # Zoom in fully
    def on_circle_press(self):
        self.ptz.zoom_out_full()

    # Set exposure or zoom out
    def on_x_press(self):
        if self.toggleOn:
            self.ptz.set_exposure_to_auto()
        else:
            self.send_command(0, 0, -self.Z_DELTA)

    def drive_ptz(self, cmds):
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
        INFINITE_PAN = True
        CAM_PAN_MAX = 1.0
        CAM_PAN_MIN = -1.0
        CAM_TILT_MAX = 1.0
        CAM_TILT_MIN = -1.0
        CAM_ZOOM_MAX = 1.0
        CAM_ZOOM_MIN = 0

        if INFINITE_PAN:
            cmds['pan'] = wrap_pan(cmds['pan'], CAM_PAN_MIN, CAM_PAN_MAX)
        else:
            cmds['pan'] = keep_in_bounds(cmds['pan'], CAM_PAN_MIN, CAM_PAN_MAX)
        cmds['tilt'] = keep_in_bounds(cmds['tilt'], CAM_TILT_MIN, CAM_TILT_MAX)
        cmds['zoom'] = keep_in_bounds(cmds['zoom'], CAM_ZOOM_MIN, CAM_ZOOM_MAX)

#    print(f'prepped zoom command - {cmds["zoom"]}')

        self.ptz.absmove_w_zoom(cmds['pan'],
                           cmds['tilt'],
                           cmds['zoom'])

    def custom_listen(self):
        while not self.stop_flag.is_set():
            try:
                events = self.read_input()
                for event in events:
                    self.process_event(event)
            except Exception as e:
                print(f"error while listening: {e}")
                break

    def read_input(self):
        return super().read()

    def process_event(self, event):
        super().handle_event(event)

    
class PTZControlSystem:
    """Class to manage the overall PTZ control system."""

    def __init__(self, configs, stream_override=None):
#         with open(config_file, 'r', encoding='utf-8') as f:
  #          configs = yaml.load(f, Loader=yaml.SafeLoader)
        self.cam_view = None
        self.ptz = PtzCam(configs['IP'], configs['PORT'], configs['USER'], configs['PASS'])
        self.controller = None
        self.controller_thread = None
        self.stop_flag = threading.Event()
        self.ip = configs['IP']
        self.user = configs['USER']
        self.passwd = configs['PASS']
        self.stream = stream_overrise if stream_override else configs['STREAM']
        self.orientation = configs['ORIENTATION']
        self.headless = configs['HEADLESS']
        self.cam_view = CamView(
            self.ip,
            self.user,
            self.passwd,
            self.stream,
            self.orientation,
            self.headless)

    def start_system(self):
        self.cam_view.start_stream()
        print("4. started stream")


    def start_control(self):
        self.controller = PS4Controller(self.ptz, stop_flag=self.stop_flag, interface='/dev/input/js0', connecting_using_ds4drv=False)

    def _run_controller(self):
        self.controller.custom_listen()

    def stop_system(self):
        print("attempting to call stop_stream function in camview class inside ptz_control")
        self.cam_view.stop_stream()
        print("should have stopped system inside ptz_control, stopped stream")

    def stop_control(self):
        if self.controller_thread and self.controller_thread.is_alive():
            self.stop_flag.set()
            self.controller_thread.join()
        self.controller = None
        self.controller_thread = None
        self.stop_flag.clear()

# Main script
if __name__ == "__main__":
    config_file = "cyclops_config.yaml"
    
    # Initialize system
    ptz_system = PTZControlSystem(config_file)

    # Start streaming and controller
    ptz_system.start_system()
    ptz_system.cam_view.display_stream()
  #  print("started display and control, waiting 5 seconds before starting controls")
    # Example usage: disable control after 10 seconds
    time.sleep(5)
#    ptz_system.start_control()
 #   print("control started, waiting 10 seconds before disabling control")
   # time.sleep(10)
    #ptz_system.stop_control()
   # print("stopped control, waiting 5 seconds to disable screen")
    # Stop system after 20 seconds
   # time.sleep(5)
    print("stopping stream, waiting 5 seconds to reenable stream")
    ptz_system.stop_stream()
    time.sleep(5)
    ptz_system.start_system()
    ptz_system.cam_view.display_stream()
    time.sleep(5)
    print("screen should be reinitialized")


