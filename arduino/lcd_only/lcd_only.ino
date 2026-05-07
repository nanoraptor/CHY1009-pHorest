#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Change 0x27 to 0x3F (if the screen remains blank after adjusting contrast)
LiquidCrystal_I2C lcd(0x27, 16, 2);

void writeLine(uint8_t row, const char *text) {
  char padded[17];
  snprintf(padded, sizeof(padded), "%-16s", text);
  lcd.setCursor(0, row);
  lcd.print(padded);
}

void formatFixed(char *out, size_t outSize, float value, int decimals) {
  long scale = 1;
  for (int i = 0; i < decimals; i++) scale *= 10;

  long scaled = (long)(value * scale + (value >= 0 ? 0.5 : -0.5));
  long whole = scaled / scale;
  long frac = scaled % scale;
  if (frac < 0) frac = -frac;

  if (decimals == 2) {
    snprintf(out, outSize, "%ld.%02ld", whole, frac);
  } else if (decimals == 1) {
    snprintf(out, outSize, "%ld.%01ld", whole, frac);
  } else {
    snprintf(out, outSize, "%ld", whole);
  }
}

void showValues(float ph, int tds, float temp, float hum, bool hasClimate) {
  char line0[17];
  char line1[17];
  char phText[8];
  char tempText[8];
  char humText[8];
  formatFixed(phText, sizeof(phText), ph, 2);
  formatFixed(tempText, sizeof(tempText), temp, 1);
  formatFixed(humText, sizeof(humText), hum, 1);

  snprintf(line0, sizeof(line0), "pH:%s TDS:%4d", phText, tds);
  if (hasClimate) {
    snprintf(line1, sizeof(line1), "T:%sC H:%s%%", tempText, humText);
  } else {
    snprintf(line1, sizeof(line1), "T/H unavailable");
  }
  writeLine(0, line0);
  writeLine(1, line1);
}

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50);
  lcd.init();
  lcd.backlight();
  writeLine(0, "Waiting data...");
  writeLine(1, "Run apptest.py");
}

void loop() {
  char packet[32];
  size_t n = Serial.readBytesUntil('\n', packet, sizeof(packet) - 1);
  if (n == 0) {
    return;
  }
  packet[n] = '\0';

  // Trim trailing CR/spaces from serial line.
  while (n > 0 && (packet[n - 1] == '\r' || packet[n - 1] == ' ' || packet[n - 1] == '\t')) {
    packet[n - 1] = '\0';
    n--;
  }

  char *comma = strchr(packet, ',');
  if (comma != NULL) {
    *comma = '\0';
    float ph = atof(packet);
    char *rest = comma + 1;
    char *comma2 = strchr(rest, ',');

    if (comma2 == NULL) {
      int tds = atoi(rest);
      showValues(ph, tds, 0.0, 0.0, false);
      Serial.print("ACK2 ");
      Serial.print(ph);
      Serial.print(",");
      Serial.println(tds);
      return;
    }

    *comma2 = '\0';
    int tds = atoi(rest);
    char *tempStr = comma2 + 1;
    char *comma3 = strchr(tempStr, ',');
    if (comma3 == NULL) {
      showValues(ph, tds, 0.0, 0.0, false);
      Serial.println("ACK2 fallback");
      return;
    }

    *comma3 = '\0';
    float temp = atof(tempStr);
    float hum = atof(comma3 + 1);
    showValues(ph, tds, temp, hum, true);
    Serial.print("ACK4 ");
    Serial.print(ph);
    Serial.print(",");
    Serial.print(tds);
    Serial.print(",");
    Serial.print(temp);
    Serial.print(",");
    Serial.println(hum);
  } else {
    writeLine(0, "Invalid packet");
    writeLine(1, packet);
  }
}
