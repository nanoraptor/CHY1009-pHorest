import json
import os
import sys
import time
from urllib import error, request

try:
    import serial
    from serial import SerialException
except ModuleNotFoundError:
    print("Error: pyserial is not installed. Run: pip install pyserial")
    sys.exit(1)

APP_READING_URL = os.getenv("APP_READING_URL", "http://127.0.0.1:5000/api/latest")
ARDUINO_PORT = os.getenv("ARDUINO_PORT", "/dev/ttyACM0")
ARDUINO_BAUD = int(os.getenv("ARDUINO_BAUD", "9600"))
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "0.1"))
ARDUINO_BOOT_WAIT = float(os.getenv("ARDUINO_BOOT_WAIT", "3"))


def fetch_simulated_values():
    try:
        with request.urlopen(APP_READING_URL, timeout=4) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except error.URLError as exc:
        raise RuntimeError(f"Cannot reach app.py at {APP_READING_URL}: {exc}") from exc

    if not payload.get("ok"):
        raise RuntimeError(payload.get("error", "app.py returned an unknown error"))

    ph_value = float(payload["ph"])
    tds_value = float(payload["tds"])
    temp_value = float(payload.get("temperature", 0.0))
    hum_value = float(payload.get("humidity", 0.0))
    reading_key = (
        payload.get("timestamp"),
        round(ph_value, 2),
        int(round(tds_value)),
        round(temp_value, 1),
        round(hum_value, 1),
    )
    return reading_key, (
        ph_value,
        tds_value,
        temp_value,
        hum_value,
    )


def build_packet(ph_value: float, tds_value: float, temp_value: float, hum_value: float) -> str:
    # Packet format expected by the Arduino LCD receiver sketch.
    return (
        f"{ph_value:.2f},"
        f"{int(round(tds_value))},"
        f"{temp_value:.1f},"
        f"{hum_value:.1f}\n"
    )


def main():
    try:
        ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
    except SerialException as exc:
        print(f"Error: cannot open serial port {ARDUINO_PORT}: {exc}")
        sys.exit(1)

    time.sleep(ARDUINO_BOOT_WAIT)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    print(f"LCD bridge live -> app: {APP_READING_URL} | serial: {ARDUINO_PORT}@{ARDUINO_BAUD}")

    last_sent_key = None
    try:
        while True:
            try:
                reading_key, values = fetch_simulated_values()
                if reading_key != last_sent_key:
                    ph_value, tds_value, temp_value, hum_value = values
                    packet = build_packet(ph_value, tds_value, temp_value, hum_value)
                    ser.write(packet.encode("utf-8"))
                    ser.flush()
                    print(
                        "Sent to LCD -> "
                        f"pH: {ph_value:.2f}, "
                        f"TDS: {int(round(tds_value))} ppm, "
                        f"T: {temp_value:.1f} C, "
                        f"H: {hum_value:.1f}%"
                    )
                    reply = ser.readline().decode("utf-8", errors="replace").strip()
                    if reply:
                        print(f"Arduino -> {reply}")
                    last_sent_key = reading_key
            except RuntimeError as exc:
                print(f"Reading error: {exc}")
            except SerialException as exc:
                print(f"Serial write error: {exc}")
                break
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
