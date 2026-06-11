/*
 * SLG47004V NVM Reader — Prime_Maxel-v3
 * 
 * Reads and dumps NVM contents from all 6 GreenPAKs.
 * Run this BEFORE programming to save the factory default state.
 * 
 * Also reads the active register space for comparison.
 */

#include <Wire.h>

#define MUX_ADDR     0x70
#define GP_REG_ADDR  0x08    // Active registers
#define GP_NVM_ADDR  0x09    // NVM (stored config)

#define NVM_SIZE     256

uint8_t buffer[NVM_SIZE];

void selectMuxChannel(uint8_t channel) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

bool readSpace(uint8_t i2cAddr, uint8_t* buf) {
  for (int page = 0; page < NVM_SIZE / 16; page++) {
    uint8_t startAddr = page * 16;
    
    Wire.beginTransmission(i2cAddr);
    Wire.write(startAddr);
    if (Wire.endTransmission() != 0) return false;
    
    Wire.requestFrom(i2cAddr, (uint8_t)16);
    for (int i = 0; i < 16; i++) {
      if (Wire.available()) {
        buf[startAddr + i] = Wire.read();
      } else {
        return false;
      }
    }
  }
  return true;
}

void hexDump(uint8_t* data, int len) {
  for (int i = 0; i < len; i++) {
    if (i % 16 == 0) {
      if (i < 0x10) Serial.print("0");
      Serial.print(i, HEX);
      Serial.print(": ");
    }
    if (data[i] < 0x10) Serial.print("0");
    Serial.print(data[i], HEX);
    Serial.print(" ");
    if (i % 16 == 15) Serial.println();
  }
  Serial.println();
}

bool isAllZero(uint8_t* data, int len) {
  for (int i = 0; i < len; i++) {
    if (data[i] != 0x00) return false;
  }
  return true;
}

bool isAllFF(uint8_t* data, int len) {
  for (int i = 0; i < len; i++) {
    if (data[i] != 0xFF) return false;
  }
  return true;
}

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);
  
  Serial.println("=============================================");
  Serial.println("  Prime_Maxel-v3 GreenPAK NVM Reader");
  Serial.println("=============================================");
  Serial.println();
  
  for (uint8_t ch = 0; ch < 6; ch++) {
    selectMuxChannel(ch);
    delay(10);
    
    Serial.print("=== Channel ");
    Serial.print(ch);
    Serial.println(" ===");
    
    // Check if GreenPAK responds
    Wire.beginTransmission(GP_REG_ADDR);
    if (Wire.endTransmission() != 0) {
      Serial.println("  No GreenPAK found!");
      Serial.println();
      continue;
    }
    
    // Read NVM
    Serial.println("  NVM contents:");
    if (readSpace(GP_NVM_ADDR, buffer)) {
      if (isAllZero(buffer, NVM_SIZE)) {
        Serial.println("  [ALL ZEROS — factory erased]");
      } else if (isAllFF(buffer, NVM_SIZE)) {
        Serial.println("  [ALL 0xFF — blank]");
      } else {
        hexDump(buffer, NVM_SIZE);
      }
    } else {
      Serial.println("  Read failed!");
    }
    
    // Read active registers
    Serial.println("  Active registers:");
    if (readSpace(GP_REG_ADDR, buffer)) {
      if (isAllZero(buffer, NVM_SIZE)) {
        Serial.println("  [ALL ZEROS]");
      } else {
        // Just show non-zero bytes to save space
        int nonZero = 0;
        for (int i = 0; i < NVM_SIZE; i++) {
          if (buffer[i] != 0x00) nonZero++;
        }
        Serial.print("  (");
        Serial.print(nonZero);
        Serial.println(" non-zero bytes)");
        hexDump(buffer, NVM_SIZE);
      }
    } else {
      Serial.println("  Read failed!");
    }
    
    Serial.println();
  }
  
  // Disable mux
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0);
  Wire.endTransmission();
  
  Serial.println("Done! Copy this output for your records.");
}

void loop() {
  // Nothing — run once
}
