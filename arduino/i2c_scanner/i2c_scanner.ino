// I2C Scanner for Prime_Maxel-v3
// Scans all 127 addresses and reports what's found
// Expected: TCA9548A mux at 0x70 (default address)

#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);
  
  Serial.println("=================================");
  Serial.println("  Prime_Maxel-v3 I2C Scanner");
  Serial.println("=================================");
  Serial.println();
}

void loop() {
  byte error, address;
  int deviceCount = 0;

  Serial.println("Scanning I2C bus...");
  Serial.println();

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("  Device found at 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      
      // Identify known devices
      if (address == 0x70) Serial.print("  <-- TCA9548A I2C Mux");
      if (address >= 0x08 && address <= 0x0F) Serial.print("  <-- SLG47004V GreenPAK (default range)");
      
      Serial.println();
      deviceCount++;
    } else if (error == 4) {
      Serial.print("  Unknown error at 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }

  Serial.println();
  if (deviceCount == 0)
    Serial.println("No I2C devices found! Check wiring.");
  else {
    Serial.print("Found ");
    Serial.print(deviceCount);
    Serial.println(" device(s).");
  }

  Serial.println();
  Serial.println("Scan again in 5 seconds...");
  Serial.println("---");
  delay(5000);
}
