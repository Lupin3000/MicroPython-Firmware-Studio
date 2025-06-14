from logging import basicConfig, info, error
from signal import signal, SIGINT
from atexit import register
from customtkinter import set_appearance_mode, set_default_color_theme
from config.application_configuration import APPEARANCE_MODE, COLOR_THEME, TITLE, LOG_LEVEL
from lib.firmware_studio import MicroPythonFirmwareStudio


def cleanup(*args) -> None:
    """
    Cleans up the application by attempting to destroy it.

    :param args: Arbitrary arguments that are not used by the function.
    :return: None
    """
    global app
    _ = args

    if app:
        try:
            app.destroy()
        except Exception as e:
            error(f'Error while shutting down application: {e}')


if __name__ == "__main__":
    basicConfig(
        level=LOG_LEVEL,
        format='[%(levelname)s] %(message)s'
    )

    set_appearance_mode(APPEARANCE_MODE)
    set_default_color_theme(COLOR_THEME)

    info(f'Starting {TITLE} Application...')
    app = MicroPythonFirmwareStudio()
    app.protocol("WM_DELETE_WINDOW", cleanup)

    register(cleanup)
    signal(SIGINT, cleanup)

    try:
        app.mainloop()
    except KeyboardInterrupt:
        info('KeyboardInterrupt received.')
    except Exception as err:
        error(f'Error while running application: {err}')
    finally:
        info('Shutting down application...')
        cleanup()
