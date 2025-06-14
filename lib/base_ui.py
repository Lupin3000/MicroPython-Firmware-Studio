from logging import getLogger, debug, error
from platform import system
from customtkinter import CTk, CTkFrame
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

        # Top Frame
        self._top_frame = CTkFrame(self)
        self._top_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        # Left Top Frame
        self._left_top_frame = CTkFrame(self)
        self._left_top_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self._left_top_frame.grid_columnconfigure(0, weight=1)

        # Left Bottom Frame
        self._left_bottom_frame = CTkFrame(self)
        self._left_bottom_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self._left_bottom_frame.grid_columnconfigure(0, weight=1)

        # Right Frame
        self._right_frame = CTkFrame(self)
        self._right_frame.grid(row=1, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")
        self._right_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=0)
        self._right_frame.grid_columnconfigure(5, weight=1)

        # Bottom Frame
        self._bottom_frame = CTkFrame(self)
        self._bottom_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        self._bottom_frame.grid_columnconfigure(0, weight=1)

    def destroy(self) -> None:
        """
        Terminates the execution of the current process or application by invoking
        the quit method associated with the instance.

        :return: None
        """
        self.quit()
