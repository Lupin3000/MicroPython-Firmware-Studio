from logging import getLogger, debug
from serial_plugin.serial_base import SerialBase


logger = getLogger(__name__)


class Version(SerialBase):
    """
    Represents a utility for interacting with a MicroPython device to fetch the
    current Micropython version information over a serial connection.
    """

    @staticmethod
    def _extract_version(raw_output: str) -> str:
        """
        Extracts the MicroPython version string from raw output.

        :param raw_output: The raw string output to parse.
        :type raw_output: str
        :return: MicroPython version as a string or a default message.
        :rtype: str
        """
        lines = raw_output.splitlines()

        for line in lines:
            if "MicroPython" in line:
                return line.strip().split(";")[1].strip()

        return "No MicroPython version found"

    def get_version(self) -> str:
        """
        Extracts and returns the Python version from the command output.

        :param self: The instance of the class calling the method.
        :return: The extracted Python version as a string.
        :rtype: str
        """
        output = self.send_repl_command("import sys; print(sys.version)")
        debug(f"[DEBUG] version output: {output}")

        return self._extract_version(output)
