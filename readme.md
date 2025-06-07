# MicroPython Firmware Studio

![application_preview.jpg](img/application_preview.jpg)

The **MicroPython Firmware Studio** is a user-friendly application designed for the management and configuration of ESP microcontrollers. This software enables efficient firmware development and seamless flashing of MicroPython firmware onto ESP chips.

## Important

The owner of this project assumes no responsibility for any damage, issues, or legal consequences resulting from the use of this software. Use it at your own risk and ensure compliance with all applicable laws and regulations.

## Supported Devices

Supported devices include ESP chips in the variants ESP32, ESP32-S2, ESP32-S3, ESP32-C3, and ESP32-C6, with specific flash sector configurations.

## Installation

### Prerequisite

The latest [VCP driver](https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads) needs to be installed.

### Minimum requirements

The code is written and tested with the following requirements:

| OS            | Python                                                                                                                        |
|---------------|-------------------------------------------------------------------------------------------------------------------------------|
| macOS Sequoia | [![Static](https://img.shields.io/badge/python-==3.12.2-green)](https://python.org)                                           | 
| macOS Sequoia | [![Static](https://img.shields.io/badge/esptool-==4.8.1-green)](https://docs.espressif.com/projects/esptool/en/latest/esp32/) |
| macOS Sequoia | [![Static](https://img.shields.io/badge/customtkinter-==5.2.2-green)](https://customtkinter.tomschimansky.com)                |

### Quick installation

```shell
# clone repository
$ git clone https://github.com/Lupin3000/MicroPython-Firmware-Studio.git

# change into cloned root directory
$ cd MicroPython-Firmware-Studio/

# create Python virtualenv (optional but recommended)
$ python3 -m venv venv

# activate Python virtualenv
$ source venv/bin/activate

# update pip (optional)
(venv) $ pip3 install -U pip

# install required dependencies
(venv) $ pip3 install -r requirements.txt

# show packages (optional)
(venv) $ pip3 freeze
```

## Usage

```shell
# run application
(venv) $ python3 main.py
```
