# AgriSense: AI-Driven Precision Soil Sustainability
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
- **Smart Recommendations:** Automated chemical advice (e.g., Applying $CaCO_3$ for low pH).

## 📂 Project Structure
- `main_bridge.py`: Local Python bridge between Arduino and ML model.
- `virtual_demo.py`: Simulation script for software-only demonstration.
- `sensor_readings.cpp`: Arduino firmware for data acquisition.
- `soil_model.pkl`: Serialized Random Forest model.
- `Crop_recommendation.csv`: Dataset used for training.

## 🛠️ Setup
1. Connect Arduino to `/dev/ttyACM0`.
2. Install dependencies: `pip install pandas joblib pyserial scikit-learn`.
3. Run `python main_bridge.py`.
