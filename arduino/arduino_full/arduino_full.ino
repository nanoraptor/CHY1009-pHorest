#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#define PH_PIN A0
#define TDS_PIN A1
#define DHT_PIN 2
#define DHT_TYPE DHT11

const uint16_t LOOP_DELAY_MS = 2000;
const float TDS_CALIBRATION_FACTOR = 645.58;
const float PH_VOLTAGE_PH7 = 1.251;
const float PH_VOLTAGE_PH4 = 1.769;
const float PH_SLOPE = (PH_VOLTAGE_PH4 - PH_VOLTAGE_PH7) / 3.0;

// Change 0x27 to 0x3F if your LCD backpack address is different.
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHT_PIN, DHT_TYPE);

float phFromRawCalibrated(int phRaw) {
  // Intentionally temperature-independent for now.
  const float voltage = (phRaw * 5.0) / 1023.0;
  return 7.0 - ((voltage - PH_VOLTAGE_PH7) / PH_SLOPE);
}

void clearRow(uint8_t row) {
  lcd.setCursor(0, row);
  lcd.print("                ");
  lcd.setCursor(0, row);
}

void printClimateValue(float value) {
  if (value < 0) {
    lcd.print("--.-");
  } else {
    lcd.print(value, 1);
  }
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
  lcd.init();
  lcd.backlight();
  dht.begin();

  clearRow(0);
  lcd.print("Full Sensor Test");
  clearRow(1);
  lcd.print("Starting...");
  delay(1200);
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

  // LCD output
  clearRow(0);
  lcd.print("pH:");
  lcd.print(phValue, 2);
  lcd.print(" T:");
  printClimateValue(temp);

  clearRow(1);
  lcd.print("TDS:");
  lcd.print(tdsPpm, 0);
  lcd.print(" H:");
  printClimateValue(hum);

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
