from logging import getLogger, debug
from time import sleep
from lib.serial_base import MicroPythonSerialBase


logger = getLogger(__name__)


class MicroPythonVersion(MicroPythonSerialBase):
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

    def _wake_repl(self) -> None:
        """
        Invokes a wake-up sequence for the REPL (Read-Eval-Print Loop) interface by
        interacting with the serial connection.

        :return: None
        """
        self._ser.reset_input_buffer()
        self._ser.write(b'\r\n')
        sleep(0.2)

        self._ser.read_all()

    def _send_command(self, command: str, wait: float = 0.3) -> str:
        """
        Sends a command to the REPL interface and retrieves its output.

        :param command: The command to be sent to the REPL interface.
        :type command: str
        :param wait: The amount of time, in seconds.
        :type wait: float, optional
        :return: The output received from the REPL
        :rtype: str
        :raises RuntimeError: If the REPL interface is not connected or available.
        """
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("REPL not connected")

        self._ser.write(command.encode() + b'\r\n')
        sleep(wait)

        output = self._ser.read_all().decode(errors='ignore')
        debug(f"[DEBUG] command output: {output}")
        return output.strip()

    def get_version(self) -> str:
        """
        Extracts and returns the Python version from the command output.

        :param self: The instance of the class calling the method.
        :return: The extracted Python version as a string.
        :rtype: str
        """
        output = self._send_command("import sys; print(sys.version)")
        return self._extract_version(output)
