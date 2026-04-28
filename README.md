# pHorest: AI-Driven Precision Soil Sustainability

**A CHY1009/Environmental Science Project**

## 🌿 Overview

pHorest is a cyber-physical system designed to combat soil acidification and nutrient runoff—major environmental concerns in modern chemistry. By integrating IoT sensors with a Random Forest Machine Learning model, the system identifies the soil's chemical state and provides precise neutralization strategies.

## 🧪 Chemistry & EVS Focus

- **Acid-Base Equilibrium:** Monitoring soil pH to prevent aluminum toxicity.
- **Ion Exchange Capacity:** Using TDS as a proxy for nutrient (NPK) concentration.
- **Sustainability:** Reducing chemical waste by suggesting the "minimum necessary" fertilizer.

## 🚀 Features

- **Hardware Sensing:** Real-time pH, TDS, and Temperature monitoring via Arduino.
- **AI Inference:** Random Forest Classifier trained on agricultural datasets.
- **Smart Recommendations:** Crop prediction + fertilizer suggestion with pH-aware chemistry advice.

## 🤖 ML Algorithm & Training

### Model used

- **Algorithm:** `RandomForestClassifier`
- **Input features (strict order):**
  `Nitrogen`, `phosphorus`, `potassium`, `temperature`, `humidity`, `ph`, `rainfall`
- **Target label:** `label` (crop name)
- **Train/test split:** `80/20` using `train_test_split(..., test_size=0.2, random_state=42)`
- **Model params used:** `n_estimators=100`, `random_state=42`
- **Saved model artifact:** `soil_model.pkl` (via `joblib.dump`)

### Training environment

- Trained in **Google Colab (Jupyter Notebook)**.
- Dataset used: `Crop_recommendation.csv` (same schema as `dataset/Crop_recommendation.csv` in this repo).

### Training code (used in Colab)

```python
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

df = pd.read_csv('Crop_recommendation.csv')

X = df[['Nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, predictions) * 100:.2f}%")

joblib.dump(model, 'soil_model.pkl')
print("Model saved as soil_model.pkl")
```

### Using the trained model in this project

1. Place `soil_model.pkl` in the project root.
2. Ensure runtime feature order exactly matches training feature order.
3. Run `pscript.py`, `testscript.py`, or `app.py` to load the model and predict crops.

## 📂 Project Structure

- `pscript.py`: Local Python bridge between Arduino and ML model.
- `testscript.py`: Simulation script for software-only demonstration.
- `app.py`: Browser dashboard (live readings + crop + fertilizer recommendation).
- `arduino.cpp`: Arduino firmware for data acquisition.
- `soil_model.pkl`: Serialized Random Forest model.
- `dataset/Crop_recommendation.csv`: Dataset used for training.

## 🛠️ Setup

### Linux / macOS

1. Connect Arduino (commonly `/dev/ttyACM0` or `/dev/ttyUSB0`).
2. Install dependencies:

   ```bash
   python3 -m pip install pandas joblib pyserial scikit-learn flask
   ```

3. Run:
   - Hardware terminal mode:

     ```bash
     ARDUINO_PORT=/dev/ttyACM0 python3 pscript.py
     ```

   - Simulation terminal mode:

     ```bash
     python3 testscript.py
     ```

   - Browser dashboard (simulation):

     ```bash
     python3 app.py
     ```

   - Browser dashboard (live Arduino):

     ```bash
     SOURCE_MODE=serial ARDUINO_PORT=/dev/ttyACM0 python3 app.py
     ```

### Windows

1. Connect Arduino and note COM port (for example `COM3`).
2. Install dependencies:

   ```powershell
   py -m pip install pandas joblib pyserial scikit-learn flask
   ```

3. Run:
   - Hardware terminal mode:

     ```powershell
     set ARDUINO_PORT=COM3
     py pscript.py
     ```

   - Simulation terminal mode:

     ```powershell
     py testscript.py
     ```

   - Browser dashboard (simulation):

     ```powershell
     py app.py
     ```

   - Browser dashboard (live Arduino):

     ```powershell
     set SOURCE_MODE=serial
     set ARDUINO_PORT=COM3
     py app.py
     ```

## 🌐 Browser Dashboard

Open `http://127.0.0.1:5000` after starting `app.py`.
