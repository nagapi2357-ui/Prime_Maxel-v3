/*
 * SLG47004V NVM Programmer for Prime_Maxel-v3
 * 
 * Programs GreenPAK chips via I2C through TCA9548A mux.
 * 
 * Usage:
 *   1. Upload this sketch to Arduino Mega
 *   2. Open Serial Monitor at 9600 baud
 *   3. Follow menu prompts to read/write NVM
 *
 * The SLG47004V has 4 I2C address spaces per device:
 *   Base+0 (0x08): Register space (active config)
 *   Base+1 (0x09): NVM space (stored config)
 *   Base+2 (0x0A): EEPROM space
 *   Base+3 (0x0B): Reserved
 *
 * NVM is 256 bytes, written in 16-byte pages.
 * After writing NVM, device must be reset to load new config.
 */

#include <Wire.h>

#define MUX_ADDR     0x70    // TCA9548A address
#define GP_REG_ADDR  0x08    // GreenPAK register space
#define GP_NVM_ADDR  0x09    // GreenPAK NVM space
#define GP_EE_ADDR   0x0A    // GreenPAK EEPROM space

#define NVM_SIZE     256     // bytes
#define PAGE_SIZE    16      // bytes per NVM page

// NVM data buffer
uint8_t nvmData[NVM_SIZE];

void selectMuxChannel(uint8_t channel) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void disableMux() {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0);
  Wire.endTransmission();
}

// Read 256 bytes from a GreenPAK address space
bool readGreenPAK(uint8_t i2cAddr, uint8_t* buffer) {
  for (int page = 0; page < NVM_SIZE / PAGE_SIZE; page++) {
    uint8_t startAddr = page * PAGE_SIZE;
    
    Wire.beginTransmission(i2cAddr);
    Wire.write(startAddr);
    if (Wire.endTransmission() != 0) return false;
    
    Wire.requestFrom(i2cAddr, (uint8_t)PAGE_SIZE);
    for (int i = 0; i < PAGE_SIZE; i++) {
      if (Wire.available()) {
        buffer[startAddr + i] = Wire.read();
      } else {
        return false;
      }
    }
  }
  return true;
}

// Erase NVM (write all 0x00)
bool eraseNVM(uint8_t i2cAddr) {
  Serial.println("Erasing NVM...");
  for (int page = 0; page < NVM_SIZE / PAGE_SIZE; page++) {
    uint8_t startAddr = page * PAGE_SIZE;
    
    Wire.beginTransmission(i2cAddr);
    Wire.write(startAddr);
    for (int i = 0; i < PAGE_SIZE; i++) {
      Wire.write((uint8_t)0x00);
    }
    if (Wire.endTransmission() != 0) {
      Serial.print("Erase failed at page ");
      Serial.println(page);
      return false;
    }
    delay(50); // Wait for NVM write cycle
  }
  Serial.println("Erase complete.");
  return true;
}

// Write 256 bytes to NVM in 16-byte pages
bool writeNVM(uint8_t i2cAddr, uint8_t* data) {
  Serial.println("Writing NVM...");
  for (int page = 0; page < NVM_SIZE / PAGE_SIZE; page++) {
    uint8_t startAddr = page * PAGE_SIZE;
    
    Wire.beginTransmission(i2cAddr);
    Wire.write(startAddr);
    for (int i = 0; i < PAGE_SIZE; i++) {
      Wire.write(data[startAddr + i]);
    }
    if (Wire.endTransmission() != 0) {
      Serial.print("Write failed at page ");
      Serial.println(page);
      return false;
    }
    delay(50); // Wait for NVM write cycle
    
    // Progress indicator
    if (page % 4 == 0) {
      Serial.print(".");
    }
  }
  Serial.println("\nWrite complete.");
  return true;
}

