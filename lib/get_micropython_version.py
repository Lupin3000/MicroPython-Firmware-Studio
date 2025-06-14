from logging import getLogger, debug, error
from serial import Serial, SerialException
from time import sleep
from types import TracebackType
from typing import Optional, Type


logger = getLogger(__name__)


class MicroPythonREPL:
    """
    Handles communication with a MicroPython-enabled device over a serial connection.
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: int = 1):
        """
        Initializes a serial communication instance with specified port, baud rate, and
        timeout settings. Establishes the necessary attributes for managing the serial
        connection.

        :param port: The serial port to connect to as a string.
        :type port: str
        :param baudrate: The baud rate for the connection, defaulting to 115200.
        :type baudrate: int, optional
        :param timeout: The timeout for serial connection operations in seconds, defaulting to 1.
        :type timeout: int, optional
        """
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._ser = None

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

    def _connect(self) -> bool:
        """
        Attempts to establish a serial connection with the specified port and baud rate
        and initializes the connection by waking up the REPL (Read-Evaluate-Print Loop).

        :return: True if the connection was successfully established, False otherwise
        :rtype: bool
        """
        try:
            self._ser = Serial(self._port, self._baudrate, timeout=self._timeout)
            sleep(2)

            self._wake_repl()
            return True
        except SerialException as err:
            error(f"[ERROR] connection missed: {err}")
            return False

    def _disconnect(self) -> None:
        """
        Disconnects the serial connection if it is open. This method checks if the
        serial connection object exists and is open.

        :return: None
        """
        if self._ser and self._ser.is_open:
            self._ser.close()

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

    def __enter__(self) -> "MicroPythonREPL":
        """
        This method is part of a context manager implementation for the
        MicroPythonREPL class.

        :return: The instance of the class that represents the REPL.
        :rtype: MicroPythonREPL
        """
        self._connect()
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        """
        Handles the cleanup operations when exiting a context manager.

        :param exc_type: The exception type.
        :type exc_type: Optional[Type[BaseException]]
        :param exc_val: The exception instance.
        :type exc_val: Optional[BaseException]
        :param exc_tb: The traceback object associated with the exception.
        :type exc_tb: Optional[TracebackType]
        :return: None

        """
        self._disconnect()
