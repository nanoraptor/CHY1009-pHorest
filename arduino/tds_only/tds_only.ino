#define TDS_PIN A1

// Calculated from your 1.549V reading at 1000ppm
const float CALIBRATION_FACTOR = 645.58; 

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

  Serial.println("========================================");
  Serial.println("      TDS SENSOR CALIBRATED (UNO)      ");
  Serial.println("========================================");
}

void loop() {
  const int raw = readAverageRaw(20);
  const float voltage = (raw * 5.0) / 1023.0;
  
  // Calculate TDS
  const float tdsValue = voltage * CALIBRATION_FACTOR;

  Serial.println("----------------------------------------");
  Serial.print("Analog pin   : A1\n");
  Serial.print("Raw ADC      : ");
  Serial.print(raw);
  Serial.println(" / 1023");
  Serial.print("Voltage      : ");
  Serial.print(voltage, 3);
  Serial.println(" V");
  
  // Print calculated TDS
  Serial.print("TDS ppm      : ");
  Serial.print(tdsValue, 0); 
  Serial.println(" ppm");

  delay(2000);
}