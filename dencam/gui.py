import logging
import time
import tkinter as tk
import tkinter.font as tkFont
from threading import Thread

from dencam import networking

log = logging.getLogger(__name__)


class BaseController(Thread):
    def __init__(self, configs, recorder, state):
        super().__init__()
        self.recorder = recorder
        self.state = state

        self.PAUSE_BEFORE_RECORD = configs['PAUSE_BEFORE_RECORD']

    def run(self):
        self._setup()
        self.window.after(100, self._update)
        self.window.mainloop()

    def _setup(self):
        # GUI setup
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True)
        self.window.title('DenCam Control')

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

        container = tk.Frame(self.window, bg='black')
        container.pack(side='top', fill='both', expand=True)
        # container.pack(fill=tk.BOTH, expand=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.configure(bg='black')

        self.frames = {}

        for Page in (RecordingPage, NetworkPage, BlankPage):
            page_name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('RecordingPage')

    def show_frame(self, page_name):
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
        """Core loop method run at 10 Hz

        """
        self.elapsed_time = time.time() - self.recorder.record_start_time

        self.recorder.update_timestamp()

        if self.state.value <= 1:
            self.show_frame('NetworkPage')
        elif self.state.value == 2:
            self.show_frame('RecordingPage')
        elif self.state.value == 3:
            self.show_frame('BlankPage')

        self._update_strings()
        self.window.after(100, self._update)

    def _update_strings(self):
        """Draw the readout for the user to the screen.

        """
        strg = "Vids this run: " + str(self.recorder.vid_count)
        self.vid_count_text.set(strg)

        # prepare storage info text
        free_space = self.recorder.get_free_space()
        storage_string = 'Free: ' + '{0:.2f}'.format(free_space) + ' GB'
        log.debug('Storage as seen in main update loop: ' + storage_string)
        self.storage_text.set(storage_string)

        strg = 'To: {}'.format(self.recorder.video_path)
        self.device_text.set(strg)

        strg = 'Time: ' + self._get_time()
        self.time_text.set(strg)

        # prepare record state info text
        if not self.recorder.initial_pause_complete:
            remaining = self.PAUSE_BEFORE_RECORD - self.elapsed_time
            rec_text = '{0:.0f}'.format(remaining)
        else:
            state = 'Recording' if self.recorder.recording else 'Idle'
            rec_text = '{}'.format(state)
        self.recording_text.set(rec_text)

        # prep network text
        network_info = networking.get_network_info()
        self.ip_text.set(network_info)


class Controller(BaseController):
    def __init__(self, configs, recorder, state):
        super().__init__(configs, recorder, state)

        self.RECORD_LENGTH = configs['RECORD_LENGTH']

    def _update(self):
        super()._update()
        
        if ((self.elapsed_time > self.PAUSE_BEFORE_RECORD
             and not self.recorder.initial_pause_complete)):
            self.recorder.initial_pause_complete = True
            self.recorder.start_recording()
        elif (self.elapsed_time > self.RECORD_LENGTH
              and self.recorder.recording):
            self.recorder.stop_recording()
            self.recorder.start_recording()


class State():
    def __init__(self, num_states):
        self.value = 0
        self.num_states = num_states

    def goto_next(self):
        self.value += 1
        if self.value >= self.num_states:
            self.value = 0


def prep_fonts(controller):
    # set font sizes
    fonts = {}

    scrn_height = controller.window.winfo_screenheight()
    fonts['small'] = tkFont.Font(family='Courier New',
                                 size=-int(scrn_height/9))
    fonts['smaller'] = tkFont.Font(family='Courier New',
                                   size=-int(scrn_height/12))
    fonts['error'] = tkFont.Font(family='Courier New',
                                 size=-int(scrn_height/12))
    fonts['big'] = tkFont.Font(family='Courier New',
                               size=-int(scrn_height/5))

    return fonts


class RecordingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        fonts = prep_fonts(controller)

        self.configure(bg='black')

        self.vid_count_label = tk.Label(self,
                                        textvariable=controller.vid_count_text,
                                        font=fonts['small'],
                                        fg='blue',
                                        bg='black')
        self.vid_count_label.pack(fill=tk.X)

        self.device_label = tk.Label(self,
                                     textvariable=controller.device_text,
                                     font=fonts['smaller'],
                                     fg='blue',
                                     bg='black')
        self.device_label.pack(fill=tk.X)

        self.storage_label = tk.Label(self,
                                      textvariable=controller.storage_text,
                                      font=fonts['small'],
                                      fg='blue',
                                      bg='black')
        self.storage_label.pack(fill=tk.X)

        self.time_label = tk.Label(self,
                                   textvariable=controller.time_text,
                                   font=fonts['small'],
                                   fg='blue',
                                   bg='black')
        self.time_label.pack(fill=tk.X)

        self.recording_label = tk.Label(self,
                                        textvariable=controller.recording_text,
                                        font=fonts['big'],
                                        fg='blue',
                                        bg='black')
        self.recording_label.pack(fill=tk.X)

        self.error_label = tk.Label(self,
                                    textvariable=controller.error_text,
                                    font=fonts['error'],
                                    fg='red',
                                    bg='black')
        self.error_label.pack(fill=tk.X)


class NetworkPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        fonts = prep_fonts(controller)

        self.configure(bg='black')

        self.ip_label = tk.Label(self,
                                 textvariable=controller.ip_text,
                                 font=fonts['smaller'],
                                 fg='red',
                                 bg='black')
        self.ip_label.pack(fill=tk.X)


class BlankPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.configure(bg='black')
