/*
 * Random Control Frequency Set — Prime_Maxel-v3
 * 
 * 6 frequencies with NO mathematical relationship, chosen by
 * random draw from 200-550 Hz range (same band as zeta sets).
 * Seed: numpy.random.seed(42), randint(200,550,6), sorted.
 *
 *   Pin 22: 221 Hz
 *   Pin 24: 303 Hz
 *   Pin 26: 349 Hz
 *   Pin 28: 412 Hz
 *   Pin 30: 471 Hz
 *   Pin 32: 523 Hz
 *
 * GCD structure: gcd(221,303)=1, gcd(303,349)=1, gcd(349,412)=1,
 *   gcd(412,471)=1, gcd(471,523)=1 — accidentally mostly coprime
 *   (integers drawn at random tend to be coprime with prob 6/π²≈61%)
 *   but NOT derived from any prime/zeta structure.
 *
 * Method: Timer1 at 50 kHz ISR, per-channel toggle thresholds.
 */

#define NUM_CHANNELS 6
#define TIMER_FREQ 50000UL

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };

// Toggle thresholds: TIMER_FREQ / (2 * freq)
const uint16_t toggleAt[NUM_CHANNELS] = {
  113,  // 50000/(2*221) ≈ 113.1  → 221.2 Hz
   83,  // 50000/(2*303) ≈ 82.5   → 301.2 Hz
   72,  // 50000/(2*349) ≈ 71.6   → 347.2 Hz
   61,  // 50000/(2*412) ≈ 60.7   → 409.8 Hz
   53,  // 50000/(2*471) ≈ 53.1   → 471.7 Hz
   48   // 50000/(2*523) ≈ 47.8   → 520.8 Hz
};

volatile uint16_t counters[NUM_CHANNELS];
volatile uint8_t pinState[NUM_CHANNELS];

ISR(TIMER1_COMPA_vect) {
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    if (++counters[i] >= toggleAt[i]) {
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
  Serial.println(F("=== Random Control Freq Set ==="));
  Serial.println(F("No mathematical structure — random draw 200-550 Hz"));
  Serial.println(F("Freqs: 221, 301, 347, 410, 472, 521 Hz (approx)"));

  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    pinMode(outPins[i], OUTPUT);
    digitalWrite(outPins[i], LOW);
    counters[i] = 0;
    pinState[i] = 0;
  }

  noInterrupts();
  TCCR1A = 0; TCCR1B = 0; TCNT1 = 0;
  OCR1A = 319;
  TCCR1B |= (1 << WGM12) | (1 << CS10);
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
