#!/usr/bin/env python3
import argparse
import os
import random
import sys
import time
from threading import Lock

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template_string, request

VALID_MODES = {"sim", "serial"}


def parse_start_mode_args(argv):
    parser = argparse.ArgumentParser(description="Run the pHorest dashboard server.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--sim", action="store_true", help="Start in simulation mode")
    mode_group.add_argument("--serial", action="store_true", help="Start in serial mode")
    parser.add_argument(
        "--lock-mode",
        action="store_true",
        help="Hide mode selector and lock the startup mode",
    )
    parser.add_argument(
        "serial_port",
        nargs="?",
        help="Serial port for --serial (example: /dev/ttyACM0 or COM3)",
    )
    args, _ = parser.parse_known_args(argv)
    if args.serial_port and not args.serial:
        parser.error("serial_port can only be used with --serial")
    if args.sim:
        return "sim", None, args.lock_mode
    if args.serial:
        return "serial", args.serial_port, args.lock_mode
    return None, None, args.lock_mode


CLI_MODE_OVERRIDE, CLI_PORT_OVERRIDE, CLI_LOCK_MODE = (
    parse_start_mode_args(sys.argv[1:]) if __name__ == "__main__" else (None, None, False)
)

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

    .mode-select {
      margin-left: 6px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: rgba(15, 23, 42, 0.9);
      color: var(--text);
      padding: 4px 8px;
      font-size: 12px;
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
      <div class="mode-pill"{% if mode_locked %} style="display:none;"{% endif %}>
        MODE:
        <select id="modeSelect" class="mode-select">
          <option value="sim">SIM</option>
          <option value="serial">SERIAL</option>
        </select>
      </div>
    </div>

    <div class="card">
      <div class="grid">
        <div class="tile"><div class="label">pH</div><div class="value" id="ph">-</div></div>
        <div class="tile"><div class="label">TDS (ppm)</div><div class="value" id="tds">-</div></div>
        <div class="tile"><div class="label">Temperature (°C)</div><div class="value" id="temperature">-</div></div>
        <div class="tile"><div class="label">Humidity (%)</div><div class="value" id="humidity">-</div></div>
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

    <div class="card" id="serialSensorsCard" style="display:none;">
      <div class="label">Connected Sensors (Serial Mode)</div>
      <div id="serialSensorsBody" class="raw-box">Switch to SERIAL mode to inspect connected sensors.</div>
    </div>
  </div>

  <script>
    const modeSelect = document.getElementById('modeSelect');
    const modeLocked = {{ 'true' if mode_locked else 'false' }};
    const serialSensorsCard = document.getElementById('serialSensorsCard');
    const serialSensorsBody = document.getElementById('serialSensorsBody');

    async function setMode(mode) {
      const res = await fetch('/api/mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode }),
      });
      return res.json();
    }

    function updateSerialSensorControls(mode) {
      const serialMode = mode === 'serial';
      serialSensorsCard.style.display = serialMode ? 'block' : 'none';
    }

    function clearReadingUI() {
      document.getElementById('ph').textContent = '-';
      document.getElementById('tds').textContent = '-';
      document.getElementById('temperature').textContent = '-';
      document.getElementById('humidity').textContent = '-';
      document.getElementById('crop').textContent = '-';
      document.getElementById('fertilizer').textContent = '-';
      document.getElementById('raw').textContent = '-';
      document.getElementById('updated').textContent = '-';
      document.getElementById('action').textContent = '';
      document.getElementById('fertilizerReason').textContent = '';
    }

    function normalizeSerialError(message) {
      const text = String(message || '').toLowerCase();
      if (
        text.includes('arduino not connected') ||
        text.includes('cannot open') ||
        text.includes('no such file or directory')
      ) {
        return 'Arduino not detected. Connect the board and verify the serial port.';
      }
      return message || 'Unable to fetch serial sensor status';
    }

    async function loadSerialSensors(options = {}) {
      const silent = Boolean(options.silent);
      if (modeSelect.value !== 'serial') {
        serialSensorsCard.style.display = 'none';
        return;
      }
      serialSensorsCard.style.display = 'block';
      if (!silent) {
        serialSensorsBody.textContent = 'Checking sensor connections...';
      }
      try {
        const res = await fetch('/api/serial/sensors', { cache: 'no-store' });
        const data = await res.json();
        if (!data.ok) {
          throw new Error(data.error || 'Unable to fetch serial sensor status');
        }
        const rows = data.sensors.map((sensor) => {
          const flag = sensor.connected ? 'CONNECTED' : 'MISSING';
          return `${flag.padEnd(10)} | ${sensor.name.padEnd(22)} | ${sensor.value}`;
        });
        serialSensorsBody.textContent = `${rows.join('\\n')}\\n\\nPacket: ${data.raw}\\nUpdated: ${data.timestamp}`;
        serialSensorsCard.style.display = 'block';
      } catch (e) {
        serialSensorsBody.textContent = normalizeSerialError(e.message);
        serialSensorsCard.style.display = 'block';
      }
    }

    async function refresh() {
      try {
        const res = await fetch('/api/reading', { cache: 'no-store' });
        const data = await res.json();
        if (!data.ok) {
          if (data.mode) modeSelect.value = data.mode;
          if (data.mode) updateSerialSensorControls(data.mode);
          clearReadingUI();
          const statusMessage =
            data.mode === 'serial'
              ? normalizeSerialError(data.error)
              : (data.error || 'Dashboard error');
          document.getElementById('status').textContent = statusMessage;
          document.getElementById('status').className = 'status bad';
          if (data.mode === 'serial') {
            serialSensorsBody.textContent = statusMessage;
            serialSensorsCard.style.display = 'block';
          }
          return;
        }

        modeSelect.value = data.mode;
        updateSerialSensorControls(data.mode);
        document.getElementById('ph').textContent = data.ph.toFixed(2);
        document.getElementById('tds').textContent = Math.round(data.tds);
        document.getElementById('temperature').textContent = data.temperature.toFixed(1);
        document.getElementById('humidity').textContent = data.humidity.toFixed(1);
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
        if (data.mode === 'serial') {
          await loadSerialSensors({ silent: true });
        }
      } catch (e) {
        clearReadingUI();
        const statusEl = document.getElementById('status');
        statusEl.textContent = 'Dashboard fetch error';
        statusEl.className = 'status bad';
      }
    }

    if (modeLocked) {
      modeSelect.disabled = true;
    } else {
      modeSelect.addEventListener('change', async (event) => {
        const desiredMode = event.target.value;
        modeSelect.disabled = true;
        try {
          const data = await setMode(desiredMode);
          if (!data.ok) {
            throw new Error(data.error || 'Failed to switch mode');
          }
          if (data.mode === 'serial') {
            await loadSerialSensors();
          }
        } catch (e) {
          const statusEl = document.getElementById('status');
          statusEl.textContent = e.message;
          statusEl.className = 'status bad';
        } finally {
          modeSelect.disabled = false;
          refresh();
        }
      });
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
    numeric = [float(x) for x in parts]
    if len(numeric) == 7:
        return numeric
    if len(numeric) == 4:
        # Arduino packet format: phRaw,tdsRaw,temp,humidity
        ph_raw, tds_raw, temp, hum = numeric
        npk_proxy = tds_raw / 3.0
        return [npk_proxy, npk_proxy, npk_proxy, temp, hum, ph_raw, 100.0]
    raise ValueError("Expected 4 or 7 comma-separated values")


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


def sanitize_input_values(values: list):
    """
    Sanitizes a list of 7 sensor values.
    The order is N, P, K, temp, humidity, pH, rainfall.
    Raises ValueError on validation failure.
    """
    if len(values) != 7:
        raise ValueError(f"Expected 7 values for sanitization, but got {len(values)}")

    sanitized = []
    labels = ["Nitrogen", "Phosphorus", "Potassium", "Temperature", "Humidity", "pH", "Rainfall"]
    ranges = [
        (0, 2000),  # N
        (0, 2000),  # P
        (0, 2000),  # K
        (-40, 60),  # Temp
        (0, 100),   # Humidity
        (0, 14),    # pH
        (0, 1000),  # Rainfall
    ]

    for i, (val, label, (min_val, max_val)) in enumerate(zip(values, labels, ranges)):
        try:
            f_val = float(val)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid non-numeric value for {label}: {val}") from e

        if not (min_val <= f_val <= max_val):
            raise ValueError(f"{label} value {f_val} is out of the acceptable range ({min_val} - {max_val})")
        sanitized.append(f_val)

    return sanitized


try:
    model = joblib.load("soil_model.pkl")
except FileNotFoundError:
    print("Error: soil_model.pkl not found in project folder.")
    sys.exit(1)

MODE = os.getenv("SOURCE_MODE", "sim").lower()
PORT = os.getenv("ARDUINO_PORT", "/dev/ttyACM0")
BAUD = int(os.getenv("ARDUINO_BAUD", "9600"))
MODE_LOCKED = False
if MODE not in VALID_MODES:
    MODE = "sim"

SER = None
SERIAL_MODULE = None
SERIAL_EXCEPTION = None

app = Flask(__name__)
LATEST_READING = None
LATEST_READING_LOCK = Lock()
STATE_LOCK = Lock()


@app.get("/")
def home():
    return render_template_string(HTML, mode_locked=MODE_LOCKED)


def get_mode():
    with STATE_LOCK:
        return MODE


def close_serial_locked():
    global SER
    if SER is not None:
        SER.close()
        SER = None


def ensure_serial_ready_locked():
    global SERIAL_MODULE, SERIAL_EXCEPTION, SER

    if SERIAL_MODULE is None:
        try:
            import serial as serial_module
            from serial import SerialException as serial_exception
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "pyserial missing. Install with: pip install pyserial"
            ) from exc
        SERIAL_MODULE = serial_module
        SERIAL_EXCEPTION = serial_exception

    if SER is None:
        try:
            SER = SERIAL_MODULE.Serial(PORT, BAUD, timeout=1)
            time.sleep(2)
        except SERIAL_EXCEPTION as exc:
            raise RuntimeError("Arduino not connected") from exc
    return SER


