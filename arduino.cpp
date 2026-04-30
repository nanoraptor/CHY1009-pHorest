#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#define PH_PIN A0
#define TDS_PIN A1
#define DHT_PIN 2
#define DHT_TYPE DHT11

LiquidCrystal_I2C lcd(0x27, 16, 2);
DHT dht(DHT_PIN, DHT_TYPE);

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

  Serial.print(phRaw);
  Serial.print(",");
  Serial.print(tdsRaw);
  Serial.print(",");
  Serial.print(temp);
  Serial.print(",");
  Serial.println(hum);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("pH:");
  lcd.print(phRaw);
  lcd.print(" T:");
  lcd.print(temp, 1);

  lcd.setCursor(0, 1);
  lcd.print("TDS:");
  lcd.print(tdsRaw);
  lcd.print(" H:");
  lcd.print(hum, 1);

  delay(2000);
}
