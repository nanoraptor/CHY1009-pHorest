# pHorest: AI-Driven Precision Soil Sustainability
**A CHY1009/Environmental Science Project**

## 🌿 Overview
AgriSense is a cyber-physical system designed to combat soil acidification and nutrient runoff—major environmental concerns in modern chemistry. By integrating IoT sensors with a Random Forest Machine Learning model, the system identifies the soil's chemical state and provides precise neutralization strategies.

## 🧪 Chemistry & EVS Focus
- **Acid-Base Equilibrium:** Monitoring soil pH to prevent aluminum toxicity.
- **Ion Exchange Capacity:** Using TDS as a proxy for nutrient (NPK) concentration.
- **Sustainability:** Reducing chemical waste by suggesting the "minimum necessary" fertilizer.

## 🚀 Features
- **Hardware Sensing:** Real-time pH, TDS, and Temperature monitoring via Arduino.
- **AI Inference:** Random Forest Classifier trained on agricultural datasets.
- **Smart Recommendations:** Crop prediction + fertilizer suggestion with pH-aware chemistry advice.

## 📂 Project Structure
- `pscript.py`: Local Python bridge between Arduino and ML model.
- `testscript.py`: Simulation script for software-only demonstration.
- `app.py`: Browser dashboard (live readings + crop + fertilizer recommendation).
- `arduino.cpp`: Arduino firmware for data acquisition.
- `soil_model.pkl`: Serialized Random Forest model.
- `dataset/Crop_recommendation.csv`: Dataset used for training.

## 🛠️ Setup
1. Connect Arduino to `/dev/ttyACM0`.
2. Install dependencies: `pip install pandas joblib pyserial scikit-learn flask`.
3. Run:
   - `python pscript.py` (hardware mode in terminal), or
   - `python testscript.py` (simulation mode in terminal), or
   - `python app.py` (browser dashboard in simulation mode).

## 🌐 Browser Dashboard
1. Start dashboard: `python app.py`
2. Open: `http://127.0.0.1:5000`

For Arduino live mode:
```bash
SOURCE_MODE=serial ARDUINO_PORT=/dev/ttyACM0 python app.py
```