def switch_mode(new_mode: str):
    global MODE, LATEST_READING
    mode = str(new_mode).strip().lower()
    if mode not in VALID_MODES:
        raise ValueError("Mode must be 'sim' or 'serial'")

    with STATE_LOCK:
        if mode == MODE:
            return MODE
        if mode != "serial":
            close_serial_locked()
        MODE = mode

    with LATEST_READING_LOCK:
        LATEST_READING = None
    return mode


def _safe_float(text):
    try:
        return float(str(text).strip())
    except (TypeError, ValueError):
        return None


def _is_non_nan(value):
    return value is not None and value == value


def build_serial_sensor_status(reading: dict):
    raw_line = str(reading.get("raw", "")).strip()
    parts = [p.strip() for p in raw_line.split(",")] if raw_line else []
    if len(parts) < 4:
        raise RuntimeError("Serial packet does not contain all expected sensor fields")

    ph_raw = _safe_float(parts[0])
    tds_raw = _safe_float(parts[1])
    temp_val = _safe_float(parts[2])
    hum_val = _safe_float(parts[3])

    return [
        {
            "name": "pH Sensor (A0)",
            "connected": _is_non_nan(ph_raw),
            "value": f"raw={parts[0]}",
        },
        {
            "name": "TDS Sensor (A1)",
            "connected": _is_non_nan(tds_raw),
            "value": f"raw={parts[1]}",
        },
        {
            "name": "DHT11 Temperature",
            "connected": _is_non_nan(temp_val) and temp_val >= 0,
            "value": f"{parts[2]} C",
        },
        {
            "name": "DHT11 Humidity",
            "connected": _is_non_nan(hum_val) and hum_val >= 0,
            "value": f"{parts[3]} %",
        },
    ]


