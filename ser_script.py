import argparse
import os
import sys
import time

import joblib
import pandas as pd
try:
    import serial
    from serial import SerialException
except ModuleNotFoundError:
    print("Error: pyserial is not installed. Run: pip install pyserial")
    sys.exit(1)

COLS = [
    "Nitrogen",
    "phosphorus",
    "potassium",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]

try:
    model = joblib.load("soil_model.pkl")
except FileNotFoundError:
    print("Error: soil_model.pkl not found in project folder.")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Read Arduino serial data and run crop prediction.")
parser.add_argument(
    "--port",
    default=os.getenv("ARDUINO_PORT", "/dev/ttyACM0"),
    help="Arduino serial port (example: /dev/ttyACM0 or COM3)",
)
args = parser.parse_args()

port = args.port
try:
    ser = serial.Serial(port, 9600, timeout=1)
except SerialException as exc:
    print(f"Error: cannot open serial port {port}: {exc}")
    sys.exit(1)

time.sleep(2)
print(f"System Live. Reading Soil Chemistry from {port}...")

try:
    while True:
        if ser.in_waiting <= 0:
            continue

        line = ser.readline().decode("utf-8", errors="replace").strip()
        if not line:
            continue

        data = line.split(",")
        if len(data) != 7:
            print(f"Skipping malformed row (expected 7 values): {line}")
            continue

        try:
            numeric = [float(v) for v in data]
        except ValueError:
            print(f"Skipping non-numeric row: {line}")
            continue

        current_readings = pd.DataFrame([numeric], columns=COLS)
        prediction = model.predict(current_readings)[0]

        print(f"--- Sensor Data: {line} ---")
        print(f"Recommended Crop: {prediction}")

        ph_val = numeric[5]
        if ph_val < 5.5:
            print("ACTION: Soil is acidic. Suggest adding Lime (CaCO3).")
        elif ph_val > 7.5:
            print("ACTION: Soil is alkaline. Suggest adding organic mulch.")
        else:
            print("ACTION: pH is in balanced range.")
except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    ser.close()
