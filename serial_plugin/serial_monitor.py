from logging import getLogger, debug
from .serial_base import SerialBase


logger = getLogger(__name__)


class Debug(SerialBase):
    """
    Represents a utility for interacting with a device to fetch the
    current console over a serial connection.
    """
    pass

    def get_debug(self) -> str:
        while True:
            line = self._ser.readline().decode('utf-8', errors='ignore').strip()

            if line:
                debug(line)