/*
 * twin_primes — Prime_Maxel-v3
 * Twin prime pairs: (5,7)(11,13)(17,19) — 6k±1 structure
 * Coprimality: 100%
 *
 *   Pin 22: f₀/5 = 204.8 Hz (ACTIVE)
 *   Pin 24: f₀/7 = 146.3 Hz (ACTIVE)
 *   Pin 26: f₀/11 = 93.1 Hz (ACTIVE)
 *   Pin 28: f₀/13 = 78.8 Hz (ACTIVE)
 *   Pin 30: f₀/17 = 60.2 Hz (ACTIVE)
 *   Pin 32: f₀/19 = 53.9 Hz (ACTIVE)
 */

#define NUM_CHANNELS 6
const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };
const uint8_t divisors[NUM_CHANNELS] = { 5, 7, 11, 13, 17, 19 };
volatile uint8_t counters[NUM_CHANNELS];
volatile uint8_t pinState[NUM_CHANNELS];

ISR(TIMER1_COMPA_vect) {
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    if (divisors[i] == 0) continue;
    counters[i]++;
    if (counters[i] >= divisors[i]) {
      counters[i] = 0;
      pinState[i] ^= 1;
      if (pinState[i]) {
        *portOutputRegister(digitalPinToPort(outPins[i])) |= digitalPinToBitMask(outPins[i]);
      } else {
        *portOutputRegister(digitalPinToPort(outPins[i])) &= ~digitalPinToBitMask(outPins[i]);
      }
    }
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println(F("=== twin_primes: f₀/5, f₀/7, f₀/11, f₀/13, f₀/17, f₀/19 ==="));
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    pinMode(outPins[i], OUTPUT); digitalWrite(outPins[i], LOW);
    counters[i] = 0; pinState[i] = 0;
  }
  noInterrupts();
  TCCR1A = 0; TCCR1B = 0; TCNT1 = 0;
  OCR1A = 976;
  TCCR1B |= (1 << WGM12) | (1 << CS11);
  TIMSK1 |= (1 << OCIE1A);
  interrupts();
  Serial.println(F("Running."));
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'S' || c == 's') { TIMSK1 &= ~(1 << OCIE1A); Serial.println(F("Stopped.")); }
    else if (c == 'R' || c == 'r') { TIMSK1 |= (1 << OCIE1A); Serial.println(F("Restarted.")); }
  }
}