// Verify NVM by reading back and comparing
bool verifyNVM(uint8_t i2cAddr, uint8_t* expectedData) {
  uint8_t readback[NVM_SIZE];
  Serial.println("Verifying NVM...");
  
  if (!readGreenPAK(i2cAddr, readback)) {
    Serial.println("Read-back failed!");
    return false;
  }
  
  int errors = 0;
  for (int i = 0; i < NVM_SIZE; i++) {
    if (readback[i] != expectedData[i]) {
      Serial.print("Mismatch at 0x");
      Serial.print(i, HEX);
      Serial.print(": expected 0x");
      Serial.print(expectedData[i], HEX);
      Serial.print(", got 0x");
      Serial.println(readback[i], HEX);
      errors++;
      if (errors > 10) {
        Serial.println("Too many errors, aborting verify.");
        return false;
      }
    }
  }
  
  if (errors == 0) {
    Serial.println("Verify OK — all 256 bytes match!");
    return true;
  }
  return false;
}

// Reset GreenPAK to reload NVM into registers
void resetGreenPAK(uint8_t regAddr) {
  Serial.println("Resetting GreenPAK (reload NVM -> registers)...");
  Wire.beginTransmission(regAddr);
  Wire.write(0xC8);  // POR reset register
  Wire.write(0x02);  // Trigger reset
  Wire.endTransmission();
  delay(100);  // Wait for POR sequence
  Serial.println("Reset complete.");
}

// Print hex dump of buffer
void hexDump(uint8_t* data, int len) {
  for (int i = 0; i < len; i++) {
    if (i % 16 == 0) {
      Serial.print("0x");
      if (i < 0x10) Serial.print("0");
      Serial.print(i, HEX);
      Serial.print(": ");
    }
    if (data[i] < 0x10) Serial.print("0");
    Serial.print(data[i], HEX);
    Serial.print(" ");
    if (i % 16 == 15) Serial.println();
  }
  if (len % 16 != 0) Serial.println();
}

// Parse hex string from Serial into nvmData buffer
// Expects 512 hex characters (256 bytes)
bool parseHexFromSerial() {
  Serial.println("Paste 512 hex characters (256 bytes) now:");
  Serial.println("(or type 'cancel' to abort)");
  
  int byteIndex = 0;
  int nibbleCount = 0;
  uint8_t currentByte = 0;
  unsigned long timeout = millis() + 60000; // 60 second timeout
  
  while (byteIndex < NVM_SIZE && millis() < timeout) {
    if (Serial.available()) {
      char c = Serial.read();
      
      // Check for cancel
      if (c == 'c' || c == 'C') {
        Serial.println("Cancelled.");
        return false;
      }
      
      // Skip whitespace, colons, newlines
      if (c == ' ' || c == ':' || c == '\n' || c == '\r' || c == '\t') continue;
      
      // Parse hex nibble
      uint8_t nibble;
      if (c >= '0' && c <= '9') nibble = c - '0';
      else if (c >= 'a' && c <= 'f') nibble = c - 'a' + 10;
      else if (c >= 'A' && c <= 'F') nibble = c - 'A' + 10;
      else continue; // skip non-hex
      
      if (nibbleCount % 2 == 0) {
        currentByte = nibble << 4;
      } else {
        currentByte |= nibble;
        nvmData[byteIndex++] = currentByte;
      }
      nibbleCount++;
    }
  }
  
  if (byteIndex == NVM_SIZE) {
    Serial.print("Received ");
    Serial.print(byteIndex);
    Serial.println(" bytes.");
    return true;
  } else {
    Serial.print("Timeout — only received ");
    Serial.print(byteIndex);
    Serial.println(" bytes.");
    return false;
  }
}

