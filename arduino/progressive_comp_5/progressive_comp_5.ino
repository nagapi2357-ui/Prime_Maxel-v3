/*
 * Progressive Composite Addition #5 — Prime_Maxel-v3
 * EXPERIMENT: 5 composite frequencies active: f₀/4, f₀/6, f₀/8, f₀/9, f₀/10
 *
 *   Pin 22: f₀/4 = 256.0 Hz (ACTIVE)
 *   Pin 24: f₀/6 = 170.7 Hz (ACTIVE)
 *   Pin 26: f₀/8 = 128.0 Hz (ACTIVE)
 *   Pin 28: f₀/9 = 113.8 Hz (ACTIVE)
 *   Pin 30: f₀/10 = 102.4 Hz (ACTIVE)
 *   Pin 32: OFF
 */

#define NUM_CHANNELS 6

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };
const uint8_t divisors[NUM_CHANNELS] = { 4, 6, 8, 9, 10, 0 };

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
  Serial.println(F("=== PROG COMP #5: f₀/4, f₀/6, f₀/8, f₀/9, f₀/10 ==="));
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    pinMode(outPins[i], OUTPUT);
    digitalWrite(outPins[i], LOW);
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