def get_reading():
    with STATE_LOCK:
        mode = MODE
        if mode == "serial":
            ser = ensure_serial_ready_locked()
            line = ser.readline().decode("utf-8", errors="replace").strip()
            if not line:
                raise RuntimeError("No serial data received yet")
            values = parse_serial_line(line)
            raw_line = line
        else:
            ph = round(random.uniform(4.5, 8.5), 2)
            tds = random.randint(300, 800)
            temp = round(random.uniform(24.0, 35.0), 1)
            hum = round(random.uniform(45.0, 85.0), 1)
            values = [tds / 3, tds / 3, tds / 3, temp, hum, ph, 100.0]
            raw_line = ",".join(f"{x:.2f}" for x in values)

    values = sanitize_input_values(values)

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
        "mode": mode,
        "ph": ph_val,
        "tds": values[0] + values[1] + values[2],
        "temperature": values[3],
        "humidity": values[4],
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
    global LATEST_READING
    try:
        reading = get_reading()
        with LATEST_READING_LOCK:
            LATEST_READING = dict(reading)
        return jsonify(reading)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc), "mode": get_mode()}), 200


@app.get("/api/latest")
def api_latest():
    global LATEST_READING
    try:
        with LATEST_READING_LOCK:
            cached = dict(LATEST_READING) if LATEST_READING is not None else None
        if cached is None:
            cached = get_reading()
            with LATEST_READING_LOCK:
                LATEST_READING = dict(cached)
        return jsonify(cached)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc), "mode": get_mode()}), 200


