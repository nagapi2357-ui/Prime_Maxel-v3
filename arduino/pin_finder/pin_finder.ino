/*
 * Pin Finder v2 — Interactive
 * 
 * Type an Arduino pin number (22-53) in Serial Monitor and hit Send.
 * That pin goes HIGH (5V) and stays HIGH until you type a different pin.
 * The previous pin goes LOW automatically.
 * 
 * Type 'off' or '0' to turn everything off.
 * 
 * Use scope or multimeter to find which physical header position
 * matches the Arduino pin number.
 */

int currentPin = -1;

void allOff() {
  for (int p = 22; p <= 53; p++) {
    digitalWrite(p, LOW);
  }
  currentPin = -1;
}

void setup() {
  Serial.begin(9600);
  
  for (int p = 22; p <= 53; p++) {
    pinMode(p, OUTPUT);
    digitalWrite(p, LOW);
  }
  
  Serial.println(F("========================================"));
  Serial.println(F("  Pin Finder v2 — Interactive"));
  Serial.println(F("========================================"));
  Serial.println(F("Type a pin number (22-53) and hit Send."));
  Serial.println(F("That pin goes HIGH until you type another."));
  Serial.println(F("Type '0' to turn all off."));
  Serial.println();
  Serial.println(F("Map these 6 pins for the freq generator:"));
  Serial.println(F("  22, 24, 26, 28, 30, 32"));
  Serial.println();
  Serial.println(F("Ready — type a pin number:"));
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    int pin = input.toInt();
    
    if (pin == 0) {
      allOff();
      Serial.println(F("All pins OFF."));
      Serial.println();
      Serial.println(F("Type a pin number (22-53):"));
      return;
    }
    
    if (pin >= 22 && pin <= 53) {
      allOff();
      digitalWrite(pin, HIGH);
      currentPin = pin;
      Serial.print(F(">>> Arduino Pin "));
      Serial.print(pin);
      Serial.println(F(" is now HIGH (5V)"));
      Serial.println(F("    Find it on the header with your scope."));
      Serial.println(F("    Type next pin number when ready."));
      Serial.println();
    } else {
      Serial.print(F("Invalid: '"));
      Serial.print(input);
      Serial.println(F("' — enter 22-53 or 0 for off."));
    }
  }
}
