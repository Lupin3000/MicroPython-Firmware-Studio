OPERATING_SYSTEM: dict = {
    "Darwin": {
        "device_path": "/dev/cu.usb*",
        "search_path": "~/Downloads"
    },
    "Linux": {
        "device_path": "/dev/ttyUSB*",
        "search_path": "~/Downloads"
    },
    "Windows": {
        "device_path": "COM*",
        "search_path": "C:/Users/"
    }
}