@app.route("/api/mode", methods=["GET", "POST"])
def api_mode():
    if request.method == "GET":
        return jsonify(
            {
                "ok": True,
                "mode": get_mode(),
                "port": PORT,
                "baud": BAUD,
                "mode_locked": MODE_LOCKED,
            }
        )

    if MODE_LOCKED:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Mode switching is locked for this launch",
                    "mode": get_mode(),
                    "mode_locked": True,
                }
            ),
            200,
        )

    payload = request.get_json(silent=True) or {}
    requested_mode = payload.get("mode")
    try:
        active_mode = switch_mode(requested_mode)
        return jsonify({"ok": True, "mode": active_mode, "port": PORT, "baud": BAUD})
    except ValueError as exc:
        return (
            jsonify({"ok": False, "error": str(exc), "mode": get_mode()}),
            400,
        )
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc), "mode": get_mode()}), 200


@app.get("/api/serial/sensors")
def api_serial_sensors():
    global LATEST_READING
    if get_mode() != "serial":
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Switch to SERIAL mode to inspect connected sensors",
                    "mode": get_mode(),
                }
            ),
            200,
        )

    try:
        with LATEST_READING_LOCK:
            reading = dict(LATEST_READING) if LATEST_READING is not None else None
        if reading is None or reading.get("mode") != "serial":
            reading = get_reading()
            with LATEST_READING_LOCK:
                LATEST_READING = dict(reading)

        sensors = build_serial_sensor_status(reading)
        return jsonify(
            {
                "ok": True,
                "mode": "serial",
                "sensors": sensors,
                "raw": reading.get("raw", ""),
                "timestamp": reading.get("timestamp", ""),
            }
        )
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc), "mode": get_mode()}), 200


if __name__ == "__main__":
    if CLI_MODE_OVERRIDE is not None:
        MODE = CLI_MODE_OVERRIDE
    if CLI_PORT_OVERRIDE:
        PORT = CLI_PORT_OVERRIDE
    if CLI_LOCK_MODE:
        MODE_LOCKED = True
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
