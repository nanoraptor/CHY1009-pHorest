#include <DHT.h>

#define PH_PIN A0
#define TDS_PIN A1
#define DHT_PIN 2
#define DHT_TYPE DHT11

const uint16_t LOOP_DELAY_MS = 2000;
const float TDS_CALIBRATION_FACTOR = 645.58;

DHT dht(DHT_PIN, DHT_TYPE);

int readAverageRaw(uint8_t pin, uint8_t samples) {
  long total = 0;
  for (uint8_t i = 0; i < samples; i++) {
    total += analogRead(pin);
    delay(10);
  }
  return (int)(total / samples);
}

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  int phRaw = analogRead(PH_PIN);
  int tdsRaw = readAverageRaw(TDS_PIN, 20);
  float tdsVoltage = (tdsRaw * 5.0) / 1023.0;
  float tdsPpm = tdsVoltage * TDS_CALIBRATION_FACTOR;
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (temp != temp) temp = -1.0;
  if (hum != hum) hum = -1.0;

  // Serial output used by Python app: phRaw,tdsPpm,temp,humidity
  Serial.print(phRaw);
  Serial.print(",");
  Serial.print(tdsPpm, 0);
  Serial.print(",");
  Serial.print(temp);
  Serial.print(",");
  Serial.println(hum);

  delay(LOOP_DELAY_MS);
}
