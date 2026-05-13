#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#define PH_PIN A0
#define TDS_PIN A1
#define DHT_PIN 2
#define DHT_TYPE DHT11

const uint16_t LOOP_DELAY_MS = 2000;
const float TDS_CALIBRATION_FACTOR = 645.58;

// Change 0x27 to 0x3F if your LCD backpack address is different.
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHT_PIN, DHT_TYPE);

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
  int phRaw = analogRead(PH_PIN);
  int tdsRaw = readAverageRaw(TDS_PIN, 20);
  float tdsVoltage = (tdsRaw * 5.0) / 1023.0;
  float tdsPpm = tdsVoltage * TDS_CALIBRATION_FACTOR;
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (temp != temp) temp = -1.0;
  if (hum != hum) hum = -1.0;

  // LCD output
  clearRow(0);
  lcd.print("pH:");
  lcd.print(phRaw);
  lcd.print(" T:");
  printClimateValue(temp);

  clearRow(1);
  lcd.print("TDS:");
  lcd.print(tdsPpm, 0);
  lcd.print(" H:");
  printClimateValue(hum);

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
