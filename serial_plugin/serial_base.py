from logging import getLogger, error, debug
from serial import Serial
from time import sleep
from types import TracebackType
from typing import Optional, Type
from config.application_configuration import SERIAL_RATE


logger = getLogger(__name__)


class SerialBase:
    """
    Manages a MicroPython serial connection and REPL modes.
    """

    def __init__(self, port: str, baudrate: int = SERIAL_RATE, timeout: int = 2):
        """
        Initializes a serial connection with the provided port settings.

        :param port: The serial port to connect to.
        :type port: str
        :param baudrate: The baud rate for the connection, which determines data transmission speed.
        :type baudrate: int, optional
        :param timeout: The timeout duration in seconds for the serial connection, default is 2.
        :type timeout: int, optional
        """
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._ser: Optional[Serial] = None

    def _connect(self) -> bool:
        """
        Opens a serial connection with the specified port and settings.

        :return: None
        """
        try:
            self._ser = Serial(self._port, self._baudrate, timeout=self._timeout)
            sleep(self._timeout)
            return True
        except Exception as err:
            error(f"[ERROR] connection missed: {err}")
            return False

    def _disconnect(self) -> None:
        """
        Closes the serial connection if it is currently open.

        :return: None
        """
        if self._ser and self._ser.is_open:
            self._ser.close()

    def send_repl_command(self, command: str, wait: float = 0.3) -> str:
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

    def enter_raw_repl(self) -> None:
        """
        Enter raw REPL mode on the connected device.

        :return: None
        """
        self._ser.write(b'\r\x03\x03')
        sleep(0.1)

        self._ser.write(b'\r\x01')
        sleep(0.1)

        self._ser.reset_input_buffer()

    def exit_raw_repl(self) -> None:
        """
        Exits raw REPL mode on the connected device.

        :return: None
        """
        self._ser.write(b'\r\x02')
        sleep(0.1)

    def __enter__(self) -> "SerialBase":
        """
        Provides context management for the MicroPythonTree, ensuring resources are
        properly opened and can be safely used within the context.

        :return: The instance of the class.
        :rtype: MicroPythonTreeBase
        """
        self._connect()
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        """
        Handles cleanup operations upon exiting a runtime context. Ensures proper
        closure of resources by invoking the `_close` method.

        :param exc_type: The type of the exception that caused the context to be exited.
        :type exc_type: Optional[Type[BaseException]]
        :param exc_val: The instance of the exception that caused the context to be exited.
        :type exc_val: Optional[BaseException]
        :param exc_tb: The traceback object associated with the exception, if any.
        :type exc_tb: Optional[TracebackType]
        :return: None
        """
        self._disconnect()
