/*
 * Zeta Zero Frequency Set — Prime_Maxel-v3
 * 
 * Injects 6 frequencies whose RATIOS match the first 6
 * non-trivial Riemann zeta function zeros (imaginary parts):
 *   γ₁=14.135, γ₂=21.022, γ₃=25.011, γ₄=30.425, γ₅=32.935, γ₆=37.586
 *
 * Normalized to γ₁ and scaled to ~200 Hz base:
 *   Pin 22: 200.0 Hz  (γ₁ — base)
 *   Pin 24: 297.6 Hz  (γ₂/γ₁ = 1.487)
 *   Pin 26: 352.1 Hz  (γ₃/γ₁ = 1.770)  [target 354, ≤0.5% err]
 *   Pin 28: 431.0 Hz  (γ₄/γ₁ = 2.152)
 *   Pin 30: 462.9 Hz  (γ₅/γ₁ = 2.330)  [target 466, ≤0.7% err]
 *   Pin 32: 531.9 Hz  (γ₆/γ₁ = 2.660)
 *
 * Method: Timer1 at 50 kHz ISR, per-channel toggle thresholds.
 * Unlike integer-divisor sketches, this uses independent counters
 * to achieve non-integer frequency ratios (irrational in theory).
 */

#define NUM_CHANNELS 6
#define TIMER_FREQ 50000UL  // 50 kHz tick rate

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };

// Toggle thresholds: TIMER_FREQ / (2 * target_freq), rounded to nearest int
// Each pin toggles every N ticks → freq = TIMER_FREQ / (2*N)
const uint16_t toggleAt[NUM_CHANNELS] = {
  125,  // 50000/(2*200.0) = 125   → 200.0 Hz exact
   84,  // 50000/(2*297.6) ≈ 84.04 → 297.6 Hz
   71,  // 50000/(2*352.1) ≈ 70.62 → 352.1 Hz
   58,  // 50000/(2*431.0) ≈ 58.00 → 431.0 Hz
   54,  // 50000/(2*462.9) ≈ 53.65 → 462.9 Hz
   47   // 50000/(2*531.9) ≈ 47.01 → 531.9 Hz
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
  Serial.println(F("=== Zeta Zero Freq Set ==="));
  Serial.println(F("Ratios from first 6 non-trivial zeros of zeta(s)"));
  Serial.println(F("gamma: 14.135, 21.022, 25.011, 30.425, 32.935, 37.586"));
  Serial.println(F("Freqs: 200.0, 297.6, 352.1, 431.0, 462.9, 531.9 Hz"));

  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    pinMode(outPins[i], OUTPUT);
    digitalWrite(outPins[i], LOW);
    counters[i] = 0;
    pinState[i] = 0;
  }

  // Timer1: CTC mode, prescaler=1, 50 kHz
  // OCR1A = 16MHz / (1 * 50000) - 1 = 319
  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  OCR1A = 319;
  TCCR1B |= (1 << WGM12) | (1 << CS10);  // CTC, no prescaler
  TIMSK1 |= (1 << OCIE1A);
  interrupts();

  Serial.println(F("Running."));
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'S' || c == 's') {
      TIMSK1 &= ~(1 << OCIE1A);
      Serial.println(F("Stopped."));
    } else if (c == 'R' || c == 'r') {
      TIMSK1 |= (1 << OCIE1A);
      Serial.println(F("Restarted."));
    }
  }
}
