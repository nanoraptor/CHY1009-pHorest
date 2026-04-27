void setup() {
  Serial.begin(9600);
}

void loop() {
  // Replace these with actual analogRead(pin) from your sensors
  float ph = analogRead(A0) * (14.0 / 1024.0); // Simple pH conversion
  float temp = 28.5; // If you have a DHT11, read it here
  float hum = 65.0;
  float tds = analogRead(A1); // TDS as a proxy for N, P, K
  
  // Format: Nitrogen,phosphorus,potassium,temperature,humidity,ph,rainfall
  // Since we don't have NPK sensors, we estimate them from TDS for the demo
  Serial.print(tds/3); Serial.print(","); 
  Serial.print(tds/3); Serial.print(",");
  Serial.print(tds/3); Serial.print(",");
  Serial.print(temp); Serial.print(",");
  Serial.print(hum); Serial.print(",");
  Serial.print(ph); Serial.print(",");
  Serial.println("0"); // 0 for rainfall
  
  delay(2000); 
}
