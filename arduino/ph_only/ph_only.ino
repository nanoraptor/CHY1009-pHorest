#define PH_PIN A0

// Replace these with your own measured pH calibration voltages (pH 7 and pH 4) for your setup.
const float VOLTAGE_PH7 = 1.251;
const float VOLTAGE_PH4 = 1.769;
const float PH_SLOPE = (VOLTAGE_PH4 - VOLTAGE_PH7) / 3.0;

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
  
  Serial.println("========================================");
  Serial.println("      pH sensor calibrated (uno)        ");
  Serial.println("========================================");
}

void loop() {
  const int raw = readAverageRaw(20);
  const float voltage = (raw * 5.0) / 1023.0;
  const float phValue = 7.0 - ((voltage - VOLTAGE_PH7) / PH_SLOPE);

  Serial.println("----------------------------------------");
  Serial.print("Analog pin   : A0\n");
  Serial.print("Raw ADC      : ");
  Serial.print(raw);
  Serial.println(" / 1023");
  Serial.print("Voltage      : ");
  Serial.print(voltage, 3);
  Serial.println(" V");
  Serial.print("pH value     : ");
  Serial.println(phValue, 2);

  delay(2000);
}