import tkinter as tk


class RecordingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.configure(bg='black')

        self.vid_count_label = tk.Label(self,
                                        textvariable=controller.vid_count_text,
                                        font=controller.small_font,
                                        fg='blue',
                                        bg='black')
        self.vid_count_label.pack(fill=tk.X)

        self.storage_label = tk.Label(self,
                                      textvariable=controller.storage_text,
                                      font=controller.small_font,
                                      fg='blue',
                                      bg='black')
        self.storage_label.pack(fill=tk.X)

        self.storage_label = tk.Label(self,
                                      textvariable=controller.device_text,
                                      font=controller.small_font,
                                      fg='blue',
                                      bg='black')
        self.storage_label.pack(fill=tk.X)

        self.time_label = tk.Label(self,
                                   textvariable=controller.time_text,
                                   font=controller.small_font,
                                   fg='blue',
                                   bg='black')
        self.time_label.pack(fill=tk.X)

        self.recording_label = tk.Label(self,
                                        textvariable=controller.recording_text,
                                        font=controller.big_font,
                                        fg='blue',
                                        bg='black')
        self.recording_label.pack(fill=tk.X)

        self.error_label = tk.Label(self,
                                    textvariable=controller.error_text,
                                    font=controller.error_font,
                                    fg='red',
                                    bg='black')
        self.error_label.pack(fill=tk.X)


class NetworkPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.configure(bg='black')

        self.ip_label = tk.Label(self,
                                 textvariable=controller.ip_text,
                                 font=controller.small_font,
                                 fg='red',
                                 bg='black')
        self.ip_label.pack(fill=tk.X)
