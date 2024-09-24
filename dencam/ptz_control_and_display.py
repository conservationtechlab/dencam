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
        if not self.headless:
            cv2.namedWindow("Control PTZ Camera", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Control PTZ Camera", cv2.WND_PROP_TOPMOST, 1)
            cv2.setWindowProperty("Control PTZ Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.resizeWindow("Control PTZ Camera", 320, 210)

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
        

class PS4Controller(Controller):
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
        return v / 35000


    
class PTZControlSystem:
    """Class to manage the overall PTZ control system."""

    def __init__(self, configs, stream_override=None):
        #with open(config_file, 'r', encoding='utf-8') as f:
         #   configs = yaml.load(f, Loader=yaml.SafeLoader)

        self.ptz = PtzCam(configs['IP'], configs['PORT'], configs['USER'], configs['PASS'])
        self.cam_view = CamView(
            ip=configs['IP'],
            user=configs['USER'],
            passwd=configs['PASS'],
            stream=stream_override if stream_override else configs['STREAM'],
            orientation=configs['ORIENTATION'],
            headless=configs['HEADLESS']
        )
       # self.controller = PS4Controller(self.ptz, interface='/dev/input/js0', connecting_using_ds4drv=False)

    def start_system(self):
        self.cam_thread = Thread(target=self.cam_view.start_stream)
        self.cam_thread.start()
        #self.controller.listen()

    def stop_system(self):
        self.cam_view.stop_stream()
        print("stopped stream")
        #self.controller.disable_control()

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

