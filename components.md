# Required Components and Arduino Connections

## Core components

| Component | Qty | Purpose |
|---|---:|---|
| Arduino Uno R3 (or compatible) | 1 | Main controller |
| Analog pH sensor module + probe | 1 | pH reading |
| Analog TDS sensor module + probe | 1 | TDS reading |
| DHT11 sensor module | 1 | Temperature + humidity |
| 16x2 I2C LCD display | 1 | Local display output |
| Breadboard | 1 | Wiring/power distribution |
| Jumper wires (M-M / M-F) | As needed | Connections |
| USB cable for Arduino | 1 | Power + serial data |

## Arduino wiring (for `arduino/arduino_full/arduino_full.ino`)

| Module | Module pin | Arduino pin |
|---|---|---|
| pH sensor | `VCC` | `5V` |
| pH sensor | `GND` | `GND` |
| pH sensor | `AO` / `PO` / `SIG` | `A0` |
| TDS sensor | `VCC` | `5V` |
| TDS sensor | `GND` | `GND` |
| TDS sensor | `AO` | `A1` |
| DHT11 | `VCC` | `5V` |
| DHT11 | `GND` | `GND` |
| DHT11 | `DATA` | `D2` |
| I2C LCD | `VCC` | `5V` |
| I2C LCD | `GND` | `GND` |
| I2C LCD | `SDA` | `A4` (Uno) |
| I2C LCD | `SCL` | `A5` (Uno) |

## Notes

- Keep **all grounds common** (every module GND connected to Arduino GND).
- LCD I2C address in code is `0x27` (some modules use `0x3F`).
- Serial output format from current sketch: `phRaw,tdsRaw,temp,humidity`.
