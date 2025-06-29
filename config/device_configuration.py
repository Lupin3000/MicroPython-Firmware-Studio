BAUDRATE_OPTIONS: list = ["9600", "57600", "74880", "115200", "23400", "460800", "921600", "1500000"]
FLASH_MODE_OPTIONS: list = ["keep", "qio", "qout", "dio", "dout"]
FLASH_FREQUENCY_OPTIONS: list = ["keep", "40m", "26m", "20m", "80m"]
FLASH_SIZE_OPTIONS: list = ["keep", "detect", "1MB", "2MB", "4MB", "8MB", "16MB"]

DEFAULT_URL: str = "https://micropython.org/download/"

CONFIGURED_DEVICES: dict = {
    "ESP8266": {
        "name": "esp8266",
        "write_flash": 0,
        "url": "https://micropython.org/download/?port=esp8266"
    },
    "ESP32": {
        "name": "esp32",
        "write_flash": 0x1000,
        "url": "https://micropython.org/download/?mcu=esp32"
    },
    "ESP32-S2": {
        "name": "esp32s2",
        "write_flash": 0x1000,
        "url": "https://micropython.org/download/?mcu=esp32s2"
    },
    "ESP32-S3": {
        "name": "esp32s3",
        "write_flash": 0,
        "url": "https://micropython.org/download/?mcu=esp32s3"
    },
    "ESP32-C3": {
        "name": "esp32c3",
        "write_flash": 0,
        "url": "https://micropython.org/download/?mcu=esp32c3"
    },
    "ESP32-C6": {
        "name": "esp32c6",
        "write_flash": 0,
        "url": "https://micropython.org/download/?mcu=esp32c6"
    },
    "Lilygo TTGO LoRa32": {
        "name": "esp32",
        "write_flash": 0x1000,
        "url": "https://micropython.org/download/?vendor=LILYGO"
    }
}
