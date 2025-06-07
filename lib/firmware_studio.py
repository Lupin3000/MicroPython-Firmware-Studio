from glob import glob
from logging import getLogger, debug, error
from os.path import expanduser
from subprocess import run, CalledProcessError
from tkinter import filedialog, Canvas, Event
from typing import Optional, List
from PIL import Image
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkTextbox, CTkEntry, CTkCheckBox, CTkImage, CTkOptionMenu
from config.config import CONFIGURED_DEVICES


logger = getLogger(__name__)


class MicroPythonFirmwareStudio(CTk):
    """
    A class representing the MicroPython Firmware Studio GUI.

    :ivar _WINDOW_TITLE: The title of the dialog window.
    :type _WINDOW_TITLE: str
    :ivar _FONT_PATH: The font style for the path labels.
    :type _FONT_PATH: tuple
    :ivar _FONT_CATEGORY: The font style for the category labels.
    :type _FONT_CATEGORY: tuple
    :ivar _FONT_DESCRIPTION: The font style for the description labels.
    :type _FONT_DESCRIPTION: tuple
    :ivar _DEVICE_SEARCH_PATH: The default search path for device serial ports.
    :type _DEVICE_SEARCH_PATH: str
    :ivar _FIRMWARE_SEARCH_PATH: The default search path for firmware files.
    :type _FIRMWARE_SEARCH_PATH: str
    :ivar _BAUDRATE_OPTIONS: The list of available baud rate options.
    :type _BAUDRATE_OPTIONS: list
    """
    _WINDOW_TITLE: str = 'MicroPython Firmware Studio'
    _FONT_PATH: tuple = ('Arial', 20, 'bold')
    _FONT_CATEGORY: tuple = ('Arial', 16, 'bold')
    _FONT_DESCRIPTION: tuple = ('Arial', 14)
    _DEVICE_SEARCH_PATH: str = '/dev/cu.usb*'
    _FIRMWARE_SEARCH_PATH: str = '~/Downloads'
    _BAUDRATE_OPTIONS: list = ["9600", "57600", "74880", "115200", "23400", "460800", "921600", "1500000"]

    def __init__(self):
        """
        A GUI class to manage ESP device configuration and firmware flashing.
        """
        super().__init__()

        self.title(self._WINDOW_TITLE)
        self.resizable(False, False)

        # Variables
        self.__device_path: Optional[str] = None
        self.__selected_chip: Optional[str] = None
        self.__selected_baudrate: Optional[int] = 460800
        self.__selected_firmware: Optional[str] = None

        # Main Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Top Frame
        self._top_frame = CTkFrame(self)
        self._top_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self._device_path_label = CTkLabel(self._top_frame, text="Device Path:")
        self._device_path_label.pack(side="left", padx=10, pady=10)
        self._device_path_label.configure(font=self._FONT_PATH)

        reload_img = CTkImage(light_image=Image.open('img/reload.png'))
        self._refresh = CTkButton(self._top_frame, image=reload_img, text='', width=30, command=self._search_devices)
        self._refresh.pack(side="right", padx=10, pady=10)

        self._device_dropdown = CTkOptionMenu(self._top_frame, width=150, command=self._set_device)
        self._device_dropdown.pack(side="right", padx=10, pady=10)

        # Left Top Frame
        self._left_top_frame = CTkFrame(self)
        self._left_top_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self._left_top_frame.grid_columnconfigure(0, weight=1)

        self._left_label = CTkLabel(self._left_top_frame, text='Information')
        self._left_label.pack(padx=10, pady=10)
        self._left_label.configure(font=self._FONT_CATEGORY)

        self._chip_info_btn = CTkButton(self._left_top_frame, text='Chip_ID', command=self._get_chip_id)
        self._chip_info_btn.pack(padx=10, pady=5)

        self._memory_info_btn = CTkButton(self._left_top_frame, text='Flash_ID', command=self._get_flash_id)
        self._memory_info_btn.pack(padx=10, pady=5)

        # Left Bottom Frame
        self._left_bottom_frame = CTkFrame(self)
        self._left_bottom_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self._left_bottom_frame.grid_columnconfigure(0, weight=1)

        self._left_bottom_label = CTkLabel(self._left_bottom_frame, text='Erase Flash')
        self._left_bottom_label.pack(padx=10, pady=10)
        self._left_bottom_label.configure(font=self._FONT_CATEGORY)

        self._erase_btn = CTkButton(self._left_bottom_frame, text='Erase Flash', command=self._erase_flash)
        self._erase_btn.pack(padx=10, pady=5)

        # Right Frame
        self._right_frame = CTkFrame(self)
        self._right_frame.grid(row=1, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")
        self._right_frame.grid_columnconfigure(0, weight=0)
        self._right_frame.grid_columnconfigure(1, weight=0)

        self._right_label = CTkLabel(self._right_frame, text='Flash Configuration')
        self._right_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        self._right_label.configure(font=self._FONT_CATEGORY)

        # Right Frame (chip select)
        self._chip_label = CTkLabel(self._right_frame, text='Step 1:')
        self._chip_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        chip_options = ["Select Chip"] + list(CONFIGURED_DEVICES.keys())
        self._chip_option = CTkOptionMenu(self._right_frame, values=chip_options, width=150)
        self._chip_option.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self._chip_option.set("Select Chip")
        self._chip_option.configure(command=self._set_chip)

        self._chip_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled')
        self._chip_checkbox.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self._chip_info = CTkLabel(self._right_frame, text='Choose the chip type to flash')
        self._chip_info.grid(row=1, column=3, padx=10, pady=5, sticky="w")
        self._chip_option.configure(font=self._FONT_DESCRIPTION)

        # Right Frame (firmware select)
        self._firmware_label = CTkLabel(self._right_frame, text='Step 2:')
        self._firmware_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self._firmware_btn = CTkButton(self._right_frame, text='Select Firmware', width=150)
        self._firmware_btn.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self._firmware_btn.configure(command=self._set_firmware)

        self._firmware_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled')
        self._firmware_checkbox.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        self._firmware_info = CTkLabel(self._right_frame, text='Browse and select the firmware file to upload')
        self._firmware_info.grid(row=2, column=3, padx=10, pady=5, sticky="w")
        self._firmware_btn.configure(font=self._FONT_DESCRIPTION)

        # Right Frame (baudrate select)
        self._baudrate_label = CTkLabel(self._right_frame, text='Step 3:')
        self._baudrate_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self._baudrate_dropdown = CTkOptionMenu(self._right_frame, values=self._BAUDRATE_OPTIONS, width=150)
        self._baudrate_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self._baudrate_dropdown.set("460800")
        self._baudrate_dropdown.configure(command=self._set_baudrate)

        self._baudrate_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled')
        self._baudrate_checkbox.grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self._baudrate_checkbox.select()

        self._baudrate_info = CTkLabel(self._right_frame, text='Choose a communication speed')
        self._baudrate_info.grid(row=3, column=3, padx=10, pady=5, sticky="w")
        self._baudrate_dropdown.configure(font=self._FONT_DESCRIPTION)

        # Right Frame (sector select)
        self._sector_label = CTkLabel(self._right_frame, text='Step 4:')
        self._sector_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self._sector_input = CTkEntry(self._right_frame, width=150)
        self._sector_input.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self._sector_input.bind("<KeyRelease>", self._on_sector_input_change)

        self._sector_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled')
        self._sector_checkbox.grid(row=4, column=2, padx=10, pady=5, sticky="w")

        self._sector_info = CTkLabel(self._right_frame, text='Set the starting address for firmware')
        self._sector_info.grid(row=4, column=3, padx=10, pady=5, sticky="w")
        self._sector_input.configure(font=self._FONT_DESCRIPTION)

        # Right Frame (seperator)
        self._separator_canvas = Canvas(self._right_frame, height=1, highlightthickness=0, bg="white", bd=0)
        self._separator_canvas.grid(row=5, columnspan=4, sticky="ew", padx=10, pady=10)

        # Right Frame (start firmware flash)
        self._flash_btn = CTkButton(self._right_frame, text='Flash Firmware', command=self._flash_firmware)
        self._flash_btn.grid(row=6, columnspan=4, padx=10, pady=5, sticky="w")

        # Bottom Frame
        self._bottom_frame = CTkFrame(self)
        self._bottom_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        self._bottom_frame.grid_columnconfigure(0, weight=1)

        self._bottom_label = CTkLabel(self._bottom_frame, text='Console Output')
        self._bottom_label.pack(padx=10, pady=10)
        self._bottom_label.configure(font=self._FONT_CATEGORY)

        self._console_text = CTkTextbox(self._bottom_frame, width=800, height=300)
        self._console_text.pack(padx=10, pady=10, fill="both", expand=True)
        self._console_text.bind("<Key>", lambda e: "break")

        # search for devices on the start
        self._search_devices()

    def _search_devices(self) -> None:
        """
        Updates the device dropdown menu with a list of available devices. If there are no
        connected devices, sets "No devices found" as the only dropdown value.

        :return: None
        """
        current_selection = self._device_dropdown.get()
        devices = glob(self._DEVICE_SEARCH_PATH)

        if not devices:
            devices = ["No devices found"]
        else:
            devices.insert(0, "Select Device")

        debug(f"Devices: {devices}")
        self._device_dropdown.configure(values=devices)

        if current_selection in devices:
            self._device_dropdown.set(current_selection)
        else:
            self._device_dropdown.set(devices[0])
            self._set_device(None)

    def _delete_console(self) -> None:
        """
        Deletes all the content from the console text box.

        :return: None
        """
        self._console_text.delete("1.0", "end")

    def _execute_command(self, command: List[str]) -> None:
        """
        Executes a system command by running it as a subprocess and captures its output.

        :param command: The command to execute is represented as a list of strings.
        :type command: List[str]
        :return: None
        """
        try:
            result = run(command, capture_output=True, text=True, check=True)
            self._console_text.insert("end", result.stdout)
        except CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            self._console_text.insert("end", f'[ERROR]: {error_msg}')

    def _set_device(self, selected_device: Optional[str]) -> None:
        """
        Handles the selection of a device using a device selection dialog, updates the
        device path, and modifies the configuration label to display the new device path.

        :param selected_device: The selected device path as a string.
        :type selected_device: Optional[str]
        :return: None
        """
        debug(f"Selected device: {selected_device}")

        if selected_device and selected_device not in ("Select Device", "No devices found"):
            debug(f"Selected device: {selected_device}")
            self.__device_path = selected_device
            self._device_path_label.configure(text=f"Device Path: {self.__device_path}")
        else:
            self.__device_path = None
            self._device_path_label.configure(text="Device Path:")

    def _set_chip(self, selection: str) -> None:
        """
        Sets the chip configuration based on the provided selection.

        :param selection: The selected chip name as a string.
        :type selection: str
        :return: None
        """
        debug(f"Selected chip: {selection}")

        if selection != "Select Chip":
            self.__selected_chip = CONFIGURED_DEVICES[selection]["name"]
            self._sector_input.delete(0, "end")
            self._sector_input.insert(0, hex(CONFIGURED_DEVICES[selection]["write_flash"]))
            self._chip_checkbox.select()
            self._baudrate_checkbox.select()
            self._sector_checkbox.select()
        else:
            self.__selected_chip = None
            self._sector_input.delete(0, "end")
            self._chip_checkbox.deselect()

    def _set_baudrate(self, selection: str) -> None:
        """
        Sets the baud rate based on the user selection if it is a valid option.

        :param selection: The baud rate option as a string that the user has selected.
        :type selection: str
        :return: None
        """
        debug(f"Selected baudrate: {selection}")

        if selection and selection in self._BAUDRATE_OPTIONS:
            self.__selected_baudrate = int(selection)
            self._baudrate_checkbox.select()
        else:
            self.__selected_baudrate = None
            self._baudrate_checkbox.deselect()

    def _on_sector_input_change(self, event: Optional[Event] = None) -> None:
        """
        Handles changes to the sector input field and updates the sector checkbox
        state accordingly.

        :param event: An optional event object representing a UI change.
        :return: None
        """
        _ = event

        try:
            int(self._sector_input.get().strip(), 0)
            self._sector_checkbox.select()
        except ValueError:
            self._sector_checkbox.deselect()

    def _set_firmware(self) -> None:
        """
        Handles selection and association of a firmware file in the user interface.

        :return: None
        """
        default_dir = expanduser(self._FIRMWARE_SEARCH_PATH)

        file_path = filedialog.askopenfilename(
            initialdir=default_dir,
            title="Select Firmware File",
            filetypes=(("Binary files", "*.bin"), ("All files", "*.*"))
        )

        debug(f"Selected firmware: {file_path}")

        if file_path:
            self.__selected_firmware = file_path
            self._firmware_checkbox.select()
        else:
            self.__selected_firmware = None
            self._firmware_checkbox.deselect()

    def _get_chip_id(self) -> None:
        """
        Retrieves the chip id identification for the connected device.

        :return: None
        """
        self._run_esptool_command("chip_id")

    def _get_flash_id(self) -> None:
        """
        Retrieves the flash memory identification for the connected device.

        :return: None
        """
        self._run_esptool_command("flash_id")

    def _erase_flash(self) -> None:
        """
        Erases the flash memory of the connected device.

        :return: None
        """
        self._run_esptool_command("erase_flash")

    def _run_esptool_command(self, command_name: str) -> None:
        """
        Executes an esptool command using the specified `command_name`.

        :param command_name: The name of the esptool command to execute ("chip_id", "flash_id", "erase_flash").
        :type command_name: str
        :return: None
        """
        debug(f"Running esptool command: {command_name}")
        self._delete_console()

        allowed_commands = {"chip_id", "flash_id", "erase_flash"}
        if command_name not in allowed_commands:
            self._console_text.insert("end", f'[ERROR] Invalid command: {command_name}\n')
            error(f"Invalid command: {command_name}")
            return

        if not self.__device_path:
            self._console_text.insert("end", "[ERROR] No device selected!\n")
            error("No device selected!")
            return

        chip = self.__selected_chip if self.__selected_chip else "auto"
        cmd = ["python", "-m", "esptool",
               "-c", chip,
               "-p",
               self.__device_path,
               command_name]

        self._console_text.insert("end", f'[INFO] {" ".join(cmd)}\n\n')
        self._execute_command(command=cmd)

    def _flash_firmware(self) -> None:
        """
        Internal method to flash firmware to the connected device.

        :return: None
        """
        self._delete_console()

        errors = []
        if not self.__device_path:
            errors.append("No device path selected")
            error('No device path selected.')

        if not self.__selected_chip:
            errors.append("No chip selected")
            error('No chip selected.')

        if not self.__selected_firmware:
            errors.append("No firmware selected")
            error('No firmware selected.')

        if not self.__selected_baudrate:
            errors.append("No baudrate selected")
            error('No baudrate selected.')

        if not self._sector_input.get().strip():
            errors.append("No sector value provided")
            error('No sector value provided.')

        if errors:
            self._console_text.insert("end", f'[ERROR] {", ".join(errors)}\n')
            return

        cmd = ["python", "-m", "esptool",
               '-p', self.__device_path,
               '-c', self.__selected_chip,
               '-b', str(self.__selected_baudrate),
               'write_flash', self._sector_input.get().strip(),
               self.__selected_firmware]

        self._console_text.insert("end", f'[INFO] {" ".join(cmd)}\n\n')
        self._execute_command(command=cmd)

    def destroy(self) -> None:
        """
        Terminates the execution of the current process or application by invoking
        the quit method associated with the instance.

        :return: None
        """
        self.quit()
