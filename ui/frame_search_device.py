from customtkinter import CTkFrame, CTkLabel, CTkImage, CTkButton, CTkOptionMenu
from PIL import Image
from config.application_configuration import FONT_PATH
from config.application_configuration import RELOAD_ICON


class FrameSearchDevice(CTkFrame):

    def __init__(self, master, *args, **kwargs):
        """
        A custom frame designed with widgets for select a device. This frame
        is a child of the specified parent widget (master) and includes an Label,
        Image, Button and an OptionMenu with customizable UI features.
        """
        super().__init__(master, *args, **kwargs)

        self.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.device_path_label = CTkLabel(self, text='Device Path:')
        self.device_path_label.pack(side="left", padx=10, pady=10)
        self.device_path_label.configure(font=FONT_PATH)

        reload_img = CTkImage(light_image=Image.open(RELOAD_ICON))

        self.refresh = CTkButton(self, image=reload_img, text='', width=30)
        self.refresh.pack(side="right", padx=10, pady=10)

        self.device_option = CTkOptionMenu(self, width=150)
        self.device_option.pack(side="right", padx=10, pady=10)
