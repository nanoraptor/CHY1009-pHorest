#include <DHT.h>

#define DHT_PIN 2
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();

  Serial.println("========================================");
  Serial.println("      DHT11 SENSOR TEST (ARDUINO UNO)  ");
  Serial.println("========================================");
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (temp != temp || hum != hum) {
    Serial.println("[ERROR] Failed to read from DHT11");
    delay(2000);
    return;
  }

  Serial.println("----------------------------------------");
  Serial.print("Temperature : ");
  Serial.print(temp, 1);
  Serial.println(" C");
  Serial.print("Humidity    : ");
  Serial.print(hum, 1);
  Serial.println(" %");

  delay(2000);
}
