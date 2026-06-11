/*
 * Board 3 — GreenPAK RAM Write Test
 * 
 * Tests RAM read/write on Channel 0 GreenPAK.
 * Writes to a SAFE register region (0x00-0x7E are all zeros in factory config).
 * Reads back to verify. Then restores original value.
 * 
 * I2C addresses:
 *   0x08 = Active registers (RAM) — read/write
 *   0x09 = NVM — DO NOT WRITE
 *   0x0A = EEPROM
 * 
 * SAFETY: Only writes to 0x08 (RAM). Power cycle resets everything.
 */

#include <Wire.h>

#define MUX_ADDR     0x70
#define GP_REG_ADDR  0x08    // RAM (active registers)
#define GP_NVM_ADDR  0x09    // NVM — read only!

// Test register in the "user" area (0x00-0x7E, all zeros in factory)
// Using 0x40 — deep in the zero region, unlikely to affect chip behavior
#define TEST_REG     0x40
#define TEST_VALUE   0xA5

void selectMuxChannel(uint8_t ch) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << ch);
  Wire.endTransmission();
}

uint8_t readReg(uint8_t i2cAddr, uint8_t reg) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(i2cAddr, (uint8_t)1);
  return Wire.available() ? Wire.read() : 0xFF;
}

bool writeReg(uint8_t i2cAddr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(i2cAddr);
  Wire.write(reg);
  Wire.write(val);
  return (Wire.endTransmission() == 0);
}

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);

  Serial.println(F("============================================="));
  Serial.println(F("  Board 3 — GreenPAK RAM Write Test"));
  Serial.println(F("============================================="));
  Serial.println();

  // Test each channel
  for (uint8_t ch = 0; ch < 6; ch++) {
    selectMuxChannel(ch);
    delay(10);

    Serial.print(F("--- Channel "));
    Serial.print(ch);
    Serial.println(F(" ---"));

    // Step 1: Read original value from RAM
    uint8_t original = readReg(GP_REG_ADDR, TEST_REG);
    Serial.print(F("  RAM[0x"));
    Serial.print(TEST_REG, HEX);
    Serial.print(F("] original: 0x"));
    Serial.println(original, HEX);

    // Step 2: Also read same offset from NVM for comparison
    uint8_t nvmVal = readReg(GP_NVM_ADDR, TEST_REG);
    Serial.print(F("  NVM[0x"));
    Serial.print(TEST_REG, HEX);
    Serial.print(F("] value:    0x"));
    Serial.println(nvmVal, HEX);

    // Step 3: Write test value to RAM
    Serial.print(F("  Writing 0x"));
    Serial.print(TEST_VALUE, HEX);
    Serial.print(F(" to RAM[0x"));
    Serial.print(TEST_REG, HEX);
    Serial.print(F("]... "));

    if (writeReg(GP_REG_ADDR, TEST_REG, TEST_VALUE)) {
      Serial.println(F("OK"));
    } else {
      Serial.println(F("FAILED!"));
      continue;
    }

    delay(5);  // settle

    // Step 4: Read back
    uint8_t readback = readReg(GP_REG_ADDR, TEST_REG);
    Serial.print(F("  Readback: 0x"));
    Serial.print(readback, HEX);

    if (readback == TEST_VALUE) {
      Serial.println(F("  ✓ RAM WRITE WORKS!"));
    } else if (readback == original) {
      Serial.println(F("  ✗ Write had no effect (read-only register?)"));
    } else {
      Serial.print(F("  ? Unexpected value (wrote 0x"));
      Serial.print(TEST_VALUE, HEX);
      Serial.print(F(", got 0x"));
      Serial.print(readback, HEX);
      Serial.println(F(")"));
    }

    // Step 5: Verify NVM was NOT modified
    uint8_t nvmCheck = readReg(GP_NVM_ADDR, TEST_REG);
    Serial.print(F("  NVM unchanged: 0x"));
    Serial.print(nvmCheck, HEX);
    if (nvmCheck == nvmVal) {
      Serial.println(F("  ✓ NVM safe"));
    } else {
      Serial.println(F("  ✗ NVM CHANGED! STOP!"));
    }

    // Step 6: Restore original value
    writeReg(GP_REG_ADDR, TEST_REG, original);
    delay(5);
    uint8_t restored = readReg(GP_REG_ADDR, TEST_REG);
    Serial.print(F("  Restored: 0x"));
    Serial.print(restored, HEX);
    if (restored == original) {
      Serial.println(F("  ✓ Restored"));
    } else {
      Serial.println(F("  ? Restore mismatch"));
    }

    Serial.println();
  }

  // Disable mux
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0);
  Wire.endTransmission();

  Serial.println(F("============================================="));
  Serial.println(F("  Test complete. Power cycle to fully reset."));
  Serial.println(F("============================================="));
}

void loop() {}
