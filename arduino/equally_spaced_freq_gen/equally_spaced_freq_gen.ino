/*
 * Equally Spaced (Structureless) Control — Prime_Maxel-v3
 * 
 * 6 frequencies with ZERO mathematical structure — equal 70 Hz steps.
 * No coprimality, no prime ratios, no zeta structure.
 * The true null hypothesis: "I know nothing about frequency selection."
 *
 *   Pin 22: 200 Hz
 *   Pin 24: 270 Hz
 *   Pin 26: 340 Hz
 *   Pin 28: 410 Hz
 *   Pin 30: 480 Hz
 *   Pin 32: 550 Hz
 *
 * Ratios: 20:27:34:41:48:55 — dense with shared factors
 *   gcd(200,270)=10, gcd(270,340)=10, gcd(340,410)=10,
 *   gcd(200,340)=20, gcd(270,480)=30, gcd(200,550)=50
 *
 * Method: Timer1 at 50 kHz ISR, per-channel toggle thresholds.
 */

#define NUM_CHANNELS 6
#define TIMER_FREQ 50000UL

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };

// Toggle thresholds: TIMER_FREQ / (2 * freq)
const uint16_t toggleAt[NUM_CHANNELS] = {
  125,  // 50000/(2*200) = 125.0  → 200.0 Hz exact
   93,  // 50000/(2*270) ≈ 92.6   → 268.8 Hz
   74,  // 50000/(2*340) ≈ 73.5   → 337.8 Hz
   61,  // 50000/(2*410) ≈ 61.0   → 409.8 Hz
   52,  // 50000/(2*480) ≈ 52.1   → 480.8 Hz
   45   // 50000/(2*550) ≈ 45.5   → 555.6 Hz
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
  Serial.println(F("=== Equally Spaced (Structureless) Control ==="));
  Serial.println(F("Zero mathematical structure — 70 Hz equal steps"));
  Serial.println(F("Freqs: 200, 269, 338, 410, 481, 556 Hz (approx)"));

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
