/*
 * Zeta Zero SPACING Frequency Set — Prime_Maxel-v3
 * 
 * Frequencies derived from GAPS between consecutive zeta zeros:
 *   Δ₁ = γ₂−γ₁ = 6.887    Δ₂ = γ₃−γ₂ = 3.989
 *   Δ₃ = γ₄−γ₃ = 5.414    Δ₄ = γ₅−γ₄ = 2.510
 *   Δ₅ = γ₆−γ₅ = 4.651    Δ₆ = γ₇−γ₆ = 3.333
 *
 * These spacings follow GUE (Gaussian Unitary Ensemble) statistics
 * from random matrix theory — eigenvalue repulsion.
 *
 * Normalized to Δ₄ (smallest) and scaled to ~200 Hz base:
 *   Pin 22: 200.0 Hz  (Δ₄ = 2.510 — base)
 *   Pin 24: 265.9 Hz  (Δ₆/Δ₄ = 1.328)
 *   Pin 26: 316.5 Hz  (Δ₂/Δ₄ = 1.589)
 *   Pin 28: 373.1 Hz  (Δ₅/Δ₄ = 1.853)
 *   Pin 30: 431.0 Hz  (Δ₃/Δ₄ = 2.157)
 *   Pin 32: 543.5 Hz  (Δ₁/Δ₄ = 2.744)
 *
 * Method: Timer1 at 50 kHz ISR, per-channel toggle thresholds.
 */

#define NUM_CHANNELS 6
#define TIMER_FREQ 50000UL

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };

// Toggle thresholds: TIMER_FREQ / (2 * target_freq)
const uint16_t toggleAt[NUM_CHANNELS] = {
  125,  // 50000/(2*200.0) = 125   → 200.0 Hz exact
   94,  // 50000/(2*265.9) ≈ 94.0  → 266.0 Hz
   79,  // 50000/(2*316.5) ≈ 78.6  → 316.5 Hz
   67,  // 50000/(2*373.1) ≈ 67.4  → 373.1 Hz
   58,  // 50000/(2*431.0) ≈ 58.0  → 431.0 Hz
   46   // 50000/(2*543.5) ≈ 45.5  → 543.5 Hz
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
  Serial.println(F("=== Zeta Zero SPACING Freq Set ==="));
  Serial.println(F("Gaps between consecutive zeros (GUE statistics)"));
  Serial.println(F("Deltas: 6.887, 3.989, 5.414, 2.510, 4.651, 3.333"));
  Serial.println(F("Freqs: 200.0, 266.0, 316.5, 373.1, 431.0, 543.5 Hz"));

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
