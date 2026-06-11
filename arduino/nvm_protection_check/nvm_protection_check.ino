/*
 * SLG47004V NVM Protection Check & Clear
 * 
 * Reads the protection registers (RPR at 0xE0, NPR at 0xE1)
 * and the erase register (ERSE at 0xE3) from register space.
 * Optionally clears write protection to allow NVM programming.
 * 
 * Also tests a single-page erase+write+verify cycle.
 */

#include <Wire.h>

#define MUX_ADDR     0x70
#define GP_REG_ADDR  0x08    // Active registers
#define GP_NVM_ADDR  0x09    // NVM space

void selectMuxChannel(uint8_t channel) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

uint8_t readRegByte(uint8_t i2cAddr, uint8_t regAddr) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(regAddr);
  Wire.endTransmission();
  Wire.requestFrom(i2cAddr, (uint8_t)1);
  if (Wire.available()) return Wire.read();
  return 0xFF;
}

bool writeRegByte(uint8_t i2cAddr, uint8_t regAddr, uint8_t val) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(regAddr);
  Wire.write(val);
  return (Wire.endTransmission() == 0);
}

void printBinary(uint8_t val) {
  for (int i = 7; i >= 0; i--) {
    Serial.print((val >> i) & 1);
  }
}

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);
  
  Serial.println("=============================================");
  Serial.println("  SLG47004V NVM Protection Diagnostic");
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
      continue;
    }
    
    // Read protection registers from register space (0x08)
    uint8_t rpr = readRegByte(GP_REG_ADDR, 0xE0);
    uint8_t npr = readRegByte(GP_REG_ADDR, 0xE1);
    uint8_t erse = readRegByte(GP_REG_ADDR, 0xE3);
    
    Serial.print("  RPR  (0xE0) = 0x");
    Serial.print(rpr, HEX);
    Serial.print("  bin: ");
    printBinary(rpr);
    Serial.println();
    
    Serial.print("  NPR  (0xE1) = 0x");
    Serial.print(npr, HEX);
    Serial.print("  bin: ");
    printBinary(npr);
    Serial.println();
    
    Serial.print("  ERSE (0xE3) = 0x");
    Serial.print(erse, HEX);
    Serial.print("  bin: ");
    printBinary(erse);
    Serial.println();
    
    // Decode RPR
    Serial.print("  RPR decode: ");
    uint8_t rprb = rpr & 0x0F;
    uint8_t rhprb = (rpr >> 4) & 0x01;
    Serial.print("RPRB[3:0]=");
    Serial.print(rprb, BIN);
    Serial.print(" RH_PRB=");
    Serial.println(rhprb);
    
    // Decode NPR
    Serial.print("  NPR decode: ");
    uint8_t nprb = npr & 0x0F;
    uint8_t prl = (npr >> 4) & 0x01;
    Serial.print("NPRB[3:0]=");
    Serial.print(nprb, BIN);
    Serial.print(" PRL=");
    Serial.print(prl);
    if (prl) Serial.print(" *** PERMANENTLY LOCKED ***");
    Serial.println();
    
    // Also read bytes 0xE0-0xEF from NVM space
    Serial.print("  NVM 0xE0-0xEF: ");
    Wire.beginTransmission(GP_NVM_ADDR);
    Wire.write(0xE0);
    Wire.endTransmission();
    Wire.requestFrom(GP_NVM_ADDR, (uint8_t)16);
    for (int i = 0; i < 16; i++) {
      if (Wire.available()) {
        uint8_t b = Wire.read();
        if (b < 0x10) Serial.print("0");
        Serial.print(b, HEX);
        Serial.print(" ");
      }
    }
    Serial.println();
    
    // Read bytes 0xF0-0xFF from NVM space
    Serial.print("  NVM 0xF0-0xFF: ");
    Wire.beginTransmission(GP_NVM_ADDR);
    Wire.write(0xF0);
    Wire.endTransmission();
    Wire.requestFrom(GP_NVM_ADDR, (uint8_t)16);
    for (int i = 0; i < 16; i++) {
      if (Wire.available()) {
        uint8_t b = Wire.read();
        if (b < 0x10) Serial.print("0");
        Serial.print(b, HEX);
        Serial.print(" ");
      }
    }
    Serial.println();
    
    Serial.println();
  }
  
  // Disable mux
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0);
  Wire.endTransmission();
  
  Serial.println("=============================================");
  Serial.println("Send 'C' to attempt to CLEAR protection on");
  Serial.println("all channels and test a write cycle.");
  Serial.println("Send anything else to exit.");
  Serial.println("=============================================");
  
  while (!Serial.available());
  char c = Serial.read();
  if (c != 'C' && c != 'c') {
    Serial.println("Done.");
    return;
  }
  
  Serial.println();
  Serial.println("Attempting to clear protection and test write...");
  Serial.println();
  
  for (uint8_t ch = 0; ch < 1; ch++) {  // Test on channel 0 only first
    selectMuxChannel(ch);
    delay(10);
    
    Serial.print("=== Channel ");
    Serial.print(ch);
    Serial.println(" — Protection clear test ===");
    
    // Try to clear NPR (write 0x00 to 0xE1 in register space)
    Serial.print("  Clearing NPR... ");
    if (writeRegByte(GP_REG_ADDR, 0xE1, 0x00)) {
      Serial.println("ACK");
    } else {
      Serial.println("NACK!");
    }
    
    // Try to clear RPR (write 0x00 to 0xE0 in register space)
    Serial.print("  Clearing RPR... ");
    if (writeRegByte(GP_REG_ADDR, 0xE0, 0x00)) {
      Serial.println("ACK");
    } else {
      Serial.println("NACK!");
    }
    
    // Re-read protection registers
    uint8_t rpr = readRegByte(GP_REG_ADDR, 0xE0);
    uint8_t npr = readRegByte(GP_REG_ADDR, 0xE1);
    Serial.print("  RPR after clear: 0x");
    Serial.println(rpr, HEX);
    Serial.print("  NPR after clear: 0x");
    Serial.println(npr, HEX);
    
    // Now try erasing NVM page 0
    Serial.print("  Erasing NVM page 0... ");
    uint8_t eraseCmd = 0xC0;  // ERSE=110, page=0
    if (writeRegByte(GP_REG_ADDR, 0xE3, eraseCmd)) {
      Serial.println("ACK");
    } else {
      Serial.println("NACK!");
    }
    delay(100);
    
    // Read NVM page 0 to check if erased
    Serial.print("  NVM page 0 after erase: ");
    Wire.beginTransmission(GP_NVM_ADDR);
    Wire.write(0x00);
    Wire.endTransmission();
    Wire.requestFrom(GP_NVM_ADDR, (uint8_t)16);
    bool allZero = true;
    bool allFF = true;
    for (int i = 0; i < 16; i++) {
      if (Wire.available()) {
        uint8_t b = Wire.read();
        if (b != 0x00) allZero = false;
        if (b != 0xFF) allFF = false;
        if (b < 0x10) Serial.print("0");
        Serial.print(b, HEX);
        Serial.print(" ");
      }
    }
    Serial.println();
    if (allZero) Serial.println("  → All zeros (erased to 0x00)");
    else if (allFF) Serial.println("  → All 0xFF (erased to 0xFF)");
    else Serial.println("  → Mixed data (erase may have FAILED)");
    
    // Try writing test pattern to NVM page 8 (0x80-0x8F)
    // This is where our config data goes
    Serial.print("  Erasing NVM page 8... ");
    eraseCmd = 0xC0 | 8;  // ERSE=110, page=8
    if (writeRegByte(GP_REG_ADDR, 0xE3, eraseCmd)) {
      Serial.println("ACK");
    } else {
      Serial.println("NACK!");
    }
    delay(100);
    
    // Write test pattern to page 8
    Serial.print("  Writing test to page 8... ");
    Wire.beginTransmission(GP_NVM_ADDR);
    Wire.write(0x80);  // Start address
    for (int i = 0; i < 16; i++) {
      Wire.write(0xAA);  // Test pattern
    }
    if (Wire.endTransmission() == 0) {
      Serial.println("ACK");
    } else {
      Serial.println("NACK!");
    }
    delay(50);
    
    // Read back page 8
    Serial.print("  NVM page 8 readback: ");
    Wire.beginTransmission(GP_NVM_ADDR);
    Wire.write(0x80);
    Wire.endTransmission();
    Wire.requestFrom(GP_NVM_ADDR, (uint8_t)16);
    int matches = 0;
    for (int i = 0; i < 16; i++) {
      if (Wire.available()) {
        uint8_t b = Wire.read();
        if (b == 0xAA) matches++;
        if (b < 0x10) Serial.print("0");
        Serial.print(b, HEX);
        Serial.print(" ");
      }
    }
    Serial.println();
    Serial.print("  → ");
    Serial.print(matches);
    Serial.println("/16 bytes match test pattern (0xAA)");
    
    if (matches == 16) {
      Serial.println("  *** NVM WRITE WORKS! Protection cleared. ***");
    } else {
      Serial.println("  *** NVM WRITE FAILED — protection still active ***");
    }
    
    Serial.println();
  }
  
  Serial.println("Done. If protection cleared, run the main programmer next.");
}

void loop() {}
