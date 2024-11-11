from ptzipcam.ptz_camera import PtzCam
from pyPS4Controller.controller import Controller


class PS4Controller(Controller):
    """Class to manage PTZ control via PS4 controller."""
    
    def __init__(self, ptz, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ptz = ptz
        self.fine_movement = False
        self.toggleOn = False
        self.focusMode = False
        self.yJoystickReleased = False
        self.joystick_ignore = 10000
        self.t = time.time()  # Initialize time tracking for command delays
        self.timeout = 0.25  # Delay between commands
        self.Y_DELTA = .05
        self.X_DELTA = .05
        self.Z_DELTA = .07
        self.X_DELTA_FINE = self.X_DELTA/3
        self.Y_DELTA_FINE = self.Y_DELTA/3
        self.Z_DELTA_FINE = self.Z_DELTA/3

        pin = 27
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

    def send_command(self, x_delta, y_delta, z_delta):
        cmds = {}
        pan, tilt, zoom = self.ptz.get_position()
        cmds['pan'] = pan + x_delta
        cmds['tilt'] = tilt + y_delta
        cmds['zoom'] = zoom + z_delta
        self.drive_ptz(cmds)
        return cmds

    def display_status(self, cmds):
        log.info(f'Pan: {cmds["pan"]} | Tilt: {cmds["tilt"]} | Zoom: {cmds["zoom"]}')

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
            if self.fine_movement:
                commands = self.send_command(self.X_DELTA_FINE, 0 , 0)
            else:
                commands = self.send_command(self.X_DELTA, 0, 0)
            self.t = time.time()

    def on_right_arrow_press(self):
        if self.ready_for_next():
            if self.fine_movement:
                commands = self.send_command(-self.X_DELTA_FINE, 0, 0)
            else:
                commands = self.send_command(-self.X_DELTA, 0, 0)
            self.t = time.time()

    def on_up_arrow_press(self):
        if self.ready_for_next():
            if self.fine_movement:
                commands = self.send_command(0, -self.Y_DELTA_FINE, 0)
            else:
                commands = self.send_command(0, -self.Y_DELTA, 0)
            self.t = time.time()

    def on_down_arrow_press(self):
        if self.ready_for_next():
            if self.fine_movement:
                commands = self.send_command(0, self.Y_DELTA_FINE, 0)
                self.t = time.time()
            else:
                commands = self.send_command(0, self.Y_DELTA, 0)
                self.t = time.time()

    def on_left_right_arrow_release(self):
        pass
    def on_up_down_arrow_release(self):
        pass

    # Disable Joysticks
    def on_L3_up(self, value):
        pass

    def on_L3_down(self, value):
        pass

    def on_L3_right(self, value):
        pass

    def on_L3_left(self, value):
        pass

    def on_L3_x_at_rest(self):
        pass

    def on_L3_y_at_rest(self):
        pass

    def on_R3_up(self, value):
        pass

    def on_R3_down(self, value):
        pass

    def on_R3_right(self, value):
        pass

    def on_R3_left(self, value):
        pass

    def on_R3_y_at_rest(self):
        pass

    # Fine Movement Toggle
    def on_L1_press(self):
        self.fine_movement = True

    def on_L1_release(self):
        self.fine_movement = False

    # Exposure/Focus Toggle
    def on_R1_press(self):
        self.toggleOn = True

    def on_R1_release(self):
        self.toggleOn = False

    def on_triangle_press(self):
        # zoom in
        if self.ready_for_next():
            if self.toggleOn:
                ptz.zoom_in_full()
            else:
                commands = self.send_command(0, 0, self.Z_DELTA)
            self.t = time.time()

    def on_triangle_release(self):
        pass

    def on_square_press(self):
        self.stop = True

    def on_square_release(self):
        pass

    def on_circle_press(self):
        pass

    def on_circle_press(self):
        pass

    def on_x_press(self):
        # zoom out
        if self.ready_for_next():
            if self.toggleOn:
                ptz.zoom_out_full()
            else:
                commands = self.send_command(0, 0, -self.Z_DELTA)
            self.t = time.time()

    def on_x_release(self):
        pass


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

    def check_button_press(self):
        current_state = GPIO.input(27)
        current_time = time.time()

        if current_state == GPIO.LOW and self.last_button_state == GPIO.HIGH and (current_time - self.last_press_time) >0.2:
            self.last_press_time = current_time
            self.last_button_state = current_state
            return True

        self.last_button_state = current_state
        return False
