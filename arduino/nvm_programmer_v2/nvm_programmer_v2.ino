/*
 * SLG47004V NVM Programmer — Prime_Maxel-v3
 * 
 * Programs all 6 GreenPAKs with the oscillator+counter config
 * exported from Go Configure, with per-cell counter divisors
 * for prime-ratio frequencies.
 * 
 * Signal path: OSC1 (2.048 MHz) → CNT0 (16-bit, toggle) → GPIO0 (Pin 12) → LM324
 * 
 * Base config exported from Go Configure (cell_1024Hz)
 * Counter data bytes at NVM offset 0xAB (low) and 0xAC (high)
 * 
 * Channel → Frequency mapping:
 *   Ch 0: f₀/13 =  78.8 Hz  (N=13000)
 *   Ch 1: f₀/11 =  93.1 Hz  (N=11000)
 *   Ch 2: f₀/7  = 146.3 Hz  (N=7000)
 *   Ch 3: f₀/5  = 204.8 Hz  (N=5000)
 *   Ch 4: f₀/3  = 341.3 Hz  (N=3000)
 *   Ch 5: f₀/1  = 1024.0 Hz (N=1000)
 * 
 * NOTE: Channel-to-physical-cell mapping TBD — may need to 
 * remap after testing with scope.
 */

#include <Wire.h>

#define MUX_ADDR     0x70
#define GP_REG_ADDR  0x08
#define GP_NVM_ADDR  0x09

