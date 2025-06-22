from logging import getLogger, debug, error
from threading import Thread
from subprocess import Popen, PIPE
from typing import List, Callable, Optional


logger = getLogger(__name__)


class CommandRunner:
    """
    Represents a utility for running esptool commands in a subprocess with support for threaded execution
    and optional callback handling for output, errors, and completion.
    """
    def __init__(self,
                 on_output: Optional[Callable[[str], None]] = None,
                 on_error: Optional[Callable[[str], None]] = None,
                 on_complete: Optional[Callable[[], None]] = None):
        """
        Initializes an object with optional callbacks for output, error, and completion handling.

        :param on_output: A callback function to handle output from the command.
        :type on_output: Optional[Callable[[str], None]]
        :param on_error: A callback function to handle error output from the command.
        :type on_error: Optional[Callable[[str], None]]
        :param on_complete: A callback function to handle completion of the command.
        :type on_complete: Optional[Callable[[], None]]
        """
        self._on_output = on_output
        self._on_error = on_error
        self._on_complete = on_complete

    def run_threaded_command(self, command: List[str]) -> None:
        """
        Starts a thread to execute a command.

        :param command: The command to be executed.
        :type command: List[str]
        :return: None
        """
        thread = Thread(target=self._execute_command, args=(command,))
        thread.start()

    def _execute_command(self, command: List[str]) -> None:
        """
        Executes a command in a subprocess and handles its output.

        :param command: The command to be executed.
        :type command: List[str]
        :return: None
        """
        debug(f'running esptool command: {command}')
        process = Popen(command, stdout=PIPE, stderr=PIPE, text=True)

        for line in iter(process.stdout.readline, ''):
            stripped = line.strip()

            if self._on_output:
                self._on_output(stripped)

        process.wait()

        if process.returncode != 0:
            error_output = process.stderr.read().strip()
            error(f'esptool command failed: {error_output}')

            if self._on_error:
                self._on_error(error_output)

        if self._on_complete:
            self._on_complete()
