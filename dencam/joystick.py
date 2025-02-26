"""Defines components for camera joystick interface.

For manual aiming of the Mimir system's PTZ network surveillance
camera, this module defines a pair of classes for interfacing with a
joystick to effect that control.  The joystick in question is a PS4
Controller but the decision is to refer to it as the "joystick" since
the term "controller" is pretty overloaded in our code for the DenCam
project what with their being the UI controller etc.

"""
import time
import logging

from ptzipcam.ptz_camera import PtzCam
from pyPS4Controller.controller import Controller

log = logging.getLogger(__name__)

Y_DELTA = .05
X_DELTA = .05
Z_DELTA = .07
X_DELTA_FINE = X_DELTA/3
Y_DELTA_FINE = Y_DELTA/3
Z_DELTA_FINE = Z_DELTA/3

INFINITE_PAN = True
CAM_PAN_MAX = 1.0
CAM_PAN_MIN = -1.0
CAM_TILT_MAX = 1.0
CAM_TILT_MIN = -1.0
CAM_ZOOM_MAX = 1.0
CAM_ZOOM_MIN = 0

CAMERA_DOME_DOWN = True


class PTZController:
    """Metaclass around Joystick class.

    Handles setup of PTZ camera in prep for giving that over to the
    Joystick class.

    """
    def __init__(self, configs):
        self.ptz = PtzCam(configs['CAMERA_IP'],
                          80,
                          configs['CAMERA_USER'],
                          configs['CAMERA_PASS'])
        log.info("Initiating PS4 Controller.")
        self.joystick = Joystick(self.ptz,
                                 interface='/dev/input/js0',
                                 connecting_using_ds4drv=False)

    def run_joystick(self):
        log.info("Initiate listening on PS4 Controller.")
        self.joystick.listen()

    def release_joystick(self):
        self.joystick.stop = True


class Joystick(Controller):
    """Manages PTZ camera control via PS4 controller."""

    def __init__(self, ptz, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ptz = ptz
        self.fine_movement = False
        self.toggle_on = False
        self.yJoystickReleased = False
        self.joystick_ignore = 10000
        self.time = time.time()  # Initialize time tracking for command delays
        self.timeout = 0.25  # Delay between commands
        self.zoom_state = 0.0
        pan, tilt, _ = self.ptz.get_position()
        log.info("Zoom out when Joystick object constructed.")
        self.ptz.absmove_w_zoom(pan,
                                tilt,
                                self.zoom_state)

    def _pan_ratio(self):
        zoom = self.ptz.get_position()[2]
        return 1 / (1 + zoom * 5)

    def send_command(self, x_delta, y_delta, z_delta):
        cmds = {}
        pan, tilt, _ = self.ptz.get_position()
        cmds['pan'] = pan + x_delta
        cmds['tilt'] = tilt + y_delta
        self.zoom_state = self.zoom_state + z_delta
        cmds['zoom'] = self.zoom_state
        log.info("Zoom state: %s", self.zoom_state)
        self.drive_ptz(cmds)
        self.display_status(cmds)

    def display_status(self, cmds):
        """Write the pan, tilt, and zoom stored in cmds to logs."""
        log.info("Pan: %0.2f | Tilt: %0.2f | Zoom: %0.2f",
                 cmds['pan'],
                 cmds['tilt'],
                 cmds['zoom'])

    def scale_joystick_value(self, value):
        """Scale joystick value to be within 0-1 range."""
        return value/35000

    def ready_for_next(self):
        """Check timeout time to send new command."""
        return time.time() - self.time > self.timeout

    # Arrow Buttons - step pan/tilt
    # TODO: scale fine movement by zoom amount
    def on_left_arrow_press(self):
        """Respond to left arrow button press event.

        Callback for a left arrow button press event. Will pan
        camera to the left.

        """
        if self.ready_for_next():
            if CAMERA_DOME_DOWN:
                multiplier = -1
            if self.fine_movement:
                command = multiplier * X_DELTA_FINE * self._pan_ratio()
            else:
                command = multiplier * X_DELTA * self._pan_ratio()

            self.send_command(command, 0, 0)
            self.time = time.time()

    def on_right_arrow_press(self):
        """Respond to right arrow button press event.

        Callback for a right arrow button press event. Will pan
        camera to the right.

        """
        if self.ready_for_next():
            if CAMERA_DOME_DOWN:
                multiplier = -1
            if self.fine_movement:
                command = multiplier * -X_DELTA_FINE * self._pan_ratio()
            else:
                command = multiplier * -X_DELTA * self._pan_ratio()

            self.send_command(command, 0, 0)
            self.time = time.time()

    def on_up_arrow_press(self):
        """Respond to up arrow button press event.

        Callback for an up arrow button press event. Will tilt the camera
        up.

        """
        if self.ready_for_next():
            if CAMERA_DOME_DOWN:
                multiplier = -1
            if self.fine_movement:
                command = multiplier * -Y_DELTA_FINE
            else:
                command = multiplier * -Y_DELTA

            self.send_command(0, command, 0)
            self.time = time.time()

    def on_down_arrow_press(self):
        """Respond to down arrow button press event.

        Callback for a down arrow button press event. Will tilt camera
        down.

        """
        if self.ready_for_next():
            if CAMERA_DOME_DOWN:
                multiplier = -1
            if self.fine_movement:
                command = multiplier * Y_DELTA_FINE
            else:
                command = multiplier * Y_DELTA

            self.send_command(0, command, 0)
            self.time = time.time()

    def on_left_right_arrow_release(self):
        pass

    def on_up_down_arrow_release(self):
        pass

    # Disable Joysticks by making the following callbacks have no
    # effect:
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

    def on_R3_x_at_rest(self):
        pass

    # Fine Movement Toggle
    def on_L1_press(self):
        self.fine_movement = True

    def on_L1_release(self):
        self.fine_movement = False

    # Exposure/Focus Toggle
    def on_R1_press(self):
        self.toggle_on = True

    def on_R1_release(self):
        self.toggle_on = False

    def on_triangle_press(self):
        # zoom in
        if self.ready_for_next():
            if self.toggle_on:
                self.ptz.zoom_in_full()
                self.zoom_state = 1.0
            else:
                self.send_command(0, 0, Z_DELTA)
            self.time = time.time()

    def on_triangle_release(self):
        pass

    def on_square_press(self):
        # self.stop = True
        pass

    def on_square_release(self):
        pass

    def on_circle_press(self):
        pass

    def on_x_press(self):
        # zoom out
        if self.ready_for_next():
            if self.toggle_on:
                self.ptz.zoom_out_full()
                self.zoom_state = 0.0
            else:
                self.send_command(0, 0, -Z_DELTA)
            self.time = time.time()

    def on_x_release(self):
        pass

    def drive_ptz(self, cmds):
        """Prep and send actual pan, tilt, zoom commands to camera."""
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

        self.ptz.absmove_w_zoom(cmds['pan'],
                                cmds['tilt'],
                                cmds['zoom'])
