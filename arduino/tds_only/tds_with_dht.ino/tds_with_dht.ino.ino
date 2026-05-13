#include "DHT.h"

#define DHTPIN 2          // Digital pin connected to DHT11
#define DHTTYPE DHT11
#define TdsSensorPin A1   // Analog pin connected to TDS probe
#define VREF 5.0          // Use 5.0 for Arduino Uno/Mega, 3.3 for ESP32/Nano Every

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    dht.begin();
    pinMode(TdsSensorPin, INPUT);
}

void loop() {
    // Read temperature from DHT11
    float tempC = dht.readTemperature(); 

    // Check if reading failed
    if (isnan(tempC)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
    }

    // Read voltage from TDS sensor
    int sensorValue = analogRead(TdsSensorPin);
    float rawVoltage = sensorValue * VREF / 1024.0;

    // Temperature Compensation Logic
    float compensationCoefficient = 1.0 + 0.02 * (tempC - 25.0); 
    float compensatedVoltage = rawVoltage / compensationCoefficient;

    // Convert voltage to ppm
    float tdsValue = (133.42 * pow(compensatedVoltage, 3) - 255.86 * pow(compensatedVoltage, 2) + 857.39 * compensatedVoltage) * 0.5;

    // Output to Serial Monitor
    Serial.print("Temp: ");
    Serial.print(tempC);
    Serial.print(" C | TDS: ");
    Serial.print(tdsValue);
    Serial.println(" ppm");

    delay(1000); // Wait 1 second
}