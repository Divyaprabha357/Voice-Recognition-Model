# Voice-Recognition-Model
### A Wireless Voice-Controlled Computer Automation System Using ESP32, Python and Offline Speech Recognition

---

## Overview

The **Wi-Fi Voice Remote** is an embedded systems project that allows users to control various computer operations using voice commands.

The project uses an **ESP32, I2S microphone, OLED display, and Python-based application** to capture voice commands, recognize speech offline, and execute corresponding actions on a computer.

The ESP32 communicates with the Python application through a Wi-Fi TCP connection, while the Vosk speech recognition engine processes audio locally without requiring cloud-based speech recognition.

### Key Highlights

- Offline voice recognition using Vosk.
- Wireless communication using Wi-Fi and TCP sockets.
- Real-time audio streaming from ESP32 to a computer.
- Computer automation using Python and PyAutoGUI.
- OLED-based user interface and status monitoring.
- Physical button controls for easy operation.
- Support for volume, presentations, media, applications, and window management.

---

## Features

| Feature | Description |
|---|---|
| Voice Recognition | Offline speech recognition using Vosk |
| Wireless Communication | ESP32 communicates with PC over Wi-Fi |
| Audio Streaming | Real-time microphone audio transmission |
| Volume Control | Increase, decrease, mute and unmute |
| Application Control | Open Notepad, Calculator, File Explorer and Browser |
| Presentation Control | Navigate slides and control slideshow |
| Media Control | Play, pause, next track and previous track |
| Browser Control | Navigate home and close tabs |
| Window Management | Open File Explorer and close active windows |
| OLED Interface | Display connection status and help menus |
| Physical Controls | TALK, HELP, NEXT and SELECT buttons |
| LED Indicator | Indicates when voice listening is enabled |

---

## Hardware Requirements

| Component | Quantity |
|---|---:|
| ESP32 Development Board | 1 |
| I2S Microphone (INMP441 or compatible) | 1 |
| 0.96-inch OLED Display (SH1106, I2C) | 1 |
| Push Buttons | 4 |
| LED | 1 |
| Current-Limiting Resistor | 1 |
| Jumper Wires | As required |
| Breadboard or PCB | 1 |

---

## Pin Configuration

### OLED Display (I2C)

| OLED Pin | ESP32 GPIO |
|---|---|
| SDA | GPIO 8 |
| SCL | GPIO 9 |
| VCC | 3.3V |
| GND | GND |

### I2S Microphone

| Microphone Pin | ESP32 GPIO |
|---|---|
| SCK / BCLK | GPIO 15 |
| WS / LRCL | GPIO 16 |
| SD | GPIO 17 |
| VCC | 3.3V |
| GND | GND |

The microphone is configured to receive audio through the left I2S channel.

### Push Buttons

| Button | ESP32 GPIO |
|---|---|
| TALK | GPIO 4 |
| HELP | GPIO 5 |
| NEXT | GPIO 6 |
| SELECT | GPIO 7 |

All buttons use the ESP32 internal pull-up configuration (`INPUT_PULLUP`).

Connect one terminal of each button to its respective GPIO and the other terminal to GND.

### LED Indicator

| LED Terminal | ESP32 GPIO |
|---|---|
| Anode (+) | GPIO 18 (through a current-limiting resistor) |
| Cathode (-) | GND |

The LED turns ON when voice listening is enabled.

---

## Software Requirements

### ESP32 Development

- Arduino IDE
- ESP32 Board Package
- Adafruit GFX Library
- Adafruit SH110X Library
- ESP32 Wi-Fi Library
- ESP32 I2S Driver

### Python Application

- Windows 10/11
- Python 3.9 or later
- Vosk
- PyAutoGUI

### Python Dependencies

Install the required packages using:

```bash
pip install vosk pyautogui
