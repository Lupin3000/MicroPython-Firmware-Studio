from logging import basicConfig, info
from customtkinter import set_appearance_mode, set_default_color_theme
from config.application_configuration import APPEARANCE_MODE, COLOR_THEME, TITLE
from lib.firmware_studio import MicroPythonFirmwareStudio


if __name__ == "__main__":
    basicConfig(
        level='INFO',
        format='[%(levelname)s] %(message)s'
    )

    set_appearance_mode(APPEARANCE_MODE)
    set_default_color_theme(COLOR_THEME)

    info(f'Starting {TITLE} Application...')
    app = MicroPythonFirmwareStudio()
    app.mainloop()
