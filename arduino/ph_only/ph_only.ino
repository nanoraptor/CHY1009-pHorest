#define PH_PIN A0

int readAverageRaw(uint8_t samples) {
  long total = 0;
  for (uint8_t i = 0; i < samples; i++) {
    total += analogRead(PH_PIN);
    delay(10);
  }
  return (int)(total / samples);
}

void setup() {
  Serial.begin(9600);
  pinMode(PH_PIN, INPUT);

  Serial.println("========================================");
  Serial.println("      PH SENSOR SIGNAL TEST (UNO)      ");
  Serial.println("========================================");
  Serial.println("Testing signal only (not calibrated).");
}

void loop() {
  const int raw = readAverageRaw(10);
  const float voltage = (raw * 5.0) / 1023.0;

  Serial.println("----------------------------------------");
  Serial.print("Analog pin   : A0");
  Serial.println();
  Serial.print("Raw ADC      : ");
  Serial.print(raw);
  Serial.print(" / 1023");
  Serial.println();
  Serial.print("Voltage      : ");
  Serial.print(voltage, 3);
  Serial.println(" V");
  Serial.println("pH value     : Not shown (calibration pending)");

  delay(2000);
}
