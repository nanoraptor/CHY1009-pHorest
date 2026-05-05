# AI CONTEXT MANIFEST

**Project Name:** AgriSense AI
**Target Domain:** Environmental Chemistry (CHY1009)

## 🤖 Context for LLM

This project implements a **Random Forest Classifier** to solve agricultural sustainability issues. When assisting with code or debugging, follow these parameters:

### 1. Model Signature

- **Input Features:** `Nitrogen`, `phosphorus`, `potassium`, `temperature`, `humidity`, `ph`, `rainfall`.
- **Feature Order:** Order is strict; do not reorder the vector before `model.predict()`.
- **Preprocessing:** Inputs are numerical. DataFrames are preferred over raw arrays for consistency with the `.pkl` metadata.

### 2. Physical Constants & Mapping

- **Serial Port:** `/dev/ttyACM0` (Arch Linux default).
- **Baud Rate:** `9600`.
- **Data Format:** Arduino sends a 7-value CSV string.

### 3. Business Logic (Sustainability)

- **Primary Objective:** Suggest chemical additives based on `ph` deviations.
- **Thresholds:**
  - `ph < 5.5` -> Trigger Acidification Alert -> Suggest Lime ($CaCO_3$).
  - `ph > 7.5` -> Trigger Alkalinity Alert -> Suggest Organic Matter.
- **Model File:** `soil_model.pkl` must be loaded via `joblib`.

### 4. Code Generation Preferences

- Use `pyserial` for I/O.
- Implement robust `try-except` blocks for Serial port disconnection.
- Use `pandas` for data manipulation to match the training pipeline.
