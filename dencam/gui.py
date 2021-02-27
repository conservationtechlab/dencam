import tkinter as tk
import tkinter.font as tkFont


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
