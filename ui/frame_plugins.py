from logging import getLogger, debug
from customtkinter import CTkFrame, CTkLabel, CTkButton


logger = getLogger(__name__)


class FramePlugIns(CTkFrame):
    """
    A specialized class designed to facilitate Serial Plugin operations.
    """

    def __init__(self, master, *args, **kwargs):
        """
        A custom frame designed with widgets for show plugins. This frame
        is a child of the specified parent widget (master) and includes a
         Label and Button customizable UI feature.
        """
        super().__init__(master, *args, **kwargs)
        debug('Create PlugIns Frame')

        self.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)

        self.label = CTkLabel(self, text='PlugIns')
        self.label.pack(padx=10, pady=10)

        self.mp_debug_btn = CTkButton(self, text='Debug', fg_color='green')
        self.mp_debug_btn.pack(padx=10, pady=5)

        self.mp_version_btn = CTkButton(self, text='Version', fg_color='green')
        self.mp_version_btn.pack(padx=10, pady=5)

        self.mp_structure_btn = CTkButton(self, text='File Structure', fg_color='green')
        self.mp_structure_btn.pack(padx=10, pady=5)
