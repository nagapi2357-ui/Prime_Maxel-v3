/*
 * Board 3 — GreenPAK RAM Programmer (Channel 0)
 * 
 * Writes Go Configure design to RAM ONLY (volatile, resets on power cycle).
 * 
 * SAFETY:
 * - Writes to 0x08 (RAM) only, NEVER to 0x09 (NVM)
 * - Preserves factory I2C config bytes (0xDA-0xDF, 0xF0-0xFF)
 * - Reads factory NVM first, merges with our design
 * - Verifies every write
 * 
 * Design: OSC1 (2.048MHz) → CNT0 (16-bit, div 1000) → GPIO5 (Pin 19)
 * Expected output: 1024 Hz square wave on Pin 19
 */

#include <Wire.h>

#define MUX_ADDR     0x70
#define GP_REG_ADDR  0x08    // RAM (active registers)
#define GP_NVM_ADDR  0x09    // NVM — READ ONLY!
#define TARGET_CH    0       // Channel 0 only

// Go Configure export — 256 bytes (converted from bit-level)
const uint8_t gc_config[256] PROGMEM = {
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0x00
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0x10
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0x20
  0x00, 0x00, 0x00, 0x00, 0xC0, 0xFC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0x30
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x80, 0x00, // 0x40
  0x00, 0x00, 0x08, 0x04, 0x00, 0x00, 0x02, 0x00, 0x00, 0xE0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0x50
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0x60
  0x2F, 0x2F, 0x08, 0x00, 0x40, 0x40, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, // 0x70
  0xA5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00, // 0x80
  0x00, 0x83, 0xC1, 0x60, 0x30, 0x00, 0x6C, 0x00, 0x81, 0x15, 0x00, 0x00, 0x20, 0x00, 0x20, 0x00, // 0x90
  0x20, 0x00, 0x20, 0x00, 0x20, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0xE7, 0x03, 0x00, 0x01, 0x00, // 0xA0
  0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0xB0
  0xFF, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0xC0
  0xFF, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0xD0
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0xE0
  0x5A, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00  // 0xF0
};

// Bytes to ALWAYS preserve from factory NVM (I2C config, power, etc.)
// These ranges will use factory values, NOT Go Configure values
const uint8_t PRESERVE_START_1 = 0xDA;  // I2C slave address region
const uint8_t PRESERVE_END_1   = 0xDF;
const uint8_t PRESERVE_START_2 = 0xF0;  // Boot/control region
const uint8_t PRESERVE_END_2   = 0xFF;

uint8_t factory_nvm[256];
uint8_t merged[256];

void selectMuxChannel(uint8_t ch) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << ch);
  Wire.endTransmission();
}

bool readPage(uint8_t i2cAddr, uint8_t startAddr, uint8_t* buf, uint8_t len) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(startAddr);
  if (Wire.endTransmission() != 0) return false;
  Wire.requestFrom(i2cAddr, len);
  for (uint8_t i = 0; i < len; i++) {
    if (!Wire.available()) return false;
    buf[i] = Wire.read();
  }
  return true;
}

bool writeByte(uint8_t i2cAddr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(reg);
  Wire.write(val);
  return (Wire.endTransmission() == 0);
}

uint8_t readByte(uint8_t i2cAddr, uint8_t reg) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(i2cAddr, (uint8_t)1);
  return Wire.available() ? Wire.read() : 0xFF;
}

bool isPreserved(uint8_t addr) {
  return (addr >= PRESERVE_START_1 && addr <= PRESERVE_END_1) ||
         (addr >= PRESERVE_START_2 && addr <= PRESERVE_END_2);
}

