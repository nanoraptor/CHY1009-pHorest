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
- Serial output format from `arduino_full.ino`: `ph,tdsPpm,temp,humidity`.

## Additional Stuff to buy and important notes

- While the above listed items are enough for the base project. You might have to buy pH buffer solutions and to calibrate the pH electrode (as most of the electrodes are non-calibrated). A 1000 ppm solution reference to calibrate the tds sensor as well
- Currently this project assumes the temperature to be room temperature and does not take into account the changes in ph and tds value with temperature. Using the temperature data from DHT11 is unreliable as it will only report ambient temperature not the solution temperature. It's better to buy a water temperature sensor than DHT11 sensor. (If the tds and pH sensor have inbuilt temperature sensors then this point can be neglected).
- Consider having distilled water and a standard solution with known ppm to calibrate the tds sensor (in-case it is not calibrated). Distilled water is also needed to clean the pH sensor between every soil sample test.
- The soil solutions should be made with distilled water. 1:2 ratio of soil and water. The electrode will get damaged if it is dipped in a solution which contains lot of solid sand particles. Let the slurry/solution settle or filter out the solution.
- A pH electrode stand will be helpful in handling the pH electrode. The bulb of the pH electrode should not touch the bottom of the container, as it will break the electrode. You can also use microphone stands with minor tweaks as you can see in the overview video.
- The LCD is not very useful as all the information is already displayed on the pc/laptop. So you can drop this component if you want.
