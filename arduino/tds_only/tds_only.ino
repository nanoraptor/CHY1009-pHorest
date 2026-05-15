#include <DallasTemperature.h>
#include <OneWire.h>

#define TDS_PIN A1
#define WATER_TEMP_PIN 3

// Replace this with your own TDS calibration factor derived from your reference solution and setup.
const float CALIBRATION_FACTOR = 645.58; 
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
    total += analogRead(TDS_PIN);
    delay(10);
  }
  return (int)(total / samples);
}

void setup() {
  Serial.begin(9600);
  pinMode(TDS_PIN, INPUT);
  waterTempSensor.begin();

  Serial.println("========================================");
  Serial.println("      TDS SENSOR CALIBRATED (UNO)      ");
  Serial.println("========================================");
}

void loop() {
  float waterTemp = readWaterTempC();
  bool waterTempOk = isValidWaterTempC(waterTemp);
  float compensationTempC = waterTempOk ? waterTemp : DEFAULT_COMPENSATION_TEMP_C;

  const int raw = readAverageRaw(20);
  const float rawVoltage = (raw * 5.0) / 1023.0;
  
  float compensationCoefficient = 1.0 + 0.02 * (compensationTempC - 25.0);
  if (compensationCoefficient <= 0.0) compensationCoefficient = 1.0;
  const float compensatedVoltage = rawVoltage / compensationCoefficient;
  const float tdsValue = compensatedVoltage * CALIBRATION_FACTOR;

  Serial.println("----------------------------------------");
  Serial.print("Analog pin   : A1\n");
  Serial.print("Raw ADC      : ");
  Serial.print(raw);
  Serial.println(" / 1023");
  Serial.print("Voltage      : ");
  Serial.print(rawVoltage, 3);
  Serial.println(" V");
  Serial.print("Water temp   : ");
  if (waterTempOk) {
    Serial.print(waterTemp, 2);
    Serial.println(" C");
  } else {
    Serial.println("unavailable (using 25.00 C fallback)");
  }
  
  // Print calculated TDS
  Serial.print("TDS ppm      : ");
  Serial.print(tdsValue, 0); 
  Serial.println(" ppm");

  delay(2000);
}