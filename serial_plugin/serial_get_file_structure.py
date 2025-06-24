from logging import getLogger, debug
from time import time
from serial_plugin.serial_base import SerialBase


logger = getLogger(__name__)


class FileStructure(SerialBase):
    """
    Represents a utility for interacting with a MicroPython device to fetch and manage
    a tree structure of the file system over a serial connection.

    :ivar _TREE_CODE: The Python code to generate the tree structure.
    """
    _TREE_CODE = (
        "import os\n"
        "def tree(path='', prefix=''):\n"
        " try:\n"
        "  files = os.listdir(path) if path else os.listdir()\n"
        " except: files = []\n"
        " files.sort()\n"
        " for idx, file in enumerate(files):\n"
        "  full_path = path + '/' + file if path else file\n"
        "  connector = '└── ' if idx == len(files) - 1 else '├── '\n"
        "  print(prefix + connector + file)\n"
        "  try:\n"
        "   mode = os.stat(full_path)[0]\n"
        "   if mode & 0x4000:\n"
        "    extension = '    ' if idx == len(files) - 1 else '│   '\n"
        "    tree(full_path, prefix + extension)\n"
        "  except Exception: pass\n"
        "tree('')\n"
    )

    def get_tree(self) -> str:
        """
        Retrieves the current state of the tree structure by communicating with
        a connected serial device. The method sends a specific command to the
        device, waits for the response, and processes the output to extract
        the tree structure information.

        :return: The tree structure information.
        :rtype: str
        """
        self.enter_raw_repl()
        self._ser.write(self._TREE_CODE.encode('utf-8') + b'\x04')
        output = b''
        start = time()

        while True:
            if time() - start > 10:
                output = b'[ERROR] Timeout'
                break

            data = self._ser.read(1)
            if not data:
                break
            output += data
            if output.endswith(b'\x04>'):
                break

        self.exit_raw_repl()
        out = output.decode(errors="ignore")
        debug(f"[DEBUG] tree output: {out}")

        if 'OK' in out:
            tree_output = out.split('OK', 1)[1].rsplit('\x04', 1)[0].strip()
        else:
            tree_output = out
        return tree_output.replace('\x04', '').rstrip()