void hexDump(const char* label, uint8_t* data, int len) {
  Serial.println(label);
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

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);

  Serial.println(F("============================================="));
  Serial.println(F("  Board 3 — RAM Programmer (Channel 0)"));
  Serial.println(F("  Design: OSC1→CNT0→GPIO5 = 1024 Hz"));
  Serial.println(F("  RAM ONLY — power cycle to restore factory"));
  Serial.println(F("============================================="));
  Serial.println();

  // Select channel
  selectMuxChannel(TARGET_CH);
  delay(10);

  // Verify GreenPAK present
  Wire.beginTransmission(GP_REG_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println(F("ERROR: No GreenPAK on channel 0!"));
    while(1);
  }
  Serial.println(F("✓ GreenPAK found on channel 0"));

  // Step 1: Read factory NVM
  Serial.println(F("\nStep 1: Reading factory NVM..."));
  for (int page = 0; page < 16; page++) {
    if (!readPage(GP_NVM_ADDR, page * 16, &factory_nvm[page * 16], 16)) {
      Serial.print(F("  ERROR reading page "));
      Serial.println(page);
      while(1);
    }
  }
  Serial.println(F("  ✓ Factory NVM read"));
  
  // Step 2: Merge — our design + factory preserved bytes
  Serial.println(F("\nStep 2: Merging config (preserving I2C bytes)..."));
  for (int i = 0; i < 256; i++) {
    if (isPreserved(i)) {
      merged[i] = factory_nvm[i];
    } else {
      merged[i] = pgm_read_byte(&gc_config[i]);
    }
  }

  // Show what we're preserving
  Serial.print(F("  Factory 0xDA-0xDF: "));
  for (int i = 0xDA; i <= 0xDF; i++) {
    if (factory_nvm[i] < 0x10) Serial.print("0");
    Serial.print(factory_nvm[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print(F("  Factory 0xF0-0xFF: "));
  for (int i = 0xF0; i <= 0xFF; i++) {
    if (factory_nvm[i] < 0x10) Serial.print("0");
    Serial.print(factory_nvm[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
  Serial.println(F("  ✓ Merged (factory I2C bytes preserved)"));

  // Step 3: Write merged config to RAM
  Serial.println(F("\nStep 3: Writing to RAM..."));
  int writeCount = 0;
  int skipCount = 0;
  int errorCount = 0;

  for (int i = 0; i < 256; i++) {
    // Read current RAM value
    uint8_t current = readByte(GP_REG_ADDR, i);
    
    if (current == merged[i]) {
      skipCount++;
      continue;  // Already correct
    }

    // Write new value
    if (!writeByte(GP_REG_ADDR, i, merged[i])) {
      Serial.print(F("  WRITE FAIL at 0x"));
      Serial.println(i, HEX);
      errorCount++;
      continue;
    }
    
    delay(2);  // settle

    // Verify
    uint8_t verify = readByte(GP_REG_ADDR, i);
    if (verify != merged[i]) {
      Serial.print(F("  VERIFY FAIL at 0x"));
      Serial.print(i, HEX);
      Serial.print(F(": wrote 0x"));
      Serial.print(merged[i], HEX);
      Serial.print(F(", read 0x"));
      Serial.println(verify, HEX);
      errorCount++;
    } else {
      writeCount++;
    }
  }

  Serial.print(F("  Written: "));
  Serial.print(writeCount);
  Serial.print(F("  Skipped: "));
  Serial.print(skipCount);
  Serial.print(F("  Errors: "));
  Serial.println(errorCount);

  // Step 4: Final verification — dump RAM
  Serial.println(F("\nStep 4: Final RAM dump for verification:"));
  uint8_t final_ram[256];
  for (int page = 0; page < 16; page++) {
    readPage(GP_REG_ADDR, page * 16, &final_ram[page * 16], 16);
  }
  hexDump("RAM contents:", final_ram, 256);

  // Step 5: Verify NVM untouched
  Serial.println(F("Step 5: Verifying NVM unchanged..."));
  uint8_t nvm_check[256];
  for (int page = 0; page < 16; page++) {
    readPage(GP_NVM_ADDR, page * 16, &nvm_check[page * 16], 16);
  }
  bool nvmOk = true;
  for (int i = 0; i < 256; i++) {
    if (nvm_check[i] != factory_nvm[i]) {
      Serial.print(F("  NVM CHANGED at 0x"));
      Serial.print(i, HEX);
      Serial.print(F(": was 0x"));
      Serial.print(factory_nvm[i], HEX);
      Serial.print(F(", now 0x"));
      Serial.println(nvm_check[i], HEX);
      nvmOk = false;
    }
  }
  if (nvmOk) {
    Serial.println(F("  ✓ NVM unchanged — factory config safe!"));
  }

  // Disable mux
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0);
  Wire.endTransmission();

  Serial.println(F("\n============================================="));
  if (errorCount == 0) {
    Serial.println(F("  ✓ Programming complete!"));
    Serial.println(F("  Probe Pin 19 (GPIO5) with scope"));
    Serial.println(F("  Expected: 1024 Hz square wave"));
  } else {
    Serial.print(F("  ⚠ Completed with "));
    Serial.print(errorCount);
    Serial.println(F(" errors"));
  }
  Serial.println(F("  Power cycle to restore factory config"));
  Serial.println(F("============================================="));
}

void loop() {}
