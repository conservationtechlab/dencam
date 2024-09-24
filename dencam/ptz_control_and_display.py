import time
import yaml
import cv2
from threading import Thread
from ptzipcam.camera import Camera
from ptzipcam.ptz_camera import PtzCam
from ptzipcam import ui
from pyPS4Controller.controller import Controller

class CamView:
    """Class to manage camera stream display."""
    
    def __init__(self, ip, user, passwd, stream, orientation, headless):
        self.cam = Camera(ip=ip, user=user, passwd=passwd, stream=stream)
        self.orientation = orientation
        self.headless = headless
        self.running = False

    def start_stream(self):
        self.running = True
        print("starting stream in camview class")
        if not self.headless:
            cv2.namedWindow("Control PTZ Camera", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Control PTZ Camera", cv2.WND_PROP_TOPMOST, 1)
            cv2.setWindowProperty("Control PTZ Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.resizeWindow("Control PTZ Camera", 320, 210)
            print("window should have been created")

        while self.running:
            frame = self.cam.get_frame()
            if frame is not None:
                frame = ui.orient_frame(frame, self.orientation)
                if not self.headless:
                    cv2.imshow('Control PTZ Camera', frame)
                    cv2.waitKey(33)

    def stop_stream(self):
        self.running = False
        cv2.destroyAllWindows()
        

'''class PS4Controller(Controller):
    """Class to manage PTZ control via PS4 controller."""
    
    def __init__(self, ptz, *args, **kwargs):
        Controller.__init__(self, **kwargs)
        self.ptz = ptz
        self.fine_movement = False
        self.enabled = True
        self.t = time.time()  # Initialize the time tracking for command delays
        self.timeout = 0.5  # Delay between commands

    def ready_for_next(self):
        """Check if enough time has passed to issue the next command."""
        return (time.time() - self.t) > self.timeout

    def send_command(self, x_delta, y_delta, z_delta):
        """Send movement commands to the PTZ camera."""
        if self.enabled:
            pan, tilt, zoom = self.ptz.get_position()
            cmds = {
                'pan': pan + x_delta,
                'tilt': tilt + y_delta,
                'zoom': zoom + z_delta
            }
            self.ptz.absmove_w_zoom(cmds['pan'], cmds['tilt'], cmds['zoom'])
            self.t = time.time()  # Update time after command is sent

    def disable_control(self):
        """Disable PTZ control."""
        self.enabled = False

    def enable_control(self):
        """Enable PTZ control."""
        self.enabled = True

    # Arrow buttons - handle movement commands with time check and fine movement
    def on_right_arrow_press(self):
        if self.ready_for_next():
            x_delta = -X_DELTA_FINE if self.fine_movement else -X_DELTA
            self.send_command(x_delta, 0, 0)

    def on_left_arrow_press(self):
        if self.ready_for_next():
            x_delta = X_DELTA_FINE if self.fine_movement else X_DELTA
            self.send_command(x_delta, 0, 0)

    def on_up_arrow_press(self):
        if self.ready_for_next():
            y_delta = -Y_DELTA_FINE if self.fine_movement else -Y_DELTA
            self.send_command(0, y_delta, 0)

    def on_down_arrow_press(self):
        if self.ready_for_next():
            y_delta = Y_DELTA_FINE if self.fine_movement else Y_DELTA
            self.send_command(0, y_delta, 0)

    # Fine movement toggle (L1 button press)
    def on_L1_press(self):
        self.fine_movement = True

    def on_L1_release(self):
        self.fine_movement = False


    def scale_joystick_value(self, v):
        return v / 35000'''


class PS4Controller(Controller):
    """Class to manage PTZ control via PS4 controller."""
    
    def __init__(self, ptz, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ptz = ptz
        self.fine_movement = False
        self.enabled = True
        self.t = time.time()  # Initialize time tracking for command delays
        self.timeout = 0.5  # Delay between commands
        self.previous_commands = {'pan': None, 'tilt': None, 'zoom': None}

    def ready_for_next(self):
        """Check if enough time has passed to issue the next command."""
        return (time.time() - self.t) > self.timeout

    '''def send_command(self, x_delta, y_delta, z_delta):
        """Send movement commands to the PTZ camera only if there is a change."""
        if self.enabled:
            pan, tilt, zoom = self.ptz.get_position()

            # Calculate new positions
            new_pan = pan + x_delta
            new_tilt = tilt + y_delta
            new_zoom = zoom + z_delta

            # Only send commands if there's a change in the values
            if (new_pan != self.previous_commands['pan'] or
                new_tilt != self.previous_commands['tilt'] or
                new_zoom != self.previous_commands['zoom']):
                
                self.ptz.absmove_w_zoom(new_pan, new_tilt, new_zoom)

                # Update previous commands to track the latest position
                self.previous_commands['pan'] = new_pan
                self.previous_commands['tilt'] = new_tilt
                self.previous_commands['zoom'] = new_zoom

                # Update time after command is sent
                self.t = time.time()'''

    def send_command(self, x_delta, y_delta, z_delta):
        """Send movement commands to the PTZ camera only if there is a change, and within bounds."""
        if self.enabled:
        # Get the current pan, tilt, and zoom position
            pan, tilt, zoom = self.ptz.get_position()

        # Calculate the new positions
            new_pan = pan + x_delta
            new_tilt = tilt + y_delta
            new_zoom = zoom + z_delta

        # Ensure the new positions are within the allowed bounds
            new_pan = self.keep_in_bounds(new_pan, self.ptz.CAM_PAN_MIN, self.ptz.CAM_PAN_MAX)
            new_tilt = self.keep_in_bounds(new_tilt, self.ptz.CAM_TILT_MIN, self.ptz.CAM_TILT_MAX)
            new_zoom = self.keep_in_bounds(new_zoom, self.ptz.CAM_ZOOM_MIN, self.ptz.CAM_ZOOM_MAX)

        # Only send the command if there is a change from the previous values
            if (new_pan != self.previous_commands['pan'] or
                new_tilt != self.previous_commands['tilt'] or
                new_zoom != self.previous_commands['zoom']):
            # Send the command to move the camera
                self.ptz.absmove_w_zoom(new_pan, new_tilt, new_zoom)

            # Update the previous command values
                self.previous_commands['pan'] = new_pan
                self.previous_commands['tilt'] = new_tilt
                self.previous_commands['zoom'] = new_zoom

            # Update the time for the next command
                self.t = time.time()

    def keep_in_bounds(self, value, min_value, max_value):
        """Helper function to ensure a value is within the specified bounds."""
        if value < min_value:
            return min_value
        elif value > max_value:
            return max_value
        return value


    def disable_control(self):
        """Disable PTZ control."""
        self.enabled = False

    def enable_control(self):
        """Enable PTZ control."""
        self.enabled = True

    def scale_joystick_value(self, v):
        # scales joystick value to be within 0-1 range
        return v/35000

    # Arrow buttons - handle movement commands with time check and fine movement
    def on_right_arrow_press(self):
        if self.ready_for_next():
            x_delta = -X_DELTA_FINE if self.fine_movement else -X_DELTA
            self.send_command(x_delta, 0, 0)

    def on_left_arrow_press(self):
        if self.ready_for_next():
            x_delta = X_DELTA_FINE if self.fine_movement else X_DELTA
            self.send_command(x_delta, 0, 0)

    def on_up_arrow_press(self):
        if self.ready_for_next():
            y_delta = -Y_DELTA_FINE if self.fine_movement else -Y_DELTA
            self.send_command(0, y_delta, 0)

    def on_down_arrow_press(self):
        if self.ready_for_next():
            y_delta = Y_DELTA_FINE if self.fine_movement else Y_DELTA
            self.send_command(0, y_delta, 0)

    # Joystick movement - handle pan and tilt via joystick, only when values change
    def on_L3_up(self, value):
        if self.ready_for_next():
            v = self.scale_joystick_value(value)
            if v != 0:  # Move only if joystick value is not at rest
                self.send_command(0, v, 0)

    def on_L3_down(self, value):
        if self.ready_for_next():
            v = -self.scale_joystick_value(value)
            if v != 0:
                self.send_command(0, v, 0)

    def on_L3_right(self, value):
        if self.ready_for_next():
            v = self.scale_joystick_value(value)
            if v != 0:
                self.send_command(-v, 0, 0)

    def on_L3_left(self, value):
        if self.ready_for_next():
            v = -self.scale_joystick_value(value)
            if v != 0:
                self.send_command(v, 0, 0)

    def on_L3_x_at_rest(self):
        self.ptz.stop()

    def on_L3_y_at_rest(self):
        self.ptz.stop()

    # Zoom control with right joystick
    def on_R3_up(self, value):
        if self.ready_for_next():
            v = self.scale_joystick_value(value)
            if v != 0:
                self.send_command(0, 0, v)

    def on_R3_down(self, value):
        if self.ready_for_next():
            v = -self.scale_joystick_value(value)
            if v != 0:
                self.send_command(0, 0, v)

    def on_R3_y_at_rest(self):
        self.ptz.stop()

    # Fine Movement Toggle (L1 button press)
    def on_L1_press(self):
        self.fine_movement = True

    def on_L1_release(self):
        self.fine_movement = False



    
class PTZControlSystem:
    """Class to manage the overall PTZ control system."""

    def __init__(self, configs, stream_override=None):
        #with open(config_file, 'r', encoding='utf-8') as f:
         #   configs = yaml.load(f, Loader=yaml.SafeLoader)

        self.ptz = PtzCam(configs['IP'], configs['PORT'], configs['USER'], configs['PASS'])
        self.ptz.CAM_PAN_MAX = configs['CAM_PAN_MAX']
        self.ptz.CAM_PAN_MIN = configs['CAM_PAN_MIN']
        self.ptz.CAM_TILT_MAX = configs['CAM_TILT_MAX']
        self.ptz.CAM_TILT_MIN = configs['CAM_TILT_MIN']
        self.ptz.CAM_ZOOM_MAX = configs['CAM_ZOOM_MAX']
        self.ptz.CAM_ZOOM_MIN = configs['CAM_ZOOM_MIN']
        self.cam_view = CamView(
            ip=configs['IP'],
            user=configs['USER'],
            passwd=configs['PASS'],
            stream=stream_override if stream_override else configs['STREAM'],
            orientation=configs['ORIENTATION'],
            headless=configs['HEADLESS']
        )
        self.controller = PS4Controller(self.ptz, interface='/dev/input/js0', connecting_using_ds4drv=False)

    def start_system(self):
        self.cam_thread = Thread(target=self.cam_view.start_stream)
        self.cam_thread.start()
        print("starting stream")
        self.controller.listen()

    def stop_system(self):
        self.cam_view.stop_stream()
        print("stopped stream")
        self.controller.disable_control()

# Main script
if __name__ == "__main__":
    config_file = "cyclops_config.yaml"
    
    # Initialize system
    ptz_system = PTZControlSystem(config_file)

    # Start streaming and controller
    ptz_system.start_system()
    print("started display and control")
    # Example usage: disable control after 10 seconds
    time.sleep(10)
    print("stopping control")
    ptz_system.controller.disable_control()

    # Stop system after 20 seconds
    time.sleep(10)
    print("stopping system")
    ptz_system.stop_system()

