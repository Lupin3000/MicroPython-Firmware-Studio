from logging import getLogger, debug
from customtkinter import CTkFrame, CTkLabel, CTkButton
from config.application_configuration import FONT_CATEGORY, FRAME_BTN_COLOR_INFORMATION


logger = getLogger(__name__)


class FrameDeviceInformation(CTkFrame):
    """
    A specialized class designed to facilitate device information operations.
    """

    def __init__(self, master, *args, **kwargs):
        """
        A custom frame designed with widgets for erasing flash. This frame
        is a child of the specified parent widget (master) and includes a
        Label and Button with customizable UI features.
        """
        super().__init__(master, *args, **kwargs)
        debug('Create Device Information Frame')

        self.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)

        self.label = CTkLabel(self, text='Information')
        self.label.pack(padx=10, pady=10)
        self.label.configure(font=FONT_CATEGORY)

        self.chip_info_btn = CTkButton(self, text='Chip ID', fg_color=FRAME_BTN_COLOR_INFORMATION)
        self.chip_info_btn.pack(padx=10, pady=5)

        self.memory_info_btn = CTkButton(self, text='Flash ID', fg_color=FRAME_BTN_COLOR_INFORMATION)
        self.memory_info_btn.pack(padx=10, pady=5)

        self.mac_info_btn = CTkButton(self, text='MAC Address', fg_color=FRAME_BTN_COLOR_INFORMATION)
        self.mac_info_btn.pack(padx=10, pady=5)

        self.flash_status_btn = CTkButton(self, text='Flash Status', fg_color=FRAME_BTN_COLOR_INFORMATION)
        self.flash_status_btn.pack(padx=10, pady=5)
