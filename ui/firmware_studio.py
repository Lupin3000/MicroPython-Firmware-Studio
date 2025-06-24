from glob import glob
from serial.tools import list_ports
from logging import getLogger, debug, info, error
from os.path import expanduser
from tkinter import filedialog, Event
from webbrowser import open_new
from typing import Optional, Callable
from queue import Queue, Empty
from ui.base_ui import BaseUI
from ui.frame_device_information import FrameDeviceInformation
from ui.frame_erase_device import FrameEraseDevice
from ui.frame_firmware_flash import FrameFirmwareFlash
from ui.frame_search_device import FrameSearchDevice
from ui.frame_console import FrameConsole
from esptool_plugin.esptool_command_runner import CommandRunner
from serial_plugin.serial_command_runner import SerialCommandRunner
from config.device_configuration import BAUDRATE_OPTIONS, DEFAULT_URL, CONFIGURED_DEVICES
from config.application_configuration import (FONT_PATH, FONT_CATEGORY, FONT_DESCRIPTION, CONSOLE_INFO,
                                              CONSOLE_COMMAND, CONSOLE_ERROR)


logger = getLogger(__name__)


class MicroPythonFirmwareStudio(BaseUI):
    """
    A class representing the MicroPython Firmware Studio GUI via CTkinter.
    """

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

        self.esptool_runner = CommandRunner(
            on_output=self._handle_esptool_output,
            on_error=self._handle_esptool_error,
            on_complete=self._handle_esptool_complete
        )

        # Search Device
        self.search_device = FrameSearchDevice(self)
        self.search_device.label.configure(font=FONT_PATH)
        self.search_device.reload_btn.configure(command=self._search_devices)
        self.search_device.device_option.configure(command=self._set_device)

        # Device Information
        self.information = FrameDeviceInformation(self)
        self.information.label.configure(font=FONT_CATEGORY)
        self.information.chip_info_btn.configure(command=lambda: self._esptool_command("chip_id"))
        self.information.memory_info_btn.configure(command=lambda: self._esptool_command("flash_id"))
        self.information.mac_info_btn.configure(command=lambda: self._esptool_command("read_mac"))
        self.information.flash_status_btn.configure(command=lambda: self._esptool_command("read_flash_status"))
        self.information.flash_status_btn.pack_forget()
        self.information.mp_version_btn.configure(command=self._get_version)
        self.information.mp_version_btn.pack_forget()
        self.information.mp_structure_btn.configure(command=self._get_structure)
        self.information.mp_structure_btn.pack_forget()

        # Erase Device
        self.erase_device = FrameEraseDevice(self)
        self.erase_device.label.configure(font=FONT_CATEGORY)
        self.erase_device.erase_btn.configure(command=lambda: self._esptool_command("erase_flash"))

        # Flash Firmware
        self.flash_firmware = FrameFirmwareFlash(self)
        self.flash_firmware.label.configure(font=FONT_CATEGORY)
        self.flash_firmware.expert_mode.configure(command=self.toggle_expert_mode)
        self.flash_firmware.chip_option.set("Select Chip")
        self.flash_firmware.chip_option.configure(command=self._set_chip)
        self.flash_firmware.chip_info.configure(font=FONT_DESCRIPTION)
        self.flash_firmware.firmware_btn.configure(command=self._handle_firmware_selection)
        self.flash_firmware.link_label.configure(font=(*FONT_DESCRIPTION, "underline"))
        self.flash_firmware.link_label.bind("<Button-1>", self.open_url)
        self.flash_firmware.firmware_info.configure(font=FONT_DESCRIPTION)
        self.flash_firmware.baudrate_option.set(str(self.__selected_baudrate))
        self.flash_firmware.baudrate_option.configure(command=self._set_baudrate)
        self.flash_firmware.baudrate_checkbox.select()
        self.flash_firmware.baudrate_info.configure(font=FONT_DESCRIPTION)
        self.flash_firmware.sector_input.bind("<KeyRelease>", self._handle_sector_input)
        self.flash_firmware.sector_info.configure(font=FONT_DESCRIPTION)
        self.flash_firmware.flash_mode_label.grid_remove()
        self.flash_firmware.flash_mode_option.set("keep")
        self.flash_firmware.flash_mode_option.grid_remove()
        self.flash_firmware.flash_mode_info.grid_remove()
        self.flash_firmware.flash_frequency_label.grid_remove()
        self.flash_firmware.flash_frequency_option.set("keep")
        self.flash_firmware.flash_frequency_option.grid_remove()
        self.flash_firmware.flash_frequency_info.grid_remove()
        self.flash_firmware.flash_size_label.grid_remove()
        self.flash_firmware.flash_size_option.set("detect")
        self.flash_firmware.flash_size_option.grid_remove()
        self.flash_firmware.flash_size_info.grid_remove()
        self.flash_firmware.erase_before_label.grid_remove()
        self.flash_firmware.erase_before_switch.grid_remove()
        self.flash_firmware.erase_before_info.grid_remove()
        self.flash_firmware.flash_btn.configure(command=self._flash_firmware_command)

        # Console
        self.console = FrameConsole(self)
        self.console.label.configure(font=FONT_CATEGORY)
        self.console.console_text.tag_config("info", foreground=CONSOLE_INFO)
        self.console.console_text.tag_config("normal", foreground=CONSOLE_COMMAND)
        self.console.console_text.tag_config("error", foreground=CONSOLE_ERROR)
        self.console.console_text.bind("<Key>", BaseUI._block_text_input)

        # search for devices on the start
        self._search_devices()

        # poll the console queue for new lines
        self._poll_console_queue()

    def open_url(self, event: Event) -> None:
        """
        Opens a new web browser tab or window using the URL specified in the class attribute.

        :param event: The event instance is triggering this method
        :type event: Event
        :return: None
        """
        _ = event

        debug(f'Opening URL: {self.__url}')
        open_new(url=self.__url)

    def toggle_expert_mode(self) -> None:
        """
        Toggles between expert mode and standard mode in the user interface.

        :return: None
        """
        if self.flash_firmware.expert_mode.get():
            debug('Expert mode enabled')
            self.__expert_mode = True
            self.information.flash_status_btn.pack(padx=10, pady=5)
            self.information.mp_version_btn.pack(padx=10, pady=5)
            self.information.mp_structure_btn.pack(padx=10, pady=5)
            self.flash_firmware.flash_mode_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_mode_option.grid(row=5, column=1, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_mode_info.grid(row=5, column=3, columnspan=3, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_frequency_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_frequency_option.grid(row=6, column=1, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_frequency_info.grid(row=6, column=3, columnspan=3, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_size_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_size_option.grid(row=7, column=1, padx=10, pady=5, sticky="w")
            self.flash_firmware.flash_size_info.grid(row=7, column=3, columnspan=3, padx=10, pady=5, sticky="w")
            self.flash_firmware.erase_before_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
            self.flash_firmware.erase_before_switch.grid(row=8, column=1, padx=10, pady=5, sticky="w")
            self.flash_firmware.erase_before_info.grid(row=8, column=3, columnspan=3, padx=10, pady=5, sticky="w")
        else:
            debug('Expert mode disabled')
            self.__expert_mode = False
            self.information.flash_status_btn.pack_forget()
            self.information.mp_version_btn.pack_forget()
            self.information.mp_structure_btn.pack_forget()
            self.flash_firmware.flash_mode_label.grid_remove()
            self.flash_firmware.flash_mode_option.grid_remove()
            self.flash_firmware.flash_mode_info.grid_remove()
            self.flash_firmware.flash_frequency_label.grid_remove()
            self.flash_firmware.flash_frequency_option.grid_remove()
            self.flash_firmware.flash_frequency_info.grid_remove()
            self.flash_firmware.flash_size_label.grid_remove()
            self.flash_firmware.flash_size_option.grid_remove()
            self.flash_firmware.flash_size_info.grid_remove()
            self.flash_firmware.erase_before_label.grid_remove()
            self.flash_firmware.erase_before_switch.grid_remove()
            self.flash_firmware.erase_before_info.grid_remove()

    def _poll_console_queue(self) -> None:
        """
        Polls the console queue for new messages and updates the text widget
        with messages retrieved from the queue. Continuously checks the
        console queue at regular intervals, inserts retrieved lines into
        the text widget, and ensures the view stays scrolled to the most
        recent message.

        :raises Empty: This is silently handled within the method logic when the queue is empty.
        :return: None
        """
        try:
            while True:
                line = self._console_queue.get_nowait()
                self.console.console_text.insert("end", f'{line}\n', "normal")
                self.console.console_text.see("end")
        except Empty:
            pass

        self.after(100, self._poll_console_queue)

    def _delete_console(self) -> None:
        """
        Deletes all the content from the console text box.

        :return: None
        """
        self.console.console_text.delete("1.0", "end")

    def _disable_buttons(self) -> None:
        """
        Disables specific buttons in the user interface by changing their state to 'disabled'.

        :return: None
        """
        self.information.chip_info_btn.configure(state='disabled')
        self.information.memory_info_btn.configure(state='disabled')
        self.information.mac_info_btn.configure(state='disabled')
        self.information.flash_status_btn.configure(state='disabled')
        self.information.mp_version_btn.configure(state='disabled')
        self.information.mp_structure_btn.configure(state='disabled')
        self.erase_device.erase_btn.configure(state='disabled')
        self.flash_firmware.flash_btn.configure(state='disabled')

    def _enable_buttons(self) -> None:
        """
        Enables specific UI buttons by changing their state to 'normal'.

        :return: None
        """
        self.information.chip_info_btn.configure(state='normal')
        self.information.memory_info_btn.configure(state='normal')
        self.information.mac_info_btn.configure(state='normal')
        self.information.flash_status_btn.configure(state='normal')
        self.information.mp_version_btn.configure(state='normal')
        self.information.mp_structure_btn.configure(state='normal')
        self.erase_device.erase_btn.configure(state='normal')
        self.flash_firmware.flash_btn.configure(state='normal')

    def _search_devices(self) -> None:
        """
        Updates the device dropdown menu with a list of available devices. If there are no
        connected devices, sets "No devices found" as the only dropdown value.

        :return: None
        """
        current_selection = self.search_device.device_option.get()

        if self._current_platform in ["Linux", "Darwin"]:
            devices = glob(self._device_search_path)
        else:
            devices = [port.device for port in list_ports.comports()]

        if not devices:
            devices = ['No devices found']
        else:
            devices.insert(0, 'Select Device')

        debug(f'Devices: {devices}')
        self.search_device.device_option.configure(values=devices)

        if current_selection in devices:
            self.search_device.device_option.set(current_selection)
        else:
            self.search_device.device_option.set(devices[0])
            self._set_device(None)

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
            self.search_device.label.configure(text=f'Device Path: {self.__device_path}')
        else:
            self.__device_path = None
            self.search_device.label.configure(text='Device Path:')

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
            self.flash_firmware.sector_input.delete(0, "end")
            self.flash_firmware.sector_input.insert(0, hex(CONFIGURED_DEVICES[selection]["write_flash"]))
            self.flash_firmware.chip_checkbox.select()
            self.flash_firmware.baudrate_checkbox.select()
            self.flash_firmware.sector_checkbox.select()
            self.__url = CONFIGURED_DEVICES[selection]["url"]
        else:
            self.__selected_chip = None
            self.flash_firmware.sector_input.delete(0, "end")
            self.flash_firmware.chip_checkbox.deselect()
            self.__url = DEFAULT_URL

    def _set_baudrate(self, selection: str) -> None:
        """
        Sets the baud rate based on the user selection if it is a valid option.

        :param selection: The baud rate option as a string that the user has selected.
        :type selection: str
        :return: None
        """
        debug(f'Selected baudrate: {selection}')

        if selection and selection in BAUDRATE_OPTIONS:
            self.__selected_baudrate = int(selection)
            self.flash_firmware.baudrate_checkbox.select()
        else:
            self.__selected_baudrate = None
            self.flash_firmware.baudrate_checkbox.deselect()

    def _handle_sector_input(self, event: Optional[Event] = None) -> None:
        """
        Handles changes to the sector input field and updates the sector checkbox
        state accordingly.

        :param event: An optional event object representing a UI change.
        :return: None
        """
        _ = event

        try:
            int(self.flash_firmware.sector_input.get().strip(), 0)
            self.flash_firmware.sector_checkbox.select()
        except ValueError:
            self.flash_firmware.sector_checkbox.deselect()

    def _handle_firmware_selection(self) -> None:
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
            self.flash_firmware.firmware_checkbox.select()
        else:
            self.__selected_firmware = None
            self.flash_firmware.firmware_checkbox.deselect()

    def _handle_serial_output(self, output: str, context: Optional[str] = None) -> None:
        """
        Handles the processing and queuing of serial output in the application.

        :param output: The output to be queued for processing.
        :type output: str
        :param context: An optional context string indicating the type of output.
        :type context: Optional[str]
        :return: None
        """
        if context == "structure":
            output = f"root\n{output}"

        self._console_queue.put(output)
        self.after(0, self._enable_buttons)

    def _run_serial_task(self, info_text: str, command: Callable[[SerialCommandRunner], None]) -> None:
        """
        Executes a serial task by running a provided command callable for a serial command runner.

        :param info_text: The text to be displayed in the console indicating the task being executed.
        :type info_text: str
        :param command: The command callable to be executed for the serial command runner.
        :type command: Callable[[SerialCommandRunner], None]
        :return: None
        """
        info(info_text)
        self._delete_console()

        if not self.__device_path:
            error('No device selected!')
            self.console.console_text.insert("end", '[ERROR] No device selected!\n', "error")
            return

        self._disable_buttons()
        self.console.console_text.insert("end", f'[INFO] {info_text}...\n', "info")

        runner = SerialCommandRunner()
        command(runner)

    def _get_version(self) -> None:
        """
        Triggers a task to get the MicroPython version and process its output.

        :return: None
        """
        self._run_serial_task(
            info_text="Getting MicroPython version",
            command=lambda runner: runner.get_version(
                port=self.__device_path,
                callback=lambda output: self._handle_serial_output(output)
            )
        )

    def _get_structure(self) -> None:
        """
        Triggers a task to get the file structure and process its output.

        :return: None
        """
        self._run_serial_task(
            info_text="Getting device structure",
            command=lambda runner: runner.get_structure(
                port=self.__device_path,
                callback=lambda output: self._handle_serial_output(output, "structure")
            )
        )

    def _handle_esptool_output(self, text: str) -> None:
        """
        Handles the output by scheduling a task for posting the text to the console queue.

        :param text: The text to be posted to the console queue.
        :type text: str
        :return: None
        """
        self.after(0, lambda: self._console_queue.put(text))

    def _handle_esptool_error(self, text: str) -> None:
        """
        Handles errors by updating the console text widget with the provided error message.

        :param text: The error message to be displayed in the console.
        :type text: str
        :return: None
        """
        self.after(0, lambda: self.console.console_text.insert("end", f'[ERROR] {text}\n', "error"))

    def _handle_esptool_complete(self) -> None:
        """
        Handles the completion of a specific task by enabling buttons.

        :return: None
        """
        self.after(0, lambda: self._enable_buttons())

    def _esptool_command(self, command_name: str) -> None:
        """
        Validate and prepares a simple esptool command based on user input.

        :param command_name: The name of the command to be executed.
        :type command_name: str
        :return: None
        """
        info(f'Prepare esptool command for: {command_name}')
        self._delete_console()

        allowed_commands = {"chip_id", "flash_id", "read_mac", "read_flash_status", "erase_flash"}
        if command_name not in allowed_commands:
            error(f'Invalid command: {command_name}')
            self.console.console_text.insert("end", f'[ERROR] Invalid command: {command_name}\n', "error")
            return

        if not self.__device_path:
            error('No device selected!')
            self.console.console_text.insert("end", '[ERROR] No device selected!\n', "error")
            return

        chip = self.__selected_chip if self.__selected_chip else "auto"
        cmd = ["python", "-m", "esptool",
               "-c", chip,
               "-p",
               self.__device_path,
               command_name]

        self._disable_buttons()
        self.console.console_text.insert("end", f'[INFO] {" ".join(cmd)}\n\n', "info")
        self.esptool_runner.run_threaded_command(command=cmd)

    def _flash_firmware_command(self) -> None:
        """
        Validate and prepares the esptool flash firmware command based on user input.

        :return: None
        """
        info('Prepare esptool command for: firmware flash')
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

        if not self.flash_firmware.sector_input.get().strip():
            errors.append('No sector value provided')

        if errors:
            error(f'Found errors: {errors}')
            self.console.console_text.insert("end", f'[ERROR] {", ".join(errors)}\n', "error")
            return

        cmd = ["python", "-m", "esptool",
               '-p', self.__device_path,
               '-c', self.__selected_chip,
               '-b', str(self.__selected_baudrate),
               'write_flash', self.flash_firmware.sector_input.get().strip(),
               self.__selected_firmware]

        if self.__expert_mode:
            flash_mode = self.flash_firmware.flash_mode_option.get().strip()
            flash_freq = self.flash_firmware.flash_frequency_option.get().strip()
            flash_size = self.flash_firmware.flash_size_option.get().strip()

            expert_args = ['-fm', flash_mode, '-ff', flash_freq, '-fs', flash_size]

            if self.flash_firmware.erase_before_switch.get():
                expert_args.append('-e')

            index = cmd.index('write_flash') + 1
            cmd = cmd[:index] + expert_args + cmd[index:]

        self._disable_buttons()
        self.console.console_text.insert("end", f'[INFO] {" ".join(cmd)}\n\n', "info")
        self.esptool_runner.run_threaded_command(command=cmd)
