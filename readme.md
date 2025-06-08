# MicroPython Firmware Studio

![License](https://img.shields.io/github/license/Lupin3000/MicroPython-Firmware-Studio)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)
![Last Commit](https://img.shields.io/github/last-commit/Lupin3000/MicroPython-Firmware-Studio)
![Repo Size](https://img.shields.io/github/repo-size/Lupin3000/MicroPython-Firmware-Studio)

## Preview

![Screenshot](img/application_preview.jpg)

The **MicroPython Firmware Studio** is a user-friendly application designed for the management and configuration of ESP microcontrollers. This software enables efficient firmware development and seamless flashing of MicroPython firmware onto ESP chips.

## Important

**MicroPython Firmware Studio is provided without any guarantee.** Use it at your own risk. The developer assumes no liability for any damage or legal consequences resulting from using the software. Please ensure compliance with all applicable laws and regulations when using this tool.

## Supported Devices

Supported devices include ESP chips in the variants ESP32, ESP32-S2, ESP32-S3, ESP32-C3, and ESP32-C6, with specific flash sector configurations.

## Installation

### Prerequisite

> To communicate with microcontrollers via USB, you may need to install additional drivers on your system.

**macOS**

Install the [Silicon Labs CP210x VCP drivers](https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads) or the corresponding drivers provided by your microcontroller manufacturer.

**Linux**

Linux typically does not require VCP drivers, as they are built into the kernel. However, you need to take a few steps to enable proper communication.

In Linux systems you need to execute the following commands (_e.q. as root_):

```shell
# update system
$ apt update && apt upgrade -y

# install required Python modules
$ apt install -y python3-pip python3-venv python3-tk

# enable dialout permissions
$ usermod -aG dialout <USER>

# verify user group (optional)
$ groups <USER>
```

**Windows**

Also, install the [Silicon Labs CP210x VCP drivers](https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads).

If you use Python virtualenv, execute as the Administrator the following command in cmd:

```shell
# Allows all scripts to run, including unsigned or downloaded ones (unsecure)
> Set-ExecutionPolicy Unrestricted -Force
```

It is very unsecure! Additionally, you could do the same as a user:

```shell
# Allows all scripts to run, including unsigned or downloaded ones (temporary)
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Minimum requirements

The code is written and tested with the following requirements:

| OS            | Python Module                                                                                                                 |
|---------------|-------------------------------------------------------------------------------------------------------------------------------|
| macOS + Linux | [![Static](https://img.shields.io/badge/python-==3.12.2-green)](https://python.org)                                           | 
| macOS + Linux | [![Static](https://img.shields.io/badge/esptool-==4.8.1-green)](https://docs.espressif.com/projects/esptool/en/latest/esp32/) |
| macOS + Linux | [![Static](https://img.shields.io/badge/customtkinter-==5.2.2-green)](https://customtkinter.tomschimansky.com)                |
| macOS + Linux | [![Static](https://img.shields.io/badge/pillow-==11.2.1-green)](https://python-pillow.github.io)                              |

### Quick installation

> Clone the repository from GitHub, create a virtual Python environment, and install all required dependencies.

```shell
# clone repository
$ git clone https://github.com/Lupin3000/MicroPython-Firmware-Studio.git

# change into cloned root directory
$ cd MicroPython-Firmware-Studio/

# create Python virtualenv (optional but recommended)
$ python3 -m venv .venv

# activate Python virtualenv (macOS & Linux)
$ source venv/bin/activate

# activate Python virtualenv (Windows)
$ .\.venv\Scripts\activate

# update pip (optional)
(.venv) $ pip3 install -U pip

# install required dependencies
(.venv) $ pip3 install -r requirements.txt

# show packages (optional)
(.venv) $ pip3 freeze
```

## Usage

> Start the application using the command in your terminal within the configured Python environment.

```shell
# run application
(.venv) $ python3 main.py
```

After MicroPython firmware flashing was successful you can use `rshell` to connect.

```shell
# connect to device
(.venv) $ rshell -p <PORT>
```
