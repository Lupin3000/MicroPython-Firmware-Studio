CONFIGURED_DEVICES: dict = {
    "ESP32": {
        "name": "esp32",
        "write_flash": 0x1000,
        "url": "https://micropython.org/download/ESP32_GENERIC/"
    },
    "ESP32-S2": {
        "name": "esp32s2",
        "write_flash": 0x1000,
        "url": "https://micropython.org/download/ESP32_GENERIC_S2/"
    },
    "ESP32-S3": {
        "name": "esp32s3",
        "write_flash": 0,
        "url": "https://micropython.org/download/ESP32_GENERIC_S3/"
    },
    "ESP32-C3": {
        "name": "esp32c3",
        "write_flash": 0,
        "url": "https://micropython.org/download/ESP32_GENERIC_C3/"
    },
    "ESP32-C6": {
        "name": "esp32c6",
        "write_flash": 0,
        "url": "https://micropython.org/download/ESP32_GENERIC_C6/"
    }
}
OPERATING_SYSTEM: dict = {
    "Darwin": {
        "device_path": "/dev/cu.usb*",
        "search_path": "~/Downloads"
    },
    "Linux": {
        "device_path": "/dev/ttyUSB*",
        "search_path": "~/Downloads"
    }
}
