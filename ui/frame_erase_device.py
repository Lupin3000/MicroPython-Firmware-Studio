from logging import getLogger, debug
from customtkinter import CTkFrame, CTkLabel, CTkButton
from config.application_configuration import FONT_CATEGORY


logger = getLogger(__name__)


class FrameEraseDevice(CTkFrame):
    """
    A specialized class designed to facilitate flash erasing operations.
    """

    def __init__(self, master, *args, **kwargs):
        """
        A custom frame designed with widgets for erasing flash. This frame
        is a child of the specified parent widget (master) and includes a
        Label and a Button with customizable UI features.
        """
        super().__init__(master, *args, **kwargs)
        debug('Create Erase Device Frame')

        self.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)

        self.label = CTkLabel(self, text='Erase')
        self.label.pack(padx=10, pady=10)
        self.label.configure(font=FONT_CATEGORY)

        self.erase_btn = CTkButton(self, text='Erase Flash', fg_color='red')
        self.erase_btn.pack(padx=10, pady=5)
