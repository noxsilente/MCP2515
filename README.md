# MicroPython MCP2515 Minimal Driver

A lightweight, minimal MicroPython driver for the **MCP2515 CAN-Bus controller**, optimized for Raspberry Pi Pico and designed for OBD-II vehicle data acquisition (tested on a 2008 Seat Ibiza).

---

## Features

- **Lightweight & Efficient**: Direct register manipulation via SPI without heavy dependencies.
- **Full Duplex Operations**: Supports both sending CAN messages (e.g., broadcasting OBD-II PID requests) and polling/reading incoming messages from RX buffers.
- **OBD-II Ready**: Tailored for standard 11-bit CAN IDs and standard diagnostic requests.

---

## Hardware Connections (Raspberry Pi Pico & MCP2515)

| MCP2515 Pin | Raspberry Pi Pico Pin (SPI0) | Description |
| :--- | :--- | :--- |
| **VCC** | 3.3V | Power Supply |
| **GND** | GND | Ground |
| **SCK** | GP2 (SPI0 SCK) | SPI Clock |
| **SO (MISO)** | GP4 (SPI0 RX) | SPI Master In Slave Out |
| **SI (MOSI)** | GP3 (SPI0 TX) | SPI Master Out Slave In |
| **CS** | GP5 (User Defined) | Chip Select |
| **INT** | *Optional / Unconnected* | Interrupt Pin |

---

## Code Example

Here is a quick example of how to initialize the module, send an OBD-II request for engine RPM (`0x0C`), and read the incoming response:

```python
from machine import Pin, SPI
from mcp2515 import MCP2515
import time

# Initialize SPI0 and CS pin
spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(2), mosi=Pin(3), miso=Pin(4))
cs_pin = Pin(5, Pin.OUT)

# Instantiate the MCP2515 driver
can_mcp = MCP2515(spi, cs_pin)

# Reset the controller before setup
can_mcp.reset()

# Example: Request Engine RPM (PID 0x0C) via Broadcast ID 0x7DF
obd_request = bytes([0x02, 0x01, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00])
can_mcp.send_message(0x7DF, obd_request)

# Main loop to check and read incoming responses
while True:
    msg = can_mcp.read_message()
    if msg is not None:
        msg_id, msg_data = msg
        print(f"ID: hex(msg_id) | Data: {msg_data}")
    time.sleep_ms(10)
