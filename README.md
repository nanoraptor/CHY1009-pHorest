# AI-Enhanced Soil Health & Sustainability Monitor (CHY1009)

## 🎯 Project Goal
To develop a **Cyber-Physical System** that utilizes Machine Learning to predict soil health and suggest precise chemical interventions (fertilizers/neutralizers). The objective is to maintain **Acid-Base Equilibrium** and prevent environmental degradation, such as soil acidification and nutrient runoff, through precision agriculture.

## 🛠️ Tech Stack & File Structure
- **AI Model:** `soil_model.pkl` (Random Forest Classifier trained on `Crop_recommendation.csv`).
- **Hardware:** `sensor_readings.cpp` (Arduino code for pH, TDS, and environmental sensing).
- **Bridge:** `main_bridge.py` (Real-time Serial-to-ML inference script).
- **Testing:** `virtual_demo.py` (Simulation script for logic verification without hardware).

## 🤖 Instructions for AI Agents (Copilot/Gemini-CLI)
When assisting with this project, adhere to the following technical constraints:

### 1. Data Schema
The model expects a 7-feature input vector in this **exact** order:
`['Nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']`

### 2. Inference Logic
- **Input Source:** Raw values from Arduino Serial (CSV format).
- **Processing:** Parse string -> Create Pandas DataFrame -> `model.predict()`.
- **Sustainability Guardrails:** - If `ph < 5.5`: Recommend **CaCO3 (Lime)**.
    - If `ph > 7.5`: Recommend **Organic Matter/Sulfur**.
    - Goal: Guide the user toward the "Ideal Chemical State" for the predicted crop.

### 3. Hardware Interfacing
- **Library:** `pyserial`.
- **Baud Rate:** `9600`.
- **Target Port:** `/dev/ttyACM0` or `/dev/ttyUSB0` (Arch Linux default).

## 🧪 Chemistry Focus (CHY1009 / EVS)
This project demonstrates **Ion Exchange Capacity** and **Buffer Systems** in soil. It replaces "Broadcasting" (wasteful chemical application) with "Precision" (sustainable application) by treating AI as a real-time chemical analyst.
