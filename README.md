# pHorest: AI-Driven Precision Soil Sustainability

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [ML Algorithm & Training](#ml-algorithm--training)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [App and Script flags](#flags)
- [Browser Dashboard](#-browser-dashboard)

## Overview

<https://github.com/user-attachments/assets/58077799-b780-4939-9038-7cb840730b4b>

pHorest is a cyber-physical system designed to combat soil acidification and nutrient runoff—major environmental concerns in modern chemistry. By integrating IoT sensors with a Random Forest Machine Learning model, the system identifies the soil's chemical state and provides precise neutralization strategies through recommendations of crops and fertilizers.

## Features

- **Hardware Sensing:** Real-time pH, TDS, and Temperature monitoring via Arduino.
- **Cloud Rainfall Input:** 30-day rainfall is fetched online by location (Open-Meteo) for model input.
- **AI Inference:** Random Forest Classifier trained on agricultural datasets.
- **Smart Recommendations:** Crop prediction + fertilizer suggestion with pH-aware chemistry advice.

## ML Algorithm & Training

### Model used

- **Algorithm:** `RandomForestClassifier`
- **Input features (strict order):**
  `Nitrogen`, `phosphorus`, `potassium`, `temperature`, `humidity`, `ph`, `rainfall`
- **Target label:** `label` (crop name)
- **Train/test split:** `80/20` using `train_test_split(..., test_size=0.2, random_state=42)`
- **Model params used:** `n_estimators=100`, `random_state=42`
- **Saved model artifact:** `random forest/model/soil_model.pkl` (via `joblib.dump`)

### Training environment

- Trained in **Google Colab (Jupyter Notebook)**.
- Training code used: same as `random forest/training/train.ipynb` in this repo
- Dataset used: `Crop_recommendation.csv` (same schema as `random forest/dataset/Crop_recommendation.csv` in this repo).

### Using the trained model in this project

1. Place `random forest/model/soil_model.pkl` in the `random forest/model/` directory.
2. Ensure runtime feature order exactly matches training feature order.
3. Run `scripts/ser_script.py`, `scripts/sim_script.py`, or `app/app.py` to load the model and predict crops.

## Project Structure

- `app/app.py`: Browser dashboard (live readings + crop + fertilizer recommendation).
- `scripts/`: Contains utility scripts.
  - `ser_script.py`: Local Python bridge between Arduino and ML model.
  - `sim_script.py`: Simulation script for software-only demonstration.
- `random forest/`: Contains all machine learning related files.
  - `dataset/`: Contains the dataset.
    - `Crop_recommendation.csv`: The dataset used for training.
  - `model/`: Contains the trained model.
    - `soil_model.pkl`: Serialized Random Forest model.
  - `training/`: Contains the training notebook.
    - `train.ipynb`: Jupyter notebook for training the model.
- `setup.md`: Required hardware components and Arduino wiring map.
- `arduino/`: Directory containing Arduino firmware files for data acquisition.

## Setup

Before proceeding, make sure you have the physical setup ready. You can know more about it in the `setup.md` file in the repo

### Linux / macOS

1. Connect Arduino (for live mode), commonly `/dev/ttyACM0` or `/dev/ttyUSB0`.
2. Install dependencies:

   ```bash
   python3 -m pip install pandas joblib pyserial scikit-learn flask
   ```

3. Run:
   - Terminal:

      ```bash
      # Simulation
      python3 scripts/sim_script.py

      # Serial
      python3 scripts/ser_script.py --port=/dev/ttyACM0
      ```

    - Browser dashboard:

       ```bash
       # Simulation (default)
       python3 app/app.py

       # Serial (explicit port)
       python3 app/app.py --serial /dev/ttyACM0

       # Serial (auto-detect first available Arduino-like port)
       python3 app/app.py --serial
       ```

### Windows

1. Connect Arduino and note COM port (for example `COM3`).
2. Install dependencies:

   ```powershell
   py -m pip install pandas joblib pyserial scikit-learn flask
   ```

3. Run:
   - Terminal:

      ```powershell
      # Simulation
      py scripts/sim_script.py

      # Serial
      py scripts/ser_script.py --port=COM3
      ```

   - Browser dashboard:

      ```powershell
      # Simulation (default)
      py app/app.py

      # Serial
      py app/app.py --serial COM3
      ```

## Flags

### App flags (`app/app.py`)

- `app/app.py` → starts in **SIM** mode
- `app/app.py --sim` → explicitly starts in **SIM** mode
- `app/app.py --serial <PORT>` → starts in **SERIAL** mode
- `app/app.py --serial` → starts in **SERIAL** mode and auto-detects the port if `/dev/ttyACM0` is unavailable
- `--lock-mode` → hides the mode selector and prevents switching modes during runtime
- `--no-check` → skips strict pH input range validation (chemical status still shown)

**Usage examples:**

```bash
# Start in simulation mode
python3 app/app.py

# Start in serial mode with a specific port
python3 app/app.py --serial /dev/ttyACM0

# Start in serial mode with auto-port detection and locked UI
python3 app/app.py --serial --lock-mode
```

> the mode selector can be hidden by pressing 'm' in normal mode.

### Script Flags (`scripts/sim_script.py`, `scripts/ser_script.py`)

These scripts support optional flags to provide rainfall data:

- `--location <LAT> <LON>`: Fetches 30-day rainfall data from an online weather API (Open-Meteo) based on the provided latitude and longitude.
  - If the API call fails, the script will fall back to using the `--rainfall_data` value if provided, otherwise it will use a default value (100.0mm) and print a warning.
- `--rainfall_data <VALUE>`: Directly specifies the 30-day rainfall value in millimeters.
  - If both `--location` and `--rainfall_data` are provided, `--location` is attempted first. If it fails, `--rainfall_data` is used as a fallback.

**Usage examples:**

```bash
# Simulation with location-based rainfall
python3 scripts/sim_script.py --location 34.0522 -118.2437

# Simulation with direct rainfall data
python3 scripts/sim_script.py --rainfall_data 150.0

# Serial with location-based rainfall
python3 scripts/ser_script.py --port=/dev/ttyACM0 --location 34.0522 -118.2437

# Serial with direct rainfall data
python3 scripts/ser_script.py --port=/dev/ttyACM0 --rainfall_data 150.0
```

## 🌐 Browser Dashboard

Open `http://127.0.0.1:5000` after starting `app/app.py`.

- Set your coordinates using **Use Browser Location** or manual latitude/longitude.
- The app fetches **rolling 30-day rainfall (mm)** online and feeds it to the model.
- If location/weather fetch is unavailable, the app falls back to cached or default rainfall and shows the source status in UI.