void printMenu() {
  Serial.println();
  Serial.println("========================================");
  Serial.println("  Prime_Maxel-v3 GreenPAK Programmer");
  Serial.println("========================================");
  Serial.println("  r <ch>  — Read NVM from channel (0-5)");
  Serial.println("  R <ch>  — Read REGISTERS from channel");
  Serial.println("  w <ch>  — Write NVM to channel (0-5)");
  Serial.println("  e <ch>  — Erase NVM on channel");
  Serial.println("  x <ch>  — Reset GreenPAK on channel");
  Serial.println("  s       — Scan all channels");
  Serial.println("  h       — Show this menu");
  Serial.println("========================================");
  Serial.println("Enter command:");
}

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);
  
  printMenu();
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    
    // Skip whitespace
    while (Serial.available() && Serial.peek() == ' ') Serial.read();
    
    int channel = -1;
    if (Serial.available()) {
      channel = Serial.parseInt();
    }
    
    // Flush remaining input
    while (Serial.available()) Serial.read();
    
    switch (cmd) {
      case 'r': { // Read NVM
        if (channel < 0 || channel > 5) {
          Serial.println("Usage: r <channel 0-5>");
          break;
        }
        Serial.print("Reading NVM from channel ");
        Serial.println(channel);
        selectMuxChannel(channel);
        if (readGreenPAK(GP_NVM_ADDR, nvmData)) {
          hexDump(nvmData, NVM_SIZE);
        } else {
          Serial.println("Read failed!");
        }
        disableMux();
        break;
      }
      
      case 'R': { // Read registers
        if (channel < 0 || channel > 5) {
          Serial.println("Usage: R <channel 0-5>");
          break;
        }
        Serial.print("Reading registers from channel ");
        Serial.println(channel);
        selectMuxChannel(channel);
        if (readGreenPAK(GP_REG_ADDR, nvmData)) {
          hexDump(nvmData, NVM_SIZE);
        } else {
          Serial.println("Read failed!");
        }
        disableMux();
        break;
      }
      
      case 'w': { // Write NVM
        if (channel < 0 || channel > 5) {
          Serial.println("Usage: w <channel 0-5>");
          break;
        }
        Serial.print("Programming channel ");
        Serial.println(channel);
        
        if (!parseHexFromSerial()) break;
        
        selectMuxChannel(channel);
        
        // Erase first
        if (!eraseNVM(GP_NVM_ADDR)) {
          Serial.println("Erase failed! Aborting.");
          disableMux();
          break;
        }
        
        // Write
        if (!writeNVM(GP_NVM_ADDR, nvmData)) {
          Serial.println("Write failed!");
          disableMux();
          break;
        }
        
        // Verify
        if (!verifyNVM(GP_NVM_ADDR, nvmData)) {
          Serial.println("WARNING: Verification failed!");
        }
        
        // Reset to load new config
        resetGreenPAK(GP_REG_ADDR);
        
        disableMux();
        Serial.println("Programming complete!");
        break;
      }
      
      case 'e': { // Erase NVM
        if (channel < 0 || channel > 5) {
          Serial.println("Usage: e <channel 0-5>");
          break;
        }
        Serial.print("Erasing NVM on channel ");
        Serial.println(channel);
        selectMuxChannel(channel);
        eraseNVM(GP_NVM_ADDR);
        disableMux();
        break;
      }
      
      case 'x': { // Reset
        if (channel < 0 || channel > 5) {
          Serial.println("Usage: x <channel 0-5>");
          break;
        }
        selectMuxChannel(channel);
        resetGreenPAK(GP_REG_ADDR);
        disableMux();
        break;
      }
      
      case 's': { // Scan all channels
        Serial.println("Scanning all channels...\n");
        for (uint8_t ch = 0; ch < 8; ch++) {
          selectMuxChannel(ch);
          Serial.print("Channel ");
          Serial.print(ch);
          Serial.print(": ");
          
          int count = 0;
          for (byte addr = 1; addr < 127; addr++) {
            if (addr == MUX_ADDR) continue;
            Wire.beginTransmission(addr);
            if (Wire.endTransmission() == 0) {
              Serial.print("0x");
              Serial.print(addr, HEX);
              Serial.print(" ");
              count++;
            }
          }
          if (count == 0) Serial.print("(empty)");
          Serial.println();
        }
        disableMux();
        break;
      }
      
      case 'h':
      case '?':
        printMenu();
        break;
        
      case '\n':
      case '\r':
        break; // ignore newlines
        
      default:
        Serial.print("Unknown command: ");
        Serial.println(cmd);
        printMenu();
        break;
    }
  }
}
