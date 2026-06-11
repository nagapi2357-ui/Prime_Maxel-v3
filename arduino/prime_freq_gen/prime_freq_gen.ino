/*
 * Prime Ratio Frequency Generator — Prime_Maxel-v3
 * 
 * Generates 6 prime-ratio square wave frequencies simultaneously
 * using Timer interrupts on Arduino Mega.
 * 
 * Bodge wire each output pin to an LM324 pin 3 (1IN+) on the board.
 * The LM324 buffers/amplifies the signal into the torsion ring.
 * 
 * Base frequency: f₀ = 1024 Hz
 * Frequencies: f₀/1, f₀/3, f₀/5, f₀/7, f₀/11, f₀/13
 * 
 * Uses Timer1 (16-bit) as master timebase at high frequency,
 * with software dividers for each channel.
 * 
 * Output pins (choose Arduino Mega digital pins with easy access):
 *   Pin 22: f₀/1  = 1024.0 Hz
 *   Pin 24: f₀/3  = 341.3 Hz  
 *   Pin 26: f₀/5  = 204.8 Hz
 *   Pin 28: f₀/7  = 146.3 Hz
 *   Pin 30: f₀/11 = 93.1 Hz
 *   Pin 32: f₀/13 = 78.8 Hz
 * 
 * (Using even-numbered pins on the double-row header for easy access)
 */

#define NUM_CHANNELS 6

// Output pins (Mega digital pins on the double-row header)
const uint8_t outPins[NUM_CHANNELS] = { 22, 24, 26, 28, 30, 32 };

// Prime divisors
const uint8_t primeDivisors[NUM_CHANNELS] = { 1, 3, 5, 7, 11, 13 };

// Frequencies for display
const float freqs[NUM_CHANNELS] = { 1024.0, 341.33, 204.80, 146.29, 93.09, 78.77 };

// Software counters — count up to divisor, then toggle
volatile uint8_t counters[NUM_CHANNELS];
volatile uint8_t pinState[NUM_CHANNELS];

/*
 * Timer1 strategy:
 * We need the master tick at 2 × f₀ = 2048 Hz (toggle rate for 1024 Hz)
 * Timer1 in CTC mode, 16MHz / prescaler / compare = 2048 Hz
 * 
 * 16,000,000 / 8 / 977 = 2047.08 Hz ≈ 2048 Hz  (prescaler=8, OCR1A=976)
 * Or: 16,000,000 / 64 / 122 = 2049.18 Hz        (prescaler=64, OCR1A=121)  
 * Or: 16,000,000 / 1 / 7813 = 2048.03 Hz         (prescaler=1, OCR1A=7812)
 * 
 * Best: prescaler=8, OCR1A=976 → 2048.13 Hz (0.006% error)
 * 
 * At each tick (2048 Hz), the f₀/1 channel toggles.
 * The f₀/3 channel toggles every 3 ticks (2048/3 Hz toggle = 341.33 Hz)
 * The f₀/5 channel toggles every 5 ticks, etc.
 */

ISR(TIMER1_COMPA_vect) {
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    counters[i]++;
    if (counters[i] >= primeDivisors[i]) {
      counters[i] = 0;
      pinState[i] ^= 1;
      // Direct port manipulation for speed
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
  
  Serial.println(F("============================================="));
  Serial.println(F("  Prime Ratio Frequency Generator"));
  Serial.println(F("  V3 Board — Arduino Direct Drive"));
  Serial.println(F("============================================="));
  Serial.println();
  
  // Configure output pins
  for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
    pinMode(outPins[i], OUTPUT);
    digitalWrite(outPins[i], LOW);
    counters[i] = 0;
    pinState[i] = 0;
    
    Serial.print(F("  Pin "));
    Serial.print(outPins[i]);
    Serial.print(F(": f₀/"));
    Serial.print(primeDivisors[i]);
    Serial.print(F(" = "));
    Serial.print(freqs[i], 1);
    Serial.println(F(" Hz"));
  }
  
  Serial.println();
  Serial.println(F("Bodge wire each pin to an LM324 pin 3 (1IN+)"));
  Serial.println(F("LM324 is SOIC-14: pin 3 is 3rd from top-left"));
  Serial.println();
  
  // Configure Timer1 for 2048 Hz interrupt
  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  OCR1A = 976;              // 16MHz / 8 / 977 ≈ 2048 Hz
  TCCR1B |= (1 << WGM12);  // CTC mode
  TCCR1B |= (1 << CS11);   // Prescaler = 8
  TIMSK1 |= (1 << OCIE1A); // Enable compare interrupt
  interrupts();
  
  Serial.println(F("Timer started! Frequencies running."));
  Serial.println(F("Measure with scope to verify."));
  Serial.println();
  Serial.println(F("Send 'S' to stop, 'R' to restart."));
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'S' || c == 's') {
      TIMSK1 &= ~(1 << OCIE1A);  // Disable interrupt
      for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
        digitalWrite(outPins[i], LOW);
      }
      Serial.println(F("Stopped."));
    }
    else if (c == 'R' || c == 'r') {
      for (uint8_t i = 0; i < NUM_CHANNELS; i++) {
        counters[i] = 0;
        pinState[i] = 0;
      }
      TIMSK1 |= (1 << OCIE1A);  // Re-enable interrupt
      Serial.println(F("Restarted."));
    }
  }
}
