from logging import getLogger, debug
from customtkinter import CTkFrame, CTkLabel, CTkImage, CTkButton, CTkOptionMenu
from PIL import Image
from config.application_configuration import RELOAD_ICON


logger = getLogger(__name__)


class FrameSearchDevice(CTkFrame):
    """
    A specialized class designed to facilitate search device operations.
    """

    def __init__(self, master, *args, **kwargs):
        """
        A custom frame designed with widgets for select a device. This frame
        is a child of the specified parent widget (master) and includes a Label,
        Image, Button and an OptionMenu with customizable UI features.
        """
        super().__init__(master, *args, **kwargs)
        debug('Create Search Device Frame')

        self.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.label = CTkLabel(self, text='Device Path:')
        self.label.pack(side="left", padx=10, pady=10)

        reload_img = CTkImage(light_image=Image.open(RELOAD_ICON))

        self.reload_btn = CTkButton(self, image=reload_img, text='', width=30)
        self.reload_btn.pack(side="right", padx=10, pady=10)

        self.device_option = CTkOptionMenu(self, width=150)
        self.device_option.pack(side="right", padx=10, pady=10)
