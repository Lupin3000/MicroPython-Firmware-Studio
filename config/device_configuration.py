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
