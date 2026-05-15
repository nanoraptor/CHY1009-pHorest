#include <DHT.h>

#define PH_PIN A0
#define TDS_PIN A1
#define DHT_PIN 2
#define DHT_TYPE DHT11

const uint16_t LOOP_DELAY_MS = 2000;
const float TDS_CALIBRATION_FACTOR = 645.58;
const float PH_VOLTAGE_PH7 = 1.251;
const float PH_VOLTAGE_PH4 = 1.769;
const float PH_SLOPE = (PH_VOLTAGE_PH4 - PH_VOLTAGE_PH7) / 3.0;

DHT dht(DHT_PIN, DHT_TYPE);

float phFromRawCalibrated(int phRaw) {
  // Intentionally temperature-independent for now.
  const float voltage = (phRaw * 5.0) / 1023.0;
  return 7.0 - ((voltage - PH_VOLTAGE_PH7) / PH_SLOPE);
}

int readAverageRaw(uint8_t pin, uint8_t samples, uint8_t sampleDelayMs = 10) {
  long total = 0;
  for (uint8_t i = 0; i < samples; i++) {
    total += analogRead(pin);
    delay(sampleDelayMs);
  }
  return (int)(total / samples);
}

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  int phRaw = readAverageRaw(PH_PIN, 20, 20);
  float phValue = phFromRawCalibrated(phRaw);
  int tdsRaw = readAverageRaw(TDS_PIN, 20);
  float tdsVoltage = (tdsRaw * 5.0) / 1023.0;
  // Intentionally temperature-independent for now.
  float tdsPpm = tdsVoltage * TDS_CALIBRATION_FACTOR;
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (temp != temp) temp = -1.0;
  if (hum != hum) hum = -1.0;

  // Serial output used by Python app: ph,tdsPpm,temp,humidity
  Serial.print(phValue, 2);
  Serial.print(",");
  Serial.print(tdsPpm, 0);
  Serial.print(",");
  Serial.print(temp);
  Serial.print(",");
  Serial.println(hum);

  delay(LOOP_DELAY_MS);
}
