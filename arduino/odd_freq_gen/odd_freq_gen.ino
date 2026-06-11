/*
 * Odd Divisor Frequency Set — Prime_Maxel-v3
 * 
 * Divisors: {1, 3, 5, 7, 9, 11} — all odd integers
 * Contains all primes up to 11 PLUS composite 9 (=3²)
 * Connection: sum of first k odds = k² (squares from odds)
 * Tusk Series holds for any nonce but breaks on odd-only series
 *
 *   Pin 22: f₀/1  = 1024 Hz
 *   Pin 24: f₀/3  = 341 Hz
 *   Pin 26: f₀/5  = 205 Hz
 *   Pin 28: f₀/7  = 146 Hz
 *   Pin 30: f₀/9  = 114 Hz  ← COMPOSITE (3²)
 *   Pin 32: f₀/11 = 93 Hz
 *
 * Coprimality: most pairs coprime EXCEPT gcd(3,9)=3
 */

#define NUM_CHANNELS 6

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };
const uint8_t divisors[NUM_CHANNELS] = { 1, 3, 5, 7, 9, 11 };

volatile uint8_t counters[NUM_CHANNELS];
volatile uint8_t pinState[NUM_CHANNELS];

ISR(TIMER1_COMPA_vect) {
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
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
  Serial.println(F("=== Odd Divisors: f₀/{1,3,5,7,9,11} ==="));
  Serial.println(F("All odd — primes + 9(=3²)"));

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
