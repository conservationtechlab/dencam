"""Graphical User Interface for DenCam

This module contains the classes associated with the DenCam GUI
displayed on the PiTFT screen that is attached to the Raspberry Pi's
GPIO header.

"""
import logging
import time
import tkinter as tk
import tkinter.font as tkFont
from threading import Thread

from dencam import __version__
from dencam import networking
from dencam import mppt

log = logging.getLogger(__name__)


class BaseController(Thread):
    """DenCam UI controller base class

    """
    def __init__(self, configs, recorder, state_list, state, airplane_mode):
        super().__init__()
        self.recorder = recorder
        self.state = state
        self.state_list = state_list
        self.pause_before_record = configs['PAUSE_BEFORE_RECORD']
        self.airplane_mode = airplane_mode
        self.fonts = {}

    def run(self):
        self._setup()
        self.window.after(100, self._update)
        self.window.mainloop()

    def _setup(self):
        """Set up the Tkinter GUI

        """
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True)
        self.window.title('DenCam Control')

        self._prep_fonts()

        self.vid_count_text = tk.StringVar()
        self.vid_count_text.set('|')
        self.storage_text = tk.StringVar()
        self.storage_text.set('|')
        self.device_text = tk.StringVar()
        self.device_text.set('|')
        self.recording_text = tk.StringVar()
        self.recording_text.set('|')
        self.time_text = tk.StringVar()
        self.time_text.set('|')
        self.error_text = tk.StringVar()
        self.error_text.set(' ')
        self.ip_text = tk.StringVar()
        self.ip_text.set('|')
        self.solar_text = tk.StringVar()
        self.solar_text.set('|')

        container = tk.Frame(self.window, bg='black')
        container.pack(side='top', fill='both', expand=True)
        # container.pack(fill=tk.BOTH, expand=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.configure(bg='black')

        self.frames = {}
        for Page in (RecordingPage, NetworkPage, BlankPage, SolarPage):
            page_name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('NetworkPage')

    def show_frame(self, page_name):
        """Display given page in UI

        Parameters
        ----------
        page_name : str
            Name of page to show

        """
        frame = self.frames[page_name]
        frame.tkraise()

    def _get_time(self):
        """Retrieve current time and format it for screen display

        """
        local_time = time.localtime()

        hours = local_time.tm_hour
        mins = local_time.tm_min
        secs = local_time.tm_sec

        shours = str(hours)
        smins = str(mins)
        ssecs = str(secs)

        if hours < 10:
            shours = '0' + shours
        if mins < 10:
            smins = '0' + smins
        if secs < 10:
            ssecs = '0' + ssecs

        return shours + ':' + smins + ':' + ssecs

    def _update(self):
        """Execute core loop activities

        Runs at 10 Hz (every 100 milliseconds)

        """
        self.elapsed_time = time.time() - self.recorder.record_start_time

        self.recorder.update_timestamp()

        networkp_index = self.state_list.index('NetworkPage')
        blankp_index = self.state_list.index('BlankPage')

        if (self.state.value >= networkp_index
                and self.state.value <= blankp_index):
            self.show_frame(self.state_list[self.state.value])
        self._update_strings()
        self.window.after(100, self._update)

    def _update_strings(self):
        """Update all the strings used in the UI readout

        """
        strg = f"Vids this run: {str(self.recorder.vid_count)}"
        self.vid_count_text.set(strg)

        # prepare storage info text
        free_space = self.recorder.get_free_space()
        storage_string = f"Free: {free_space:.2f} GB"
        log.debug('Storage as seen in main update loop: %s', storage_string)
        self.storage_text.set(storage_string)

        strg = f"To: {self.recorder.video_path}"
        self.device_text.set(strg)

        strg = f"Time: {self._get_time()}"
        self.time_text.set(strg)

        # prepare record state info text
        if not self.recorder.initial_pause_complete:
            remaining = self.pause_before_record - self.elapsed_time
            rec_text = f"{remaining:.0f}"
        else:
            state = 'Recording' if self.recorder.recording else 'Idle'
            rec_text = f"{state}"
        self.recording_text.set(rec_text)

        # prep network text
        network_info = networking.get_network_info()
        airplane_text = "Airplane Mode: "
        if self.airplane_mode.enabled:
            airplane_text += "On"
        else:
            airplane_text += "Off"
        self.ip_text.set(network_info + airplane_text)

        # prep solar text
        solar_info = mppt.get_solardisplay_info()
        self.solar_text.set(solar_info)

    def _prep_fonts(self):
        """Populate the dict of fonts used in UI

        """

        scrn_height = self.window.winfo_screenheight()
        self.fonts['small'] = tkFont.Font(family='Courier New',
                                          size=-int(scrn_height/9))
        self.fonts['smaller'] = tkFont.Font(family='Courier New',
                                            size=-int(scrn_height/12))
        self.fonts['smallerer'] = tkFont.Font(family='Courier New',
                                              size=-int(scrn_height/12),
                                              weight="bold")
        self.fonts['error'] = tkFont.Font(family='Courier New',
                                          size=-int(scrn_height/12))
        self.fonts['big'] = tkFont.Font(family='Courier New',
                                        size=-int(scrn_height/5))
        self.fonts['buttons'] = tkFont.Font(family='Courier New',
                                            size=-int(scrn_height/18))


