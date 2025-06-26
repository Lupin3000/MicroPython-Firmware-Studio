from logging import getLogger, debug, error
from time import time
from .serial_base import SerialBase
from config.application_configuration import SERIAL_SECONDS


logger = getLogger(__name__)


class Debug(SerialBase):
    """
    Represents a utility for interacting with a device to fetch the
    current console output over a serial connection for a specific time.
    """

    def get_debug(self, seconds: int = SERIAL_SECONDS) -> str:
        """
        Retrieves debug information from a serial connection over a fixed period.

        :param seconds: The number of seconds to wait for debug information.
        :type seconds: int
        :return: The debug information as a string.
        :rtype: str
        """
        debug(f"read debug for {seconds} sec")
        output = []
        start_time = time()
        end_time = start_time + seconds

        while time() < end_time:
            try:
                if self._ser.in_waiting:
                    line = self._ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        debug(line)
                        output.append(line)
            except Exception as e:
                error(e)
                break

        return "\n".join(output)
