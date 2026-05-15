#include <DallasTemperature.h>
#include <OneWire.h>

#define PH_PIN A0
#define WATER_TEMP_PIN 3

// Replace these with your own measured pH calibration voltages (pH 7 and pH 4) for your setup.
const float VOLTAGE_PH7 = 1.251;
const float VOLTAGE_PH4 = 1.769;
const float PH_SLOPE = (VOLTAGE_PH4 - VOLTAGE_PH7) / 3.0;
const float PH_REFERENCE_TEMP_K = 298.15;
const float DEFAULT_COMPENSATION_TEMP_C = 25.0;

OneWire oneWire(WATER_TEMP_PIN);
DallasTemperature waterTempSensor(&oneWire);

bool isValidWaterTempC(float tempC) {
  return tempC != DEVICE_DISCONNECTED_C && tempC >= -55.0 && tempC <= 125.0;
}

float readWaterTempC() {
  waterTempSensor.requestTemperatures();
  return waterTempSensor.getTempCByIndex(0);
}

int readAverageRaw(uint8_t samples) {
  long total = 0;
  for (uint8_t i = 0; i < samples; i++) {
    total += analogRead(PH_PIN);
    delay(20);
  }
  return (int)(total / samples);
}

void setup() {
  Serial.begin(9600);
  pinMode(PH_PIN, INPUT);
  waterTempSensor.begin();
  
  Serial.println("========================================");
  Serial.println("      pH sensor calibrated (uno)        ");
  Serial.println("========================================");
}

void loop() {
  float waterTemp = readWaterTempC();
  bool waterTempOk = isValidWaterTempC(waterTemp);
  float compensationTempC = waterTempOk ? waterTemp : DEFAULT_COMPENSATION_TEMP_C;

  const int raw = readAverageRaw(20);
  const float voltage = (raw * 5.0) / 1023.0;
  const float tempFactor = (compensationTempC + 273.15) / PH_REFERENCE_TEMP_K;
  const float compensatedSlope = PH_SLOPE * tempFactor;
  const float phValue = 7.0 - ((voltage - VOLTAGE_PH7) / compensatedSlope);

  Serial.println("----------------------------------------");
  Serial.print("Analog pin   : A0\n");
  Serial.print("Raw ADC      : ");
  Serial.print(raw);
  Serial.println(" / 1023");
  Serial.print("Voltage      : ");
  Serial.print(voltage, 3);
  Serial.println(" V");
  Serial.print("Water temp   : ");
  if (waterTempOk) {
    Serial.print(waterTemp, 2);
    Serial.println(" C");
  } else {
    Serial.println("unavailable (using 25.00 C fallback)");
  }
  Serial.print("pH value     : ");
  Serial.println(phValue, 2);

  delay(2000);
}