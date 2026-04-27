import serial
import joblib
import pandas as pd
import time

# 1. Load the model you got from Colab
model = joblib.load("soil_model.pkl")

# 2. Connect to Arduino (Check your port: 'COM3' for Windows, '/dev/ttyACM0' for Linux)
# In Arch, it's likely /dev/ttyACM0 or /dev/ttyUSB0
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
time.sleep(2)  # Wait for connection

print("System Live. Reading Soil Chemistry...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").strip()
        data = line.split(",")

        if len(data) == 7:
            # Create DataFrame with the EXACT column names used in training
            cols = [
                "Nitrogen",
                "phosphorus",
                "potassium",
                "temperature",
                "humidity",
                "ph",
                "rainfall",
            ]
            current_readings = pd.DataFrame([data], columns=cols)

            # AI Prediction
            prediction = model.predict(current_readings)[0]

            print(f"--- Sensor Data: {line} ---")
            print(f"Recommended Crop: {prediction}")

            # Chemistry Logic
            ph_val = float(data[5])
            if ph_val < 5.5:
                print("ACTION: Soil is acidic. Suggest adding Lime (CaCO3).")
            elif ph_val > 7.5:
                print("ACTION: Soil is alkaline. Suggest adding organic mulch.")
