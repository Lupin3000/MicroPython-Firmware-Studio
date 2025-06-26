from logging import getLogger, debug
from customtkinter import CTkFrame, CTkLabel, CTkSwitch, CTkOptionMenu, CTkCheckBox, CTkButton, CTkEntry
from tkinter import Canvas
from config.application_configuration import FONT_CATEGORY, FONT_DESCRIPTION, LINK_OBJECT
from config.device_configuration import (CONFIGURED_DEVICES, BAUDRATE_OPTIONS, FLASH_MODE_OPTIONS,
                                         FLASH_FREQUENCY_OPTIONS, FLASH_SIZE_OPTIONS)


logger = getLogger(__name__)


class FrameFirmwareFlash(CTkFrame):
    """
    A specialized class designed to facilitate firmware flashing operations.
    """

    def __init__(self, master, *args, **kwargs):
        """
        A custom frame designed with widgets for erasing flash. This frame
        is a child of the specified parent widget (master) and includes a
        Label, switch, OptionMenu, CheckBox, Button and Entry with
        customizable UI features.
        """
        super().__init__(master, *args, **kwargs)
        debug('Create Firmware Flash Frame')

        self.grid(row=1, column=1, rowspan=3, padx=10, pady=5, sticky="nsew")
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=0)
        self.grid_columnconfigure(5, weight=1)

        self.label = CTkLabel(self, text='Flash Configuration')
        self.label.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="w")
        self.label.configure(font=FONT_CATEGORY)

        self.expert_mode = CTkSwitch(self, text='Expert Mode')
        self.expert_mode.grid(row=0, column=5, padx=10, pady=5, sticky="e")

        self.chip_label = CTkLabel(self, text='Step 1:')
        self.chip_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        chip_options = ["Select Chip"] + list(CONFIGURED_DEVICES.keys())
        self.chip_option = CTkOptionMenu(self, values=chip_options, width=150)
        self.chip_option.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.chip_option.set("Select Chip")

        self.chip_checkbox = CTkCheckBox(self, text='', state='disabled', width=20)
        self.chip_checkbox.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.chip_info = CTkLabel(self, text='Choose the chip type to flash')
        self.chip_info.grid(row=1, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self.chip_info.configure(font=FONT_DESCRIPTION)

        self.firmware_label = CTkLabel(self, text='Step 2:')
        self.firmware_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.firmware_btn = CTkButton(self, text='Select Firmware', width=150)
        self.firmware_btn.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.firmware_checkbox = CTkCheckBox(self, text='', state='disabled', width=20)
        self.firmware_checkbox.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        self.link_label = CTkLabel(self, text='Browse', text_color=LINK_OBJECT, cursor="hand2")
        self.link_label.grid(row=2, column=3, padx=(10, 0), pady=5, sticky="w")
        self.link_label.configure(font=(*FONT_DESCRIPTION, "underline"))

        self.firmware_info = CTkLabel(self, text='and select the firmware file to upload')
        self.firmware_info.grid(row=2, column=4, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        self.firmware_info.configure(font=FONT_DESCRIPTION)

        self.baudrate_label = CTkLabel(self, text='Step 3:')
        self.baudrate_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.baudrate_option = CTkOptionMenu(self, values=BAUDRATE_OPTIONS, width=150)
        self.baudrate_option.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.baudrate_checkbox = CTkCheckBox(self, text='', state='disabled', width=20)
        self.baudrate_checkbox.grid(row=3, column=2, padx=10, pady=5, sticky="w")

        self.baudrate_info = CTkLabel(self, text='Choose a communication speed')
        self.baudrate_info.grid(row=3, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self.baudrate_info.configure(font=FONT_DESCRIPTION)

        self.sector_label = CTkLabel(self, text='Step 4:')
        self.sector_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.sector_input = CTkEntry(self, width=150)
        self.sector_input.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self.sector_checkbox = CTkCheckBox(self, text='', state='disabled', width=20)
        self.sector_checkbox.grid(row=4, column=2, padx=10, pady=5, sticky="w")

        self.sector_info = CTkLabel(self, text='Set the starting address for firmware')
        self.sector_info.grid(row=4, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self.sector_info.configure(font=FONT_DESCRIPTION)

        self.flash_mode_label = CTkLabel(self, text='Step 5:')
        self.flash_mode_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.flash_mode_option = CTkOptionMenu(self, values=FLASH_MODE_OPTIONS, width=150)
        self.flash_mode_option.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        self.flash_mode_option.set("keep")

        self.flash_mode_info = CTkLabel(self, text='Choose the data transfer mode for flashing')
        self.flash_mode_info.grid(row=5, column=3, columnspan=3, padx=10, pady=5, sticky="w")

        self.flash_frequency_label = CTkLabel(self, text='Step 6:')
        self.flash_frequency_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")

        self.flash_frequency_option = CTkOptionMenu(self, values=FLASH_FREQUENCY_OPTIONS, width=150)
        self.flash_frequency_option.grid(row=6, column=1, padx=10, pady=5, sticky="w")
        self.flash_frequency_option.set("keep")

        self.flash_frequency_info = CTkLabel(self, text='Set the clock speed during flash operations')
        self.flash_frequency_info.grid(row=6, column=3, columnspan=3, padx=10, pady=5, sticky="w")

        self.flash_size_label = CTkLabel(self, text='Step 7:')
        self.flash_size_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        self.flash_size_option = CTkOptionMenu(self, values=FLASH_SIZE_OPTIONS, width=150)
        self.flash_size_option.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        self.flash_size_option.set("detect")

        self.flash_size_info = CTkLabel(self, text='Specify or detect the flash memory size')
        self.flash_size_info.grid(row=7, column=3, columnspan=3, padx=10, pady=5, sticky="w")

        self.erase_before_label = CTkLabel(self, text='Step 8:')
        self.erase_before_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

        self.erase_before_switch = CTkSwitch(self, text='')
        self.erase_before_switch.grid(row=8, column=1, padx=10, pady=5, sticky="w")

        self.erase_before_info = CTkLabel(self, text='Erase flash before flashing firmware')
        self.erase_before_info.grid(row=8, column=3, columnspan=3, padx=10, pady=5, sticky="w")

        self.separator_canvas = Canvas(self, height=1, highlightthickness=0, bg="white", bd=0)
        self.separator_canvas.grid(row=9, columnspan=6, sticky="ew", padx=10, pady=10)

        self.flash_btn = CTkButton(self, text='Flash Firmware')
        self.flash_btn.grid(row=10, column=1, columnspan=5, padx=10, pady=5, sticky="w")
