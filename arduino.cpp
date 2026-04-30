#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#define PH_PIN A0
#define TDS_PIN A1
#define DHT_PIN 2
#define DHT_TYPE DHT11

// Change 0x27 to 0x3F if your LCD backpack uses that address.
LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHT_PIN, DHT_TYPE);

void clearRow(uint8_t row) {
  lcd.setCursor(0, row);
  lcd.print("                ");
  lcd.setCursor(0, row);
}

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  dht.begin();
}

void loop() {
  int phRaw = analogRead(PH_PIN);
  int tdsRaw = analogRead(TDS_PIN);
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (temp != temp) temp = -1.0;
  if (hum != hum) hum = -1.0;

  clearRow(0);
  lcd.print("pH:");
  lcd.print(phRaw);
  lcd.print(" T:");
  if (temp < 0) {
    lcd.print("--.-");
  } else {
    lcd.print(temp, 1);
  }

  clearRow(1);
  lcd.print("TDS:");
  lcd.print(tdsRaw);
  lcd.print(" H:");
  if (hum < 0) {
    lcd.print("--.-");
  } else {
    lcd.print(hum, 1);
  }

  Serial.print(phRaw);
  Serial.print(",");
  Serial.print(tdsRaw);
  Serial.print(",");
  Serial.print(temp);
  Serial.print(",");
  Serial.println(hum);

  delay(2000);
}
