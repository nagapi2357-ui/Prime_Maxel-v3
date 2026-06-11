/*
 * Even Divisor Frequency Set — Prime_Maxel-v3
 * 
 * Divisors: {2, 4, 6, 8, 10, 12} — all even integers
 * Heavily non-coprime: every pair shares factor 2
 *   gcd(2,4)=2, gcd(4,8)=4, gcd(6,12)=6, gcd(4,12)=4, etc.
 * Maximum shared-factor density of any set tested.
 *
 *   Pin 22: f₀/2  = 512 Hz
 *   Pin 24: f₀/4  = 256 Hz
 *   Pin 26: f₀/6  = 171 Hz
 *   Pin 28: f₀/8  = 128 Hz
 *   Pin 30: f₀/10 = 102 Hz
 *   Pin 32: f₀/12 = 85 Hz
 *
 * Coprimality: ZERO coprime pairs (all share factor 2)
 */

#define NUM_CHANNELS 6

const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };
const uint8_t divisors[NUM_CHANNELS] = { 2, 4, 6, 8, 10, 12 };

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
  Serial.println(F("=== Even Divisors: f₀/{2,4,6,8,10,12} ==="));
  Serial.println(F("All even — zero coprime pairs"));

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
