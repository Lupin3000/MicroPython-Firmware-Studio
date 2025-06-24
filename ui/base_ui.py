from logging import getLogger, debug, error
from platform import system
from customtkinter import CTk
from tkinter import Event
from config.application_configuration import TITLE
from config.os_configuration import OPERATING_SYSTEM


logger = getLogger(__name__)


class BaseUI(CTk):
    """
    BaseUI is responsible for the overall layout and initialization of the graphical
    user interface (GUI). It manages the creation of UI frames.
    """

    def __init__(self):
        """
        Initializes an object that configures the application layout and checks the
        current operating system for compatibility. Constructs a GUI structure with
        specific frames and layout configurations.

        :raises Exception: If the detected operating system is not supported.
        """
        super().__init__()

        self._current_platform = system()
        if self._current_platform not in OPERATING_SYSTEM:
            error(f'Unsupported operating system: {self._current_platform}')
            raise Exception(f'Unsupported operating system: {self._current_platform}')
        else:
            debug(f'Current platform: {self._current_platform}')
            self._device_search_path = OPERATING_SYSTEM[self._current_platform]['device_path']
            self._firmware_search_path = OPERATING_SYSTEM[self._current_platform]['search_path']

        self.title(TITLE)
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure((1, 2, 3), weight=1)

    @staticmethod
    def _block_text_input(event: Event) -> str:
        """
        Filters keyboard input events to block specific keys or combinations.

        :param event: A keyboard event containing information such as the key pressed.
        :type event: Event
        :return: A string indicating whether the keypress should be stopped or allowed.
        :rtype: str
        """
        is_copy = (event.state & 0x000C) and event.keysym.lower() == 'c'
        is_select_all = (event.state & 0x000C) and event.keysym.lower() == 'a'

        if is_copy or is_select_all:
            return ""

        return "break"

    def destroy(self) -> None:
        """
        Terminates the execution of the current process or application by invoking
        the quit method associated with the instance.

        :return: None
        """
        self.quit()
