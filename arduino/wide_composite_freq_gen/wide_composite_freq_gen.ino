/*
 * Wide-Bandwidth Composite Frequency Generator — Prime_Maxel-v3
 * EXPERIMENT: Matched-bandwidth composite — same range as primes (1024 down to 85 Hz)
 * but using composite (non-coprime) divisors.
 *
 *   Pin 22: f₀/1  = 1024.0 Hz  (included to match prime set bandwidth)
 *   Pin 24: f₀/4  = 256.0 Hz
 *   Pin 26: f₀/6  = 170.7 Hz
 *   Pin 28: f₀/8  = 128.0 Hz
 *   Pin 30: f₀/10 = 102.4 Hz
 *   Pin 32: f₀/12 = 85.3 Hz
 *
 * Divisors {1,4,6,8,10,12} share many common factors:
 *   gcd(4,6)=2, gcd(4,8)=4, gcd(6,8)=2, gcd(8,10)=2, gcd(10,12)=2, gcd(6,12)=6, etc.
 * vs primes {1,3,5,7,11,13} where gcd of any pair = 1.
 */

#define NUM_CHANNELS 6

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };
const uint8_t divisors[NUM_CHANNELS] = { 1, 4, 6, 8, 10, 12 };
const float freqs[NUM_CHANNELS] = { 1024.0, 256.0, 170.67, 128.0, 102.40, 85.33 };

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
  Serial.println(F("=== WIDE COMPOSITE: f0/{1,4,6,8,10,12} ==="));
  
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    pinMode(outPins[i], OUTPUT);
    digitalWrite(outPins[i], LOW);
    counters[i] = 0;
    pinState[i] = 0;
    Serial.print(F("  Pin ")); Serial.print(outPins[i]);
    Serial.print(F(": f0/")); Serial.print(divisors[i]);
    Serial.print(F(" = ")); Serial.print(freqs[i], 1);
    Serial.println(F(" Hz"));
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
