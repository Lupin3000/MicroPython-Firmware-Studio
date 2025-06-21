from glob import glob
from serial.tools import list_ports
from logging import getLogger, debug, info, error
from os.path import expanduser
from subprocess import Popen, PIPE
from tkinter import filedialog, Canvas, Event
from webbrowser import open_new
from typing import Optional, List
from PIL import Image
from threading import Thread
from queue import Queue, Empty
from customtkinter import CTkLabel, CTkButton, CTkTextbox, CTkEntry, CTkCheckBox, CTkImage, CTkOptionMenu, CTkSwitch
from lib.base_ui import BaseUI
from config.device_configuration import DEFAULT_URL, CONFIGURED_DEVICES
from config.application_configuration import (FONT_PATH, FONT_CATEGORY, FONT_DESCRIPTION, RELOAD_ICON, CONSOLE_INFO,
                                              CONSOLE_COMMAND, CONSOLE_ERROR, LINK_OBJECT)
from lib.serial_get_micropython_version import MicroPythonVersion
from lib.serial_get_file_structure import MicroPythonFileStructure


logger = getLogger(__name__)


class MicroPythonFirmwareStudio(BaseUI):
    """
    A class representing the MicroPython Firmware Studio GUI.

    :ivar _BAUDRATE_OPTIONS: The list of available baud rate options.
    :type _BAUDRATE_OPTIONS: list
    :ivar _FLASH_MODE_OPTIONS: The list of available flash mode options.
    :type _FLASH_MODE_OPTIONS: list
    :ivar _FLASH_FREQUENCY_OPTIONS: The list of available flash frequency options.
    :type _FLASH_FREQUENCY_OPTIONS: list
    :ivar _FLASH_SIZE_OPTIONS: The list of available flash size options.
    :type _FLASH_SIZE_OPTIONS: list
    """
    _BAUDRATE_OPTIONS: list = ["9600", "57600", "74880", "115200", "23400", "460800", "921600", "1500000"]
    _FLASH_MODE_OPTIONS: list = ["keep", "qio", "qout", "dio", "dout"]
    _FLASH_FREQUENCY_OPTIONS: list = ["keep", "40m", "26m", "20m", "80m"]
    _FLASH_SIZE_OPTIONS: list = ["keep", "detect", "1MB", "2MB", "4MB", "8MB", "16MB"]

    def __init__(self):
        """
        A GUI class to manage ESP device configuration and firmware flashing.
        """
        super().__init__()

        # Variables and objects
        self._console_queue: Queue = Queue()
        self.__device_path: Optional[str] = None
        self.__selected_chip: Optional[str] = None
        self.__selected_baudrate: Optional[int] = 460800
        self.__selected_firmware: Optional[str] = None
        self.__url: str = DEFAULT_URL
        self.__expert_mode: bool = False

        # Top Frame
        self._device_path_label = CTkLabel(self._top_frame, text='Device Path:')
        self._device_path_label.pack(side="left", padx=10, pady=10)
        self._device_path_label.configure(font=FONT_PATH)

        reload_img = CTkImage(light_image=Image.open(RELOAD_ICON))
        self._refresh = CTkButton(self._top_frame, image=reload_img, text='', width=30, command=self._search_devices)
        self._refresh.pack(side="right", padx=10, pady=10)

        self._device_option = CTkOptionMenu(self._top_frame, width=150, command=self._set_device)
        self._device_option.pack(side="right", padx=10, pady=10)

        # Left Top Frame
        self._left_label = CTkLabel(self._left_top_frame, text='Information')
        self._left_label.pack(padx=10, pady=10)
        self._left_label.configure(font=FONT_CATEGORY)

        self._chip_info_btn = CTkButton(self._left_top_frame, text='Chip ID', command=self._get_chip_id)
        self._chip_info_btn.pack(padx=10, pady=5)

        self._memory_info_btn = CTkButton(self._left_top_frame, text='Flash ID', command=self._get_flash_id)
        self._memory_info_btn.pack(padx=10, pady=5)

        self._mac_info_btn = CTkButton(self._left_top_frame, text='MAC Address', command=self._get_mac)
        self._mac_info_btn.pack(padx=10, pady=5)

        self._flash_status_btn = CTkButton(self._left_top_frame, text='Flash Status', command=self._get_flash_status)
        self._flash_status_btn.pack(padx=10, pady=5)
        self._flash_status_btn.pack_forget()

        self._mp_version_btn = CTkButton(self._left_top_frame, text='Version', command=self._get_version)
        self._mp_version_btn.pack(padx=10, pady=5)
        self._mp_version_btn.configure(fg_color='green')
        self._mp_version_btn.pack_forget()

        self._mp_structure_btn = CTkButton(self._left_top_frame, text='File Structure', command=self._get_structure)
        self._mp_structure_btn.pack(padx=10, pady=5)
        self._mp_structure_btn.configure(fg_color='green')
        self._mp_structure_btn.pack_forget()

        # Left Bottom Frame
        self._left_bottom_label = CTkLabel(self._left_bottom_frame, text='Erase')
        self._left_bottom_label.pack(padx=10, pady=10)
        self._left_bottom_label.configure(font=FONT_CATEGORY)

        self._erase_btn = CTkButton(self._left_bottom_frame, text='Erase Flash', command=self._erase_flash)
        self._erase_btn.pack(padx=10, pady=5)

        # Right Frame
        self._right_label = CTkLabel(self._right_frame, text='Flash Configuration')
        self._right_label.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="w")
        self._right_label.configure(font=FONT_CATEGORY)

        self._expert_mode = CTkSwitch(self._right_frame, text='Expert Mode', command=self.toggle_expert_mode)
        self._expert_mode.grid(row=0, column=5, padx=10, pady=5, sticky="e")

        # Right Frame (chip select)
        self._chip_label = CTkLabel(self._right_frame, text='Step 1:')
        self._chip_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        chip_options = ["Select Chip"] + list(CONFIGURED_DEVICES.keys())
        self._chip_option = CTkOptionMenu(self._right_frame, values=chip_options, width=150)
        self._chip_option.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self._chip_option.set("Select Chip")
        self._chip_option.configure(command=self._set_chip)

        self._chip_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled', width=20)
        self._chip_checkbox.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self._chip_info = CTkLabel(self._right_frame, text='Choose the chip type to flash')
        self._chip_info.grid(row=1, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self._chip_info.configure(font=FONT_DESCRIPTION)

        # Right Frame (firmware select)
        self._firmware_label = CTkLabel(self._right_frame, text='Step 2:')
        self._firmware_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self._firmware_btn = CTkButton(self._right_frame, text='Select Firmware', width=150)
        self._firmware_btn.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self._firmware_btn.configure(command=self._set_firmware)

        self._firmware_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled', width=20)
        self._firmware_checkbox.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        self._link_label = CTkLabel(self._right_frame, text='Browse', text_color=LINK_OBJECT, cursor="hand2")
        self._link_label.grid(row=2, column=3, padx=(10, 0), pady=5, sticky="w")
        self._link_label.configure(font=(*FONT_DESCRIPTION, "underline"))
        self._link_label.bind("<Button-1>", self.open_url)

        self._firmware_info = CTkLabel(self._right_frame, text='and select the firmware file to upload')
        self._firmware_info.grid(row=2, column=4, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        self._firmware_info.configure(font=FONT_DESCRIPTION)

        # Right Frame (baudrate select)
        self._baudrate_label = CTkLabel(self._right_frame, text='Step 3:')
        self._baudrate_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self._baudrate_option = CTkOptionMenu(self._right_frame, values=self._BAUDRATE_OPTIONS, width=150)
        self._baudrate_option.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self._baudrate_option.set(str(self.__selected_baudrate))
        self._baudrate_option.configure(command=self._set_baudrate)

        self._baudrate_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled', width=20)
        self._baudrate_checkbox.grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self._baudrate_checkbox.select()

        self._baudrate_info = CTkLabel(self._right_frame, text='Choose a communication speed')
        self._baudrate_info.grid(row=3, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self._baudrate_info.configure(font=FONT_DESCRIPTION)

        # Right Frame (sector select)
        self._sector_label = CTkLabel(self._right_frame, text='Step 4:')
        self._sector_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self._sector_input = CTkEntry(self._right_frame, width=150)
        self._sector_input.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self._sector_input.bind("<KeyRelease>", self._on_sector_input_change)

        self._sector_checkbox = CTkCheckBox(self._right_frame, text='', state='disabled', width=20)
        self._sector_checkbox.grid(row=4, column=2, padx=10, pady=5, sticky="w")

        self._sector_info = CTkLabel(self._right_frame, text='Set the starting address for firmware')
        self._sector_info.grid(row=4, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self._sector_info.configure(font=FONT_DESCRIPTION)

        # Right Frame (expert mode)
        self._flash_mode_label = CTkLabel(self._right_frame, text='Step 5:')
        self._flash_mode_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self._flash_mode_label.grid_remove()

        self._flash_mode_option = CTkOptionMenu(self._right_frame, values=self._FLASH_MODE_OPTIONS, width=150)
        self._flash_mode_option.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        self._flash_mode_option.set("keep")
        self._flash_mode_option.grid_remove()

        self._flash_mode_info = CTkLabel(self._right_frame, text='Choose the data transfer mode for flashing')
        self._flash_mode_info.grid(row=5, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self._flash_mode_info.grid_remove()

        self._flash_frequency_label = CTkLabel(self._right_frame, text='Step 6:')
        self._flash_frequency_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self._flash_frequency_label.grid_remove()

        self._flash_frequency_option = CTkOptionMenu(self._right_frame, values=self._FLASH_FREQUENCY_OPTIONS, width=150)
        self._flash_frequency_option.grid(row=6, column=1, padx=10, pady=5, sticky="w")
        self._flash_frequency_option.set("keep")
        self._flash_frequency_option.grid_remove()

        self._flash_frequency_info = CTkLabel(self._right_frame, text='Set the clock speed during flash operations')
        self._flash_frequency_info.grid(row=6, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self._flash_frequency_info.grid_remove()

        self._flash_size_label = CTkLabel(self._right_frame, text='Step 7:')
        self._flash_size_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self._flash_size_label.grid_remove()

        self._flash_size_option = CTkOptionMenu(self._right_frame, values=self._FLASH_SIZE_OPTIONS, width=150)
        self._flash_size_option.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        self._flash_size_option.set("detect")
        self._flash_size_option.grid_remove()

        self._flash_size_info = CTkLabel(self._right_frame, text='Specify or detect the flash memory size')
        self._flash_size_info.grid(row=7, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self._flash_size_info.grid_remove()

        self._erase_before_label = CTkLabel(self._right_frame, text='Step 8:')
        self._erase_before_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
        self._erase_before_label.grid_remove()

        self._erase_before_switch = CTkSwitch(self._right_frame, text='')
        self._erase_before_switch.grid(row=8, column=1, padx=10, pady=5, sticky="w")
        self._erase_before_switch.grid_remove()

        self._erase_before_info = CTkLabel(self._right_frame, text='Erase flash before flashing firmware')
        self._erase_before_info.grid(row=8, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        self._erase_before_info.grid_remove()

        # Right Frame (seperator)
        self._separator_canvas = Canvas(self._right_frame, height=1, highlightthickness=0, bg="white", bd=0)
        self._separator_canvas.grid(row=9, columnspan=6, sticky="ew", padx=10, pady=10)

        # Right Frame (start firmware flash)
        self._flash_btn = CTkButton(self._right_frame, text='Flash Firmware', command=self._flash_firmware)
        self._flash_btn.grid(row=10, column=1, columnspan=5, padx=10, pady=5, sticky="w")

        # Bottom Frame
        self._bottom_label = CTkLabel(self._bottom_frame, text='Console Output')
        self._bottom_label.pack(padx=10, pady=10)
        self._bottom_label.configure(font=FONT_CATEGORY)

        self._console_text = CTkTextbox(self._bottom_frame, width=800, height=300)
        self._console_text.pack(padx=10, pady=10, fill="both", expand=True)
        self._console_text.tag_config("info", foreground=CONSOLE_INFO)
        self._console_text.tag_config("normal", foreground=CONSOLE_COMMAND)
        self._console_text.tag_config("error", foreground=CONSOLE_ERROR)
        self._console_text.bind("<Key>", self._block_text_input)
        self._console_text.bind("<Control-c>", lambda e: None)
        self._console_text.bind("<Control-C>", lambda e: None)

        # search for devices on the start
        self._search_devices()

        # poll the console queue for new lines
        self._poll_console_queue()

    @staticmethod
    def _block_text_input(event: Event) -> str:
        """
        Filters keyboard input events to block specific keys or combinations.

        :param event: A keyboard event containing information such as the key pressed.
        :type event: Event
        :return: A string indicating whether the keypress should be stopped or allowed.
        :rtype: str
        """
        allowed_keys = ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R")

        if event.keysym in allowed_keys or event.state & 0x0004:
            return ""

        return "break"

    def toggle_expert_mode(self) -> None:
        """
        Toggles between expert mode and standard mode in the user interface.

        :return: None
        """
        if self._expert_mode.get():
            debug('Expert mode enabled')
            self.__expert_mode = True
            self._flash_status_btn.pack(padx=10, pady=5)
            self._mp_version_btn.pack(padx=10, pady=5)
            self._mp_structure_btn.pack(padx=10, pady=5)
            self._flash_mode_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
            self._flash_mode_option.grid(row=5, column=1, padx=10, pady=5, sticky="w")
            self._flash_mode_info.grid(row=5, column=3, columnspan=3, padx=10, pady=5, sticky="w")
            self._flash_frequency_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
            self._flash_frequency_option.grid(row=6, column=1, padx=10, pady=5, sticky="w")
            self._flash_frequency_info.grid(row=6, column=3, columnspan=3, padx=10, pady=5, sticky="w")
            self._flash_size_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
            self._flash_size_option.grid(row=7, column=1, padx=10, pady=5, sticky="w")
            self._flash_size_info.grid(row=7, column=3, columnspan=3, padx=10, pady=5, sticky="w")
            self._erase_before_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
            self._erase_before_switch.grid(row=8, column=1, padx=10, pady=5, sticky="w")
            self._erase_before_info.grid(row=8, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        else:
            debug('Expert mode disabled')
            self.__expert_mode = False
            self._flash_status_btn.pack_forget()
            self._mp_version_btn.pack_forget()
            self._mp_structure_btn.pack_forget()
            self._flash_mode_label.grid_remove()
            self._flash_mode_option.grid_remove()
            self._flash_mode_info.grid_remove()
            self._flash_frequency_label.grid_remove()
            self._flash_frequency_option.grid_remove()
            self._flash_frequency_info.grid_remove()
            self._flash_size_label.grid_remove()
            self._flash_size_option.grid_remove()
            self._flash_size_info.grid_remove()
            self._erase_before_label.grid_remove()
            self._erase_before_switch.grid_remove()
            self._erase_before_info.grid_remove()

    def _set_device(self, selected_device: Optional[str]) -> None:
        """
        Handles the selection of a device using a device selection dialog, updates the
        device path, and modifies the configuration label to display the new device path.

        :param selected_device: The selected device path as a string.
        :type selected_device: Optional[str]
        :return: None
        """
        if selected_device and selected_device not in ("Select Device", "No devices found"):
            info(f'Selected device: {selected_device}')
            self.__device_path = selected_device
            self._device_path_label.configure(text=f'Device Path: {self.__device_path}')
        else:
            self.__device_path = None
            self._device_path_label.configure(text='Device Path:')

    def _set_chip(self, selection: str) -> None:
        """
        Sets the chip configuration based on the provided selection.

        :param selection: The selected chip name as a string.
        :type selection: str
        :return: None
        """
        debug(f'Selected chip: {selection}')

        if selection != "Select Chip":
            self.__selected_chip = CONFIGURED_DEVICES[selection]["name"]
            self._sector_input.delete(0, "end")
            self._sector_input.insert(0, hex(CONFIGURED_DEVICES[selection]["write_flash"]))
            self._chip_checkbox.select()
            self._baudrate_checkbox.select()
            self._sector_checkbox.select()
            self.__url = CONFIGURED_DEVICES[selection]["url"]
        else:
            self.__selected_chip = None
            self._sector_input.delete(0, "end")
            self._chip_checkbox.deselect()
            self.__url = DEFAULT_URL

    def _set_baudrate(self, selection: str) -> None:
        """
        Sets the baud rate based on the user selection if it is a valid option.

        :param selection: The baud rate option as a string that the user has selected.
        :type selection: str
        :return: None
        """
        debug(f'Selected baudrate: {selection}')

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
        default_dir = expanduser(self._firmware_search_path)

        file_path = filedialog.askopenfilename(
            initialdir=default_dir,
            title='Select Firmware File',
            filetypes=(("Binary files", "*.bin"), ("All files", "*.*"))
        )
        debug(f'Selected firmware: {file_path}')

        if file_path:
            self.__selected_firmware = file_path
            self._firmware_checkbox.select()
        else:
            self.__selected_firmware = None
            self._firmware_checkbox.deselect()

    def open_url(self, event: Event) -> None:
        """
        Opens a new web browser tab or window using the URL specified in the class attribute.

        :param event: The event instance triggering this method
        :type event: Event
        :return: None
        """
        _ = event
        open_new(url=self.__url)

    def _poll_console_queue(self) -> None:
        """
        Polls the console queue for new messages and updates the text widget
        with messages retrieved from the queue. Continuously checks the
        console queue at regular intervals, inserts retrieved lines into
        the text widget, and ensures the view stays scrolled to the most
        recent message.

        :raises Empty: This is silently handled within the method logic when the queue is empty.
        :return: This method does not return any value.
        """
        try:
            while True:
                line = self._console_queue.get_nowait()
                self._console_text.insert("end", f'{line}\n', "normal")
                self._console_text.see("end")
        except Empty:
            pass

        self.after(100, self._poll_console_queue)

    def _search_devices(self) -> None:
        """
        Updates the device dropdown menu with a list of available devices. If there are no
        connected devices, sets "No devices found" as the only dropdown value.

        :return: None
        """
        current_selection = self._device_option.get()

        if self._current_platform in ["Linux", "Darwin"]:
            devices = glob(self._device_search_path)
        else:
            devices = [port.device for port in list_ports.comports()]

        if not devices:
            devices = ['No devices found']
        else:
            devices.insert(0, 'Select Device')

        debug(f'Devices: {devices}')
        self._device_option.configure(values=devices)

        if current_selection in devices:
            self._device_option.set(current_selection)
        else:
            self._device_option.set(devices[0])
            self._set_device(None)

    def _delete_console(self) -> None:
        """
        Deletes all the content from the console text box.

        :return: None
        """
        self._console_text.delete("1.0", "end")

    def _disable_buttons(self) -> None:
        """
        Disables specific buttons in the user interface by changing their state to 'disabled'.

        :return: None
        """
        self._chip_info_btn.configure(state='disabled')
        self._memory_info_btn.configure(state='disabled')
        self._mac_info_btn.configure(state='disabled')
        self._flash_status_btn.configure(state='disabled')
        self._mp_version_btn.configure(state='disabled')
        self._mp_structure_btn.configure(state='disabled')
        self._erase_btn.configure(state='disabled')
        self._flash_btn.configure(state='disabled')

    def _enable_buttons(self) -> None:
        """
        Enables specific UI buttons by changing their state to 'normal'.

        :return: None
        """
        self._chip_info_btn.configure(state='normal')
        self._memory_info_btn.configure(state='normal')
        self._mac_info_btn.configure(state='normal')
        self._flash_status_btn.configure(state='normal')
        self._mp_version_btn.configure(state='normal')
        self._mp_structure_btn.configure(state='normal')
        self._erase_btn.configure(state='normal')
        self._flash_btn.configure(state='normal')

    def _on_thread_complete(self) -> None:
        """
        Handle the completion of a thread, perform the necessary cleanup and post-processing.

        :return: None
        """
        self._enable_buttons()

    def _run_threaded_command(self, command: List[str]) -> None:
        """
        Executes a given command on a separate thread to avoid blocking the
        main execution flow. The method ensures that UI buttons are
        disabled while the command is being executed in the background.

        :param command: A list of strings representing the command and its arguments to be executed.
        :type command: List[str]
        :return: None
        """
        self._disable_buttons()

        thread = Thread(target=self._execute_command, args=(command,))
        thread.start()

    def _execute_command(self, command: List[str]) -> None:
        """
        Executes a command as a subprocess and processes its output line by line. The method
        also filters specific lines of output related to flash identification and handles
        command completion by calling a callback function.

        :param command: A list of strings representing the command and its arguments to be executed.
        :type command: List[str]
        :return: None
        """
        is_flash_id = "flash_id" in command
        process = Popen(command, stdout=PIPE, stderr=PIPE, text=True)

        while True:
            line = process.stdout.readline()
            if not line:
                break

            line = line.strip()
            if is_flash_id and (
                    "Chip is" in line or
                    "Detected flash size" in line or
                    "Detecting chip type" in line
            ):
                info(line)

            self._console_queue.put(line)

        process.wait()

        if process.returncode != 0:
            error_output = process.stderr.read().strip()
            self._console_queue.put(f'[ERROR]: {error_output}')

        self.after(0, self._on_thread_complete)

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

    def _get_mac(self) -> None:
        """
        Retrieves the mac address information for the connected device.

        :return: None
        """
        self._run_esptool_command("read_mac")

    def _get_flash_status(self) -> None:
        """
        Retrieves the flash memory status information for the connected device.

        :return: None
        """
        self._run_esptool_command("read_flash_status")

    def _get_version(self) -> None:
        """
        Gets the MicroPython version and updates the console with the retrieved version information.

        :return: None
        """
        debug('Get MicroPython version')
        self._delete_console()

        if not self.__device_path:
            error('No device selected!')
            self._console_text.insert("end", '[ERROR] No device selected!\n', "error")
            return

        self._disable_buttons()
        self._console_text.insert("end", f'[INFO] Getting MicroPython version...\n', "info")

        def task():
            try:
                with MicroPythonVersion(port=self.__device_path) as mpt:
                    version = mpt.get_version()

                if version:
                    self._console_queue.put(version)
                else:
                    self._console_queue.put('[ERROR] Could not get MicroPython version')

            except Exception as e:
                self._console_queue.put(f'[ERROR] Exception: {e}')
            finally:
                self.after(0, self._enable_buttons)

        Thread(target=task, daemon=True).start()

    def _get_structure(self) -> None:
        """
        Gets the file and folder structure of the device.

        :return: None
        """
        debug('Get device structure')
        self._delete_console()

        if not self.__device_path:
            error('No device selected!')
            self._console_text.insert("end", '[ERROR] No device selected!\n', "error")
            return

        self._disable_buttons()
        self._console_text.insert("end", f'[INFO] Getting device structure...\n', "info")

        def task():
            try:
                with MicroPythonFileStructure(port=self.__device_path) as mpt:
                    structure = mpt.get_tree()

                if structure and structure != "[ERROR] Timeout":
                    self._console_queue.put(f'root\n{structure}')
                else:
                    self._console_queue.put('[ERROR] Could not get device structure')
            except Exception as e:
                self._console_queue.put(f'[ERROR] Exception: {e}')
            finally:
                self.after(0, self._enable_buttons)

        Thread(target=task, daemon=True).start()

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
        debug(f'Running esptool command: {command_name}')
        self._delete_console()

        allowed_commands = {"chip_id", "flash_id", "read_mac", "read_flash_status", "erase_flash"}
        if command_name not in allowed_commands:
            error(f'Invalid command: {command_name}')
            self._console_text.insert("end", f'[ERROR] Invalid command: {command_name}\n', "error")
            return

        if not self.__device_path:
            error('No device selected!')
            self._console_text.insert("end", '[ERROR] No device selected!\n', "error")
            return

        chip = self.__selected_chip if self.__selected_chip else "auto"
        cmd = ["python", "-m", "esptool",
               "-c", chip,
               "-p",
               self.__device_path,
               command_name]

        self._console_text.insert("end", f'[INFO] {" ".join(cmd)}\n\n', "info")
        self._run_threaded_command(command=cmd)

    def _flash_firmware(self) -> None:
        """
        Internal method to flash firmware to the connected device.

        :return: None
        """
        self._delete_console()

        errors = []
        if not self.__device_path:
            errors.append('No device path selected')

        if not self.__selected_chip:
            errors.append('No chip selected')

        if not self.__selected_firmware:
            errors.append('No firmware selected')

        if not self.__selected_baudrate:
            errors.append('No baudrate selected')

        if not self._sector_input.get().strip():
            errors.append('No sector value provided')

        if errors:
            error(f'Found errors: {errors}')
            self._console_text.insert("end", f'[ERROR] {", ".join(errors)}\n', "error")
            return

        cmd = ["python", "-m", "esptool",
               '-p', self.__device_path,
               '-c', self.__selected_chip,
               '-b', str(self.__selected_baudrate),
               'write_flash', self._sector_input.get().strip(),
               self.__selected_firmware]

        if self.__expert_mode:
            flash_mode = self._flash_mode_option.get().strip()
            flash_freq = self._flash_frequency_option.get().strip()
            flash_size = self._flash_size_option.get().strip()

            expert_args = ['-fm', flash_mode, '-ff', flash_freq, '-fs', flash_size]

            if self._erase_before_switch.get():
                expert_args.append('-e')

            index = cmd.index('write_flash') + 1
            cmd = cmd[:index] + expert_args + cmd[index:]

        debug(f'Running esptool command: {cmd}')
        self._console_text.insert("end", f'[INFO] {" ".join(cmd)}\n\n', "info")
        self._run_threaded_command(command=cmd)
