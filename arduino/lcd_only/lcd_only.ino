#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Change 0x27 to 0x3F if the screen remains blank after adjusting the contrast screw.
LiquidCrystal_I2C lcd(0x27, 16, 2); 

void setup() {
  lcd.init();
  lcd.backlight();
  
  lcd.setCursor(0, 0);
  lcd.print("Hello World");
  
  lcd.setCursor(0, 1);
  lcd.print("First Arduino Program");
}

void loop() {
lcd.scrollDisplayLeft();
  delay(400);
}