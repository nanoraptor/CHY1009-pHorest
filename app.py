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
    :root {
      --bg-a: #0b1020;
      --bg-b: #1a2745;
      --surface: rgba(13, 24, 45, 0.72);
      --tile: rgba(10, 19, 36, 0.85);
      --border: rgba(148, 163, 184, 0.22);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --ok: #22c55e;
      --warn: #f59e0b;
      --bad: #ef4444;
      --accent: #38bdf8;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Inter", "Segoe UI", Roboto, Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 20% 15%, #1d4ed8 0%, rgba(29, 78, 216, 0) 38%),
        radial-gradient(circle at 85% 10%, #0ea5e9 0%, rgba(14, 165, 233, 0) 32%),
        linear-gradient(145deg, var(--bg-a), var(--bg-b));
      padding: 28px 16px;
    }

    .wrap {
      max-width: 1080px;
      margin: 0 auto;
      display: grid;
      gap: 14px;
    }

    .card {
      border-radius: 16px;
      border: 1px solid var(--border);
      background: var(--surface);
      backdrop-filter: blur(8px);
      box-shadow: 0 12px 34px rgba(2, 6, 23, 0.36);
      padding: 18px;
    }

    .hero {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
    }

    h1 {
      margin: 0 0 6px 0;
      font-size: 30px;
      letter-spacing: 0.01em;
    }

    .muted { color: var(--muted); }

    .mode-pill {
      align-self: center;
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 12px;
      white-space: nowrap;
      background: rgba(56, 189, 248, 0.12);
    }

    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }

    .tile {
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.9), var(--tile));
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      min-height: 102px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .label {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 700;
    }

    .value {
      margin-top: 8px;
      font-size: 28px;
      font-weight: 750;
      line-height: 1.15;
      word-break: break-word;
    }

    .status {
      margin-top: 8px;
      font-size: 21px;
      font-weight: 760;
      line-height: 1.25;
    }

    .status.ok { color: var(--ok); }
    .status.warn { color: var(--warn); }
    .status.bad { color: var(--bad); }

    .subtext { margin-top: 8px; color: var(--muted); }

    .raw-box {
      margin-top: 8px;
      border: 1px solid var(--border);
      background: var(--tile);
      border-radius: 10px;
      padding: 10px 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color: #cbd5e1;
      font-size: 13px;
      overflow-x: auto;
    }

    @media (max-width: 900px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 640px) {
      .hero { flex-direction: column; }
      .mode-pill { align-self: flex-start; }
      .grid { grid-template-columns: 1fr; }
      h1 { font-size: 26px; }
      .value { font-size: 24px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card hero">
      <div>
        <h1>pHorest Dashboard</h1>
        <div class="muted">Live soil chemistry with crop and fertilizer recommendations.</div>
      </div>
      <div class="mode-pill">MODE: <strong id="mode">loading...</strong></div>
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
      <div class="subtext" id="action"></div>
      <div class="subtext" id="fertilizerReason"></div>
    </div>

    <div class="card">
      <div class="label">Raw sensor packet</div>
      <div id="raw" class="raw-box">-</div>
      <div class="muted" style="margin-top:10px;">Last updated: <span id="updated">-</span></div>
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