class Controller(BaseController):
    """DenCam UI Controller

    Extends BaseController to add mechanics for 1) fixing the duration
    of each recording using a value drawn from user configs (and
    re-initializing recording after each duration has elapsed) and b)
    starting first recording after a user-configured wait period.

    """
    def __init__(self, configs, recorder, state_list, state, airplane_mode):
        super().__init__(configs, recorder, state_list, state, airplane_mode)

        self.record_length = configs['RECORD_LENGTH']

    def _update(self):
        super()._update()
        if ((self.elapsed_time > self.pause_before_record
             and not self.recorder.initial_pause_complete)):
            self.recorder.initial_pause_complete = True
            self.recorder.start_recording()
        elif (self.elapsed_time > self.record_length
              and self.recorder.recording):
            self.recorder.stop_recording()
            self.recorder.start_recording()


class State():
    """Class that implements a simple, linear state machine

    The states available to the device are essentially which UI page
    is being displayed and is available for interaction.  This State
    class creates the mechanics for storing the current state and
    incrementing it.  The latter is all that is necessary because the
    interface only allows cycling through each state/page in a fixed
    order and returning to the first state/page once the end is
    reached.

    Parameters
    ----------
    num_states : int
        Total number of states in state machine

    Attributes
    ----------
    value : int
        Index of current state

    Methods
    -------
    goto_next()
        Increment to next state

    """
    def __init__(self, num_states):
        self.value = 0
        self.num_states = num_states

    def goto_next(self):
        """Increment to next state

        """
        self.value += 1
        if self.value >= self.num_states:
            self.value = 0
            
            