// Base NVM image from Go Configure export (256 bytes)
// Counter data at offset 0xAB=0xE8, 0xAC=0x03 (1000 = 0x03E8)
const uint8_t baseNVM[256] PROGMEM = {
  // 0x00
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0x10
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0x20
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0xCC, 0x0F, 0x00,
  // 0x30
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0x40
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x80, 0x00,
  // 0x50
  0x00, 0x00, 0x08, 0x04, 0x00, 0x00, 0x01, 0x00,
  0x00, 0xE0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0x60
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0x70
  0x2F, 0x2F, 0x08, 0x00, 0x40, 0x40, 0x04, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01,
  // 0x80
  0xA5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00,
  // 0x90
  0x00, 0x80, 0xC1, 0x60, 0x30, 0x18, 0x6C, 0x00,
  0x81, 0x15, 0x00, 0x00, 0x20, 0x00, 0x20, 0x00,
  // 0xA0
  0x20, 0x00, 0x20, 0x00, 0x20, 0x00, 0x20, 0x00,
  0x00, 0x00, 0x00, 0xE8, 0x03, 0x00, 0x01, 0x00,
  // 0xB0
  0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00,
  0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0xC0
  0xFF, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0xD0
  0xFF, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0xE0
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  // 0xF0
  0x5A, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

// Counter data byte offset in NVM
#define CNT_DATA_LO  0xAB
#define CNT_DATA_HI  0xAC

// Per-channel counter divisors (prime ratios)
const uint16_t divisors[6] = {
  13000,  // Ch 0: f₀/13 =  78.8 Hz
  11000,  // Ch 1: f₀/11 =  93.1 Hz
   7000,  // Ch 2: f₀/7  = 146.3 Hz
   5000,  // Ch 3: f₀/5  = 204.8 Hz
   3000,  // Ch 4: f₀/3  = 341.3 Hz
   1000   // Ch 5: f₀/1  = 1024.0 Hz
};

const float freqs[6] = { 78.8, 93.1, 146.3, 204.8, 341.3, 1024.0 };

uint8_t nvmBuf[256];

void selectMuxChannel(uint8_t channel) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

bool eraseNVMPage(uint8_t page) {
  // Erase register at 0xE3: ERSE[2:0]=110 (bits 7:5) + page number (bits 4:0)
  // 0b110_xxxxx | page = 0xC0 | page
  uint8_t eraseCmd = 0xC0 | (page & 0x1F);
  Wire.beginTransmission(GP_REG_ADDR);
  Wire.write(0xE3);
  Wire.write(eraseCmd);
  if (Wire.endTransmission() != 0) return false;
  delay(50);  // Wait for erase cycle (tER)
  return true;
}

bool eraseNVM() {
  // Erase all 16 NVM pages (pages 0-15)
  for (uint8_t page = 0; page < 16; page++) {
    if (!eraseNVMPage(page)) return false;
  }
  return true;
}

bool writeNVMPage(uint8_t startAddr, uint8_t* data, uint8_t len) {
  Wire.beginTransmission(GP_NVM_ADDR);
  Wire.write(startAddr);
  for (uint8_t i = 0; i < len; i++) {
    Wire.write(data[i]);
  }
  if (Wire.endTransmission() != 0) return false;
  delay(50);  // Wait for NVM write
  return true;
}

bool writeFullNVM(uint8_t* data) {
  // Write 256 bytes in 16-byte pages
  for (int page = 0; page < 16; page++) {
    if (!writeNVMPage(page * 16, &data[page * 16], 16)) {
      return false;
    }
  }
  return true;
}

bool readNVM(uint8_t* buf) {
  for (int page = 0; page < 256 / 16; page++) {
    uint8_t startAddr = page * 16;
    Wire.beginTransmission(GP_NVM_ADDR);
    Wire.write(startAddr);
    if (Wire.endTransmission() != 0) return false;
    Wire.requestFrom(GP_NVM_ADDR, (uint8_t)16);
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

bool resetChip() {
  // Software reset: set bit 0 of register byte 0x7B (bit [984]) to 1
  // This triggers POR sequence — reloads all registers from NVM
  Wire.beginTransmission(GP_REG_ADDR);
  Wire.write(0x7B);
  Wire.write(0x01);
  if (Wire.endTransmission() != 0) return false;
  delay(200);  // Wait for POR sequence
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

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);
  
  Serial.println("=============================================");
  Serial.println("  Prime_Maxel-v3 GreenPAK NVM Programmer");
  Serial.println("  OSC1 → CNT0 → GPIO0 (Pin 12) → LM324");
  Serial.println("=============================================");
  Serial.println();
  Serial.println("This will program all 6 GreenPAKs with");
  Serial.println("prime-ratio frequencies.");
  Serial.println();
  Serial.println("Send 'Y' to proceed, anything else to abort.");
  
  while (!Serial.available());
  char c = Serial.read();
  if (c != 'Y' && c != 'y') {
    Serial.println("Aborted.");
    return;
  }
  
  Serial.println();
  Serial.println("Programming...");
  Serial.println();
  
  int successCount = 0;
  
  for (uint8_t ch = 0; ch < 6; ch++) {
    selectMuxChannel(ch);
    delay(10);
    
    Serial.print("=== Channel ");
    Serial.print(ch);
    Serial.print(": ");
    Serial.print(freqs[ch], 1);
    Serial.print(" Hz (N=");
    Serial.print(divisors[ch]);
    Serial.println(") ===");
    
    // Check if GreenPAK responds
    Wire.beginTransmission(GP_REG_ADDR);
    if (Wire.endTransmission() != 0) {
      Serial.println("  ERROR: No GreenPAK found!");
      continue;
    }
    Serial.println("  GreenPAK found.");
    
    // Prepare NVM image with this channel's counter value
    for (int i = 0; i < 256; i++) {
      nvmBuf[i] = pgm_read_byte(&baseNVM[i]);
    }
    nvmBuf[CNT_DATA_LO] = divisors[ch] & 0xFF;
    nvmBuf[CNT_DATA_HI] = (divisors[ch] >> 8) & 0xFF;
    
    Serial.print("  Counter bytes: 0x");
    if (nvmBuf[CNT_DATA_LO] < 0x10) Serial.print("0");
    Serial.print(nvmBuf[CNT_DATA_LO], HEX);
    Serial.print(" 0x");
    if (nvmBuf[CNT_DATA_HI] < 0x10) Serial.print("0");
    Serial.println(nvmBuf[CNT_DATA_HI], HEX);
    
    // Step 1: Erase NVM
    Serial.print("  Erasing NVM... ");
    if (!eraseNVM()) {
      Serial.println("FAILED!");
      continue;
    }
    Serial.println("OK");
    
    // Step 2: Write NVM
    Serial.print("  Writing NVM... ");
    if (!writeFullNVM(nvmBuf)) {
      Serial.println("FAILED!");
      continue;
    }
    Serial.println("OK");
    
    // Step 3: Verify by reading back
    Serial.print("  Verifying... ");
    uint8_t verifyBuf[256];
    if (!readNVM(verifyBuf)) {
      Serial.println("READ FAILED!");
      continue;
    }
    
    bool match = true;
    int mismatches = 0;
    for (int i = 0; i < 256; i++) {
      if (verifyBuf[i] != nvmBuf[i]) {
        match = false;
        mismatches++;
        if (mismatches <= 5) {
          Serial.print("  MISMATCH at 0x");
          Serial.print(i, HEX);
          Serial.print(": wrote 0x");
          Serial.print(nvmBuf[i], HEX);
          Serial.print(", read 0x");
          Serial.println(verifyBuf[i], HEX);
        }
      }
    }
    
    if (match) {
      Serial.println("OK — verified!");
      successCount++;
    } else {
      Serial.print("FAILED — ");
      Serial.print(mismatches);
      Serial.println(" byte mismatches!");
    }
    
    // Step 4: Reset chip to load new config
    Serial.print("  Resetting chip... ");
    if (!resetChip()) {
      Serial.println("FAILED!");
    } else {
      Serial.println("OK");
    }
    
    Serial.println();
  }
  
  // Disable mux
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0);
  Wire.endTransmission();
  
  Serial.println("=============================================");
  Serial.print("  Done! ");
  Serial.print(successCount);
  Serial.println("/6 programmed successfully.");
  Serial.println("=============================================");
  
  if (successCount == 6) {
    Serial.println();
    Serial.println("All chips programmed! Connect scope to LM324");
    Serial.println("outputs to verify frequencies.");
  }
}

void loop() {
  // Nothing — run once
}
