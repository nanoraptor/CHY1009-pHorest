#include <DHT.h>
#include <DallasTemperature.h>
#include <OneWire.h>

#define PH_PIN A0
#define TDS_PIN A1
#define DHT_PIN 2
#define WATER_TEMP_PIN 3
#define DHT_TYPE DHT11

const uint16_t LOOP_DELAY_MS = 2000;
const float DEFAULT_COMPENSATION_TEMP_C = 25.0;
const float PH_REFERENCE_TEMP_K = 298.15;

// Replace this with your own TDS calibration factor derived from your reference solution and setup.
const float TDS_CALIBRATION_FACTOR = 645.58;

// Replace these with your own measured pH calibration voltages (pH 7 and pH 4) for your setup.
const float PH_VOLTAGE_PH7 = 1.251;
const float PH_VOLTAGE_PH4 = 1.769;
const float PH_SLOPE = (PH_VOLTAGE_PH4 - PH_VOLTAGE_PH7) / 3.0;
OneWire oneWire(WATER_TEMP_PIN);
DallasTemperature waterTempSensor(&oneWire);
DHT dht(DHT_PIN, DHT_TYPE);

bool isValidWaterTempC(float tempC) {
  return tempC != DEVICE_DISCONNECTED_C && tempC >= -55.0 && tempC <= 125.0;
}

float readWaterTempC() {
  waterTempSensor.requestTemperatures();
  return waterTempSensor.getTempCByIndex(0);
}

float phFromRawCalibrated(int phRaw, float waterTempC) {
  const float voltage = (phRaw * 5.0) / 1023.0;
  const float tempFactor = (waterTempC + 273.15) / PH_REFERENCE_TEMP_K;
  const float compensatedSlope = PH_SLOPE * tempFactor;
  return 7.0 - ((voltage - PH_VOLTAGE_PH7) / compensatedSlope);
}

float tdsFromRawCompensated(int tdsRaw, float waterTempC) {
  const float rawVoltage = (tdsRaw * 5.0) / 1023.0;
  float compensationCoefficient = 1.0 + 0.02 * (waterTempC - 25.0);
  if (compensationCoefficient <= 0.0) compensationCoefficient = 1.0;
  const float compensatedVoltage = rawVoltage / compensationCoefficient;
  return compensatedVoltage * TDS_CALIBRATION_FACTOR;
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
  waterTempSensor.begin();
  dht.begin();
}

void loop() {
  float waterTemp = readWaterTempC();
  bool waterTempOk = isValidWaterTempC(waterTemp);
  float compensationTempC = waterTempOk ? waterTemp : DEFAULT_COMPENSATION_TEMP_C;

  int phRaw = readAverageRaw(PH_PIN, 20, 20);
  float phValue = phFromRawCalibrated(phRaw, compensationTempC);
  int tdsRaw = readAverageRaw(TDS_PIN, 20);
  float tdsPpm = tdsFromRawCompensated(tdsRaw, compensationTempC);
  float dhtTemp = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (dhtTemp != dhtTemp) dhtTemp = -1.0;
  if (humidity != humidity) humidity = -1.0;

  // Serial output used by Python app: ph,tdsPpm,dhtTemp,humidity
  // DS18B20 water temp is used internally for pH/TDS compensation.
  Serial.print(phValue, 2);
  Serial.print(",");
  Serial.print(tdsPpm, 0);
  Serial.print(",");
  Serial.print(dhtTemp);
  Serial.print(",");
  Serial.println(humidity, 1);

  delay(LOOP_DELAY_MS);
}
