// Board 3 GreenPAK Channel Scanner
// Scans TCA9548A mux (0x70) channels 0-5 for GreenPAK at 0x08
// Also scans top-level bus first for the mux itself

#include <Wire.h>

#define MUX_ADDR 0x70
#define GREENPAK_ADDR 0x08
#define NUM_CHANNELS 6

void selectMuxChannel(uint8_t ch) {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << ch);
  Wire.endTransmission();
}

void disableMux() {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0);
  Wire.endTransmission();
}

bool probeAddress(uint8_t addr) {
  Wire.beginTransmission(addr);
  return (Wire.endTransmission() == 0);
}

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial);

  Serial.println(F("============================================="));
  Serial.println(F("  Board 3 — GreenPAK Channel Scanner"));
  Serial.println(F("============================================="));
  Serial.println();

  // Step 1: Check mux on top-level bus
  Serial.print(F("TCA9548A at 0x70: "));
  if (probeAddress(MUX_ADDR)) {
    Serial.println(F("FOUND ✓"));
  } else {
    Serial.println(F("NOT FOUND ✗ — check wiring!"));
    Serial.println(F("HALTING."));
    while(1);
  }

  Serial.println();
  Serial.println(F("Scanning mux channels 0-5 for GreenPAK (0x08)..."));
  Serial.println();

  int found = 0;
  for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
    selectMuxChannel(ch);
    delay(10);  // settle time

    Serial.print(F("  Channel "));
    Serial.print(ch);
    Serial.print(F(": "));

    if (probeAddress(GREENPAK_ADDR)) {
      Serial.println(F("GreenPAK at 0x08 ✓"));
      found++;
    } else {
      // Scan wider range in case address differs
      bool altFound = false;
      for (uint8_t a = 0x01; a < 0x78; a++) {
        if (a == MUX_ADDR) continue;
        if (probeAddress(a)) {
          Serial.print(F("Device at 0x"));
          if (a < 16) Serial.print(F("0"));
          Serial.print(a, HEX);
          Serial.println(F(" (not 0x08!)"));
          altFound = true;
        }
      }
      if (!altFound) {
        Serial.println(F("NO DEVICE ✗"));
      }
    }
  }

  disableMux();

  Serial.println();
  Serial.print(found);
  Serial.print(F("/"));
  Serial.print(NUM_CHANNELS);
  Serial.println(F(" GreenPAKs responding."));

  if (found == NUM_CHANNELS) {
    Serial.println(F("\n🎉 All 6 GreenPAKs alive! Ready for NVM dump."));
  } else {
    Serial.println(F("\n⚠️  Not all chips responding — investigate before continuing."));
  }

  Serial.println(F("\nDone. Reset to scan again."));
}

void loop() {
  // One-shot — reset Mega to re-run
}