class RecordingPage(tk.Frame):
    """UI Page that displays information related to DenCam recording.

    This page displays:
    - number of videos recorded this run
    - path that is currently being recorded to
    - free space remaining on device where currently recording
    - current clock time
    - whether currently recording (countdown if in countdown state)

    On this page, action button toggles recording but actual
    implementation is not in this class.

    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        fonts = controller.fonts

        self.configure(bg='black')
        self.page_label = tk.Label(self, text="Recording Page",
                                   font=fonts['smaller'],
                                   fg='yellow', bg='DodgerBlue4')
        self.page_label.pack(fill=tk.X)

        self.recording_label = tk.Label(self,
                                        textvariable=controller.recording_text,
                                        font=fonts['big'],
                                        fg='yellow',
                                        bg='black')
        self.recording_label.pack(fill=tk.X)

        self.vid_count_label = tk.Label(self,
                                        textvariable=controller.vid_count_text,
                                        font=fonts['smaller'],
                                        fg='yellow',
                                        bg='black')
        self.vid_count_label.place(height=50, x=0, y=140)


        self.device_label = tk.Label(self,
                                     textvariable=controller.device_text,
                                     font=fonts['smaller'],
                                     fg='yellow',
                                     bg='black')
        self.device_label.place(height=50, x=0, y=190)


        self.storage_label = tk.Label(self,
                                      textvariable=controller.storage_text,
                                      font=fonts['smaller'],
                                      fg='yellow',
                                      bg='black')
        self.storage_label.place(height=50, x=0, y=240)


        self.time_label = tk.Label(self,
                                   textvariable=controller.time_text,
                                   font=fonts['smaller'],
                                   fg='yellow',
                                   bg='black',
                                   justify="left")
        self.time_label.place(height=50, x=0, y=290)

        self.error_label = tk.Label(self,
                                    textvariable=controller.error_text,
                                    font=fonts['error'],
                                    fg='red',
                                    bg='black')
        self.error_label.place(height=100,width=280,x=0,y=430)

        self.page_label = tk.Label(self,
                                   text="Next Page",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50,width=145,x=495,y=430)

        self.page_label = tk.Label(self,
                                   text="Toggle Recording",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50, width=260, x=380, y=310)


class NetworkPage(tk.Frame):
    """UI page that displays info related to network connection

    Displays:
    - hostname of device
    - version of firmware (included on this page as first page of UI),
    - whether in airplane mode.

    If connected to a network, also displays:
    - IP address
    - SSID of WiFi AP that device is connected to

    On this page, action button toggles airplane mode on and off.

    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        fonts = controller.fonts

        self.configure(bg='black')
        self.page_label = tk.Label(self,
                                   text="Network Page",
                                   font=fonts['smaller'],
                                   fg='yellow',
                                   bg='midnight blue')
        self.page_label.pack(fill=tk.X)

        self.ip_label = tk.Label(self,
                                 textvariable=controller.ip_text,
                                 font=fonts['smaller'],
                                 fg='yellow',
                                 bg='black',
                                 justify="left")
        self.ip_label.place(x=0,y=50)
        self.version_label = tk.Label(self,
                                      text=("v" + __version__),
                                      font=fonts['smaller'],
                                      fg='yellow',
                                      bg='black')
        self.version_label.place(height=70, x=0, y=430)

        self.page_label = tk.Label(self,
                                   text="Next Page",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50,width=145,x=495,y=430)

        self.page_label = tk.Label(self,
                                   text="Airplane Mode",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50, width=215, x=425, y=310)


class BlankPage(tk.Frame):
    """UI Page that is blank

    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg='black')
        fonts = controller.fonts

        self.page_label = tk.Label(self,
                                   text="Camera Preview",
                                   font=fonts['smaller'],
                                   fg='yellow',
                                   bg='blue4')
        self.page_label.pack(side=tk.TOP, fill=tk.X)
        self.page_label = tk.Label(self,
                                   text="Next Page",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50,width=145,x=495,y=430)

        self.page_label = tk.Label(self,
                                   text="Upper Button>Toggle Inspect",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50, width=440, x=0, y=430)


class SolarPage(tk.Frame):
    """UI Page that displays the solar data from charge controller

    On this page, UI action button refreshes solar data (mechanics of
    the refresh might bear some more detail added here or in a
    docstring associated with place where those mechanics are
    implemented)

    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        fonts = controller.fonts
        self.configure(bg='black')
        self.page_label = tk.Label(self,
                                   text="Solar Page",
                                   font=fonts['smaller'],
                                   fg='yellow',
                                   bg='SlateBlue4')
        self.page_label.pack(fill=tk.X)
        self.solar_label = tk.Label(self,
                                    textvariable=controller.solar_text,
                                    font=fonts['smaller'],
                                    fg='yellow',
                                    bg='black',
                                    justify="left")
        self.solar_label.place(x=0,y=50)

        self.page_label = tk.Label(self,
                                   text="Next Page",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50,width=145,x=495,y=430)

        self.page_label = tk.Label(self,
                                   text="Update Data",
                                   font=fonts['buttons'],
                                   fg='yellow',
                                   bg='black',
                                   highlightthickness=2)
        self.page_label.place(height=50, width=180, x=460, y=310)


class ErrorScreen():
    """Handles display of camera connection error information

    This class is used before core UI controller is even invoked as
    resolving this error supercedes all other functionality.

    """
    def __init__(self):
        self.screen = tk.Tk()
        self.screen.attributes('-fullscreen', True)
        self.screen.configure(background='black')
        label = tk.Label(self.screen,
                         text="Camera error\ncheck wiring to camera",
                         fg="white", bg="black", font=("Helvetica", 28))
        label.pack(expand=True)
        self.screen.update()

    def hide(self):
        """Destroy the error screen

        """
        self.screen.destroy()
