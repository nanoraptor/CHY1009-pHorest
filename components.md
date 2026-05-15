# Required Components and Arduino Connections

## Core components

| Component | Qty | Purpose |
|---|---:|---|
| Arduino Uno R3 (or compatible) | 1 | Main controller |
| Analog pH sensor module + probe | 1 | pH reading |
| Analog TDS sensor module + probe | 1 | TDS reading |
| DS18B20 waterproof temperature sensor | 1 | Water temperature (used for pH/TDS compensation) |
| 4.7kΩ resistor | 1 | DS18B20 data pull-up |
| DHT11 sensor module | 1 | Humidity input for model |
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
| DS18B20 | `VCC` | `5V` |
| DS18B20 | `GND` | `GND` |
| DS18B20 | `DATA` | `D3` |
| DHT11 | `VCC` | `5V` |
| DHT11 | `GND` | `GND` |
| DHT11 | `DATA` | `D2` |

## Notes

- Keep **all grounds common** (every module GND connected to Arduino GND).
- Add a **4.7kΩ pull-up resistor** between DS18B20 `DATA` and `VCC`.
- `temp` in serial output is **DHT11 temperature** (used by Web UI/model input).
- `humidity` in serial output is from **DHT11**.
- DS18B20 water temperature is used internally for pH/TDS compensation.
- Serial output format from `arduino_full.ino`: `ph,tdsPpm,temp,humidity`.

## Additional Stuff to buy and important notes

- While the above listed items are enough for the base project. You might have to buy pH buffer solutions and to calibrate the pH electrode (as most of the electrodes are non-calibrated). A 1000 ppm solution reference to calibrate the tds sensor as well
- Consider having distilled water and a standard solution with known ppm to calibrate the tds sensor (in-case it is not calibrated). Distilled water is also needed to clean the pH sensor between every soil sample test.
- The soil solutions should be made with distilled water. 1:2 ratio of soil and water. The electrode will get damaged if it is dipped in a solution which contains lot of solid sand particles. Let the slurry/solution settle or filter out the solution.
- A pH electrode stand will be helpful in handling the pH electrode. The bulb of the pH electrode should not touch the bottom of the container, as it will break the electrode. You can also use microphone stands with minor tweaks as you can see in the overview video.
- the DS18B20 probe is not needed if the tds and pH sensors have temperature compensation builtin. But those features are only reserved to high end probes which are not so cost effective.
