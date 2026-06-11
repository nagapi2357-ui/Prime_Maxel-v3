/*
 * Minimal I2C diagnostic — just check what's on the bus
 * with timeout protection to prevent hangs.
 */

#include <Wire.h>

void setup() {
  Serial.begin(9600);
  while (!Serial);
  delay(1000);
  
  Wire.begin();
  Wire.setWireTimeout(3000, true);  // 3ms timeout, auto-reset
  
  Serial.println(F("=== I2C Diagnostic ==="));
  
  // Step 1: Scan raw bus (no mux)
  Serial.println(F("\nRaw bus scan:"));
  for (uint8_t addr = 1; addr < 120; addr++) {
    Wire.beginTransmission(addr);
    uint8_t err = Wire.endTransmission();
    if (err == 0) {
      Serial.print(F("  0x"));
      Serial.print(addr, HEX);
      if (addr == 0x70) Serial.print(F(" (TCA9548A)"));
      Serial.println();
    }
  }
  
  // Step 2: Check TCA9548A
  Serial.println(F("\nMux check:"));
  Wire.beginTransmission(0x70);
  uint8_t muxErr = Wire.endTransmission();
  if (muxErr != 0) {
    Serial.println(F("  TCA9548A NOT responding!"));
    Serial.println(F("  Check power and connections."));
    return;
  }
  Serial.println(F("  TCA9548A OK"));
  
  // Step 3: Scan each mux channel
  for (uint8_t ch = 0; ch < 8; ch++) {
    // Select channel
    Wire.beginTransmission(0x70);
    Wire.write(1 << ch);
    Wire.endTransmission();
    delay(10);
    
    Serial.print(F("\nCh "));
    Serial.print(ch);
    Serial.print(F(": "));
    
    int found = 0;
    for (uint8_t addr = 1; addr < 120; addr++) {
      if (addr == 0x70) continue;  // Skip mux
      Wire.beginTransmission(addr);
      uint8_t err = Wire.endTransmission();
      if (err == 0) {
        Serial.print(F("0x"));
        Serial.print(addr, HEX);
        Serial.print(F(" "));
        found++;
      }
    }
    if (found == 0) Serial.print(F("empty"));
    Serial.println();
  }
  
  // Disable mux
  Wire.beginTransmission(0x70);
  Wire.write(0);
  Wire.endTransmission();
  
  Serial.println(F("\nDone."));
}

void loop() {}
