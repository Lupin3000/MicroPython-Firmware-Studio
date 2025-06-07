from logging import basicConfig, info
from customtkinter import set_appearance_mode, set_default_color_theme
from lib.firmware_studio import MicroPythonFirmwareStudio


if __name__ == "__main__":
    basicConfig(
        level='INFO',
        format='[%(levelname)s] %(message)s'
    )

    set_appearance_mode("dark")
    set_default_color_theme('blue')

    info("Starting MicroPython Firmware Studio")
    app = MicroPythonFirmwareStudio()
    app.mainloop()
