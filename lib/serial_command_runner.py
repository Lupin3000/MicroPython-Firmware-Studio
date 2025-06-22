from logging import getLogger, debug
from threading import Thread
from typing import Callable
from lib.serial_get_micropython_version import MicroPythonVersion
from lib.serial_get_file_structure import MicroPythonFileStructure


logger = getLogger(__name__)


class SerialCommandRunner:

    @staticmethod
    def _run_in_thread(worker: Callable[[], str], callback: Callable[[str], None]) -> None:
        """
        Runs a given worker function in a separate thread and executes a callback
        function with the worker's result.

        :param worker: The function to be executed in a separate thread.
        :type worker: Callable[[], str]
        :param callback: The function to be executed with the worker's result.
        :type callback: Callable[[str], None]
        :return: None
        """
        def task() -> None:
            try:
                result = worker()
            except Exception as e:
                result = f"[ERROR] {str(e)}"

            callback(result)
            debug(f"[DEBUG] callback result: {result}")

        thread = Thread(target=task, daemon=True)
        thread.start()

    @staticmethod
    def _get_version(port: str) -> str:
        """
        Fetches and returns the version of MicroPython from a given port.

        :param port: The serial port to connect to.
        :type port: str
        :return: The version of MicroPython as a string.
        :rtype: str
        """
        with MicroPythonVersion(port=port) as version_fetcher:
            return version_fetcher.get_version()

    @staticmethod
    def _get_structure(port: str) -> str:
        """
        Fetches and returns the file structure from a given port.

        :param port: The serial port to connect to.
        :type port: str
        :return: The file structure as a string.
        :rtype: str
        """
        with MicroPythonFileStructure(port=port) as structure_fetcher:
            return structure_fetcher.get_tree()

    def get_version(self, port: str, callback: Callable[[str], None]) -> None:
        """
        Executes a function to retrieve version information for a given port and
        invokes the provided callback with the result.

        :param port: The serial port to connect to.
        :type port: str
        :param callback: The function to be executed with the result.
        :type callback: Callable[[str], None]
        :return: None
        """
        self._run_in_thread(lambda: self._get_version(port), callback)

    def get_structure(self, port: str, callback: Callable[[str], None]) -> None:
        """
        Executes a function to retrieve the file structure for a given port and
        invokes the provided callback with the result.

        :param port: The serial port to connect to.
        :type port: str
        :param callback: The function to be executed with the result.
        :type callback: Callable[[str], None]
        :return: None
        """
        self._run_in_thread(lambda: self._get_structure(port), callback)
