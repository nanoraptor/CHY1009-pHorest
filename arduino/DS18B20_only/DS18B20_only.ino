#include <DallasTemperature.h>
#include <OneWire.h>

#define WATER_TEMP_PIN 3

OneWire oneWire(WATER_TEMP_PIN);
DallasTemperature waterTempSensor(&oneWire);

bool isValidWaterTempC(float tempC) {
  return tempC != DEVICE_DISCONNECTED_C && tempC >= -55.0 && tempC <= 125.0;
}

float readWaterTempC() {
  waterTempSensor.requestTemperatures();
  return waterTempSensor.getTempCByIndex(0);
}

void setup() {
  Serial.begin(9600);
  waterTempSensor.begin();

  Serial.println("========================================");
  Serial.println("   DS18B20 WATER TEMPERATURE TEST (UNO) ");
  Serial.println("========================================");
}

void loop() {
  float waterTemp = readWaterTempC();
  bool waterTempOk = isValidWaterTempC(waterTemp);

  Serial.println("----------------------------------------");
  Serial.print("Sensor pin   : D3\n");
  if (waterTempOk) {
    Serial.print("Water temp   : ");
    Serial.print(waterTemp, 2);
    Serial.println(" C");
  } else {
    Serial.println("Water temp   : unavailable");
    Serial.println("Check DS18B20 wiring and pull-up resistor.");
  }

  delay(2000);
}
