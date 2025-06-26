from logging import getLogger, debug
from customtkinter import CTkFrame, CTkLabel, CTkTextbox
from config.application_configuration import FONT_CATEGORY
from config.application_configuration import CONSOLE_INFO, CONSOLE_COMMAND, CONSOLE_ERROR


logger = getLogger(__name__)


class FrameConsole(CTkFrame):
    """
    A specialized class designed to facilitate console output operations.
    """

    def __init__(self, master, *args, **kwargs):
        """
        A custom frame designed with widgets for erasing flash. This frame
        is a child of the specified parent widget (master) and includes a
        Label and a Textbox with customizable UI features.
        """
        super().__init__(master, *args, **kwargs)
        debug('Create Console Frame')

        self.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)

        self.label = CTkLabel(self, text='Console Output')
        self.label.pack(padx=10, pady=10)
        self.label.configure(font=FONT_CATEGORY)

        self.console_text = CTkTextbox(self, width=800, height=300)
        self.console_text.pack(padx=10, pady=10, fill="both", expand=True)
        self.console_text.tag_config("info", foreground=CONSOLE_INFO)
        self.console_text.tag_config("normal", foreground=CONSOLE_COMMAND)
        self.console_text.tag_config("error", foreground=CONSOLE_ERROR)
