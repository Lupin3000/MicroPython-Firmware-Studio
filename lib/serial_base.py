from serial import Serial
from time import sleep
from logging import getLogger, error
from types import TracebackType
from typing import Optional, Type


logger = getLogger(__name__)


class MicroPythonSerialBase:
    """
    Manages a MicroPython serial connection.
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: int = 2):
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
            sleep(2)
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

    def __enter__(self) -> "MicroPythonSerialBase":
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
