import os
import random
import sys
import time

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template_string

COLS = [
    "Nitrogen",
    "phosphorus",
    "potassium",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>pHorest Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; }
    .wrap { max-width:960px; margin:24px auto; padding:0 16px; }
    .card { background:#1e293b; border-radius:12px; padding:16px; margin-bottom:16px; }
    h1 { margin:0 0 8px 0; font-size:28px; }
    .muted { color:#94a3b8; }
    .grid { display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:12px; }
    .tile { background:#0b1220; border-radius:10px; padding:12px; }
    .label { color:#94a3b8; font-size:12px; text-transform:uppercase; letter-spacing:0.06em; }
    .value { font-size:24px; margin-top:8px; font-weight:700; }
    .ok { color:#22c55e; } .warn { color:#f59e0b; } .bad { color:#ef4444; }
    .status { font-size:20px; font-weight:700; }
    code { background:#0b1220; padding:2px 6px; border-radius:6px; }
    @media (max-width: 720px) { .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>pHorest Dashboard</h1>
      <div class="muted">Live soil chemistry + crop and fertilizer recommendation</div>
      <div class="muted">Mode: <code id="mode">loading...</code></div>
    </div>

    <div class="card">
      <div class="grid">
        <div class="tile"><div class="label">pH</div><div class="value" id="ph">-</div></div>
        <div class="tile"><div class="label">TDS (ppm)</div><div class="value" id="tds">-</div></div>
        <div class="tile"><div class="label">Recommended Crop</div><div class="value" id="crop">-</div></div>
        <div class="tile"><div class="label">Recommended Fertilizer</div><div class="value" id="fertilizer">-</div></div>
      </div>
    </div>

    <div class="card">
      <div class="label">Chemical Status</div>
      <div class="status" id="status">Waiting for first reading...</div>
      <div class="muted" id="action"></div>
      <div class="muted" id="fertilizerReason"></div>
    </div>

    <div class="card">
      <div class="label">Raw sensor packet</div>
      <div id="raw" class="muted">-</div>
      <div class="muted" style="margin-top:8px;">Last updated: <span id="updated">-</span></div>
    </div>
  </div>

  <script>
    async function refresh() {
      try {
        const res = await fetch('/api/reading', { cache: 'no-store' });
        const data = await res.json();
        if (!data.ok) {
          document.getElementById('status').textContent = data.error;
          document.getElementById('status').className = 'status bad';
          return;
        }

        document.getElementById('mode').textContent = data.mode;
        document.getElementById('ph').textContent = data.ph.toFixed(2);
        document.getElementById('tds').textContent = Math.round(data.tds);
        document.getElementById('crop').textContent = String(data.prediction).toUpperCase();
        document.getElementById('fertilizer').textContent = data.fertilizer;
        document.getElementById('raw').textContent = data.raw;
        document.getElementById('updated').textContent = data.timestamp;

        const statusEl = document.getElementById('status');
        const actionEl = document.getElementById('action');
        const fertilizerReasonEl = document.getElementById('fertilizerReason');
        statusEl.textContent = data.status;
        actionEl.textContent = data.action;
        fertilizerReasonEl.textContent = data.fertilizer_reason;
        statusEl.className = 'status ' + data.level;
      } catch (e) {
        const statusEl = document.getElementById('status');
        statusEl.textContent = 'Dashboard fetch error';
        statusEl.className = 'status bad';
      }
    }
    refresh();
    setInterval(refresh, 2000);
  </script>
</body>
</html>
"""


def evaluate_ph(ph_val: float):
    if ph_val < 5.5:
        return (
            "Acidic soil detected",
            "Apply Lime (CaCO3) to neutralize acidity.",
            "bad",
        )
    if ph_val > 7.5:
        return (
            "Alkaline soil detected",
            "Add organic matter/mulch to improve soil balance.",
            "warn",
        )
    return (
        "Chemical equilibrium maintained",
        "pH is in the balanced range.",
        "ok",
    )


def parse_serial_line(line: str):
    parts = line.strip().split(",")
    if len(parts) != 7:
        raise ValueError("Expected 7 comma-separated values")
    numeric = [float(x) for x in parts]
    return numeric


def recommend_fertilizer(crop: str, n: float, p: float, k: float, ph_val: float):
    crop_key = str(crop).strip().lower()
    crop_map = {
        "rice": "Urea + DAP",
        "maize": "NPK 20-20-0",
        "banana": "NPK 10-26-26",
        "apple": "NPK 12-12-17",
        "cotton": "NPK 20-10-10",
        "coffee": "NPK 17-17-17",
        "grapes": "NPK 19-19-19",
        "mango": "NPK 10-10-10",
        "chickpea": "SSP + MOP",
        "lentil": "SSP",
        "kidneybeans": "SSP + MOP",
    }
    fertilizer = crop_map.get(crop_key, "NPK 19-19-19")
    reasons = [f"Crop support for {crop_key or 'predicted crop'}."]

    if n < 50:
        fertilizer = "Urea (Nitrogen boost)"
        reasons.append("Nitrogen is low.")
    elif p < 30:
        fertilizer = "SSP / DAP (Phosphorus boost)"
        reasons.append("Phosphorus is low.")
    elif k < 30:
        fertilizer = "MOP (Potassium boost)"
        reasons.append("Potassium is low.")

    if ph_val < 5.5:
        fertilizer = f"{fertilizer} + Agricultural Lime"
        reasons.append("Soil is acidic, so lime is recommended.")
    elif ph_val > 7.5:
        fertilizer = f"{fertilizer} + Organic Compost"
        reasons.append("Soil is alkaline, so organic matter is recommended.")

    return fertilizer, " ".join(reasons)


try:
    model = joblib.load("soil_model.pkl")
except FileNotFoundError:
    print("Error: soil_model.pkl not found in project folder.")
    sys.exit(1)

MODE = os.getenv("SOURCE_MODE", "sim").lower()
PORT = os.getenv("ARDUINO_PORT", "/dev/ttyACM0")
BAUD = int(os.getenv("ARDUINO_BAUD", "9600"))
SER = None
SERIAL_IMPORT_ERROR = None

if MODE == "serial":
    try:
        import serial
        from serial import SerialException
    except ModuleNotFoundError:
        SERIAL_IMPORT_ERROR = "pyserial missing. Install with: pip install pyserial"
    else:
        try:
            SER = serial.Serial(PORT, BAUD, timeout=1)
            time.sleep(2)
        except SerialException as exc:
            SERIAL_IMPORT_ERROR = f"Cannot open {PORT}: {exc}"

app = Flask(__name__)


@app.get("/")
def home():
    return render_template_string(HTML)


def get_reading():
    if MODE == "serial":
        if SERIAL_IMPORT_ERROR:
            raise RuntimeError(SERIAL_IMPORT_ERROR)
        if SER is None:
            raise RuntimeError("Serial connection not initialized")
        line = SER.readline().decode("utf-8", errors="replace").strip()
        if not line:
            raise RuntimeError("No serial data received yet")
        values = parse_serial_line(line)
        raw_line = line
    else:
        ph = round(random.uniform(4.5, 8.5), 2)
        tds = random.randint(300, 800)
        values = [tds / 3, tds / 3, tds / 3, 28.0, 60.0, ph, 100.0]
        raw_line = ",".join(f"{x:.2f}" for x in values)

    frame = pd.DataFrame([values], columns=COLS)
    prediction = model.predict(frame)[0]
    ph_val = values[5]
    n_val, p_val, k_val = values[0], values[1], values[2]
    status, action, level = evaluate_ph(ph_val)
    fertilizer, fertilizer_reason = recommend_fertilizer(
        prediction, n_val, p_val, k_val, ph_val
    )
    return {
        "ok": True,
        "mode": MODE,
        "ph": ph_val,
        "tds": values[0] + values[1] + values[2],
        "prediction": str(prediction),
        "fertilizer": fertilizer,
        "fertilizer_reason": fertilizer_reason,
        "status": status,
        "action": action,
        "level": level,
        "raw": raw_line,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/reading")
def api_reading():
    try:
        return jsonify(get_reading())
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc), "mode": MODE}), 200


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
