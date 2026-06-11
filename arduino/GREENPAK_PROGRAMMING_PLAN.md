# GreenPAK Programming Plan — V3 Board

## Overview

The SLG47004V has **three internal oscillators**:
- **OSC0:** 2.048 kHz (RC oscillator, low power)
- **OSC1:** 2.048 MHz (RC oscillator)
- **OSC2:** 25 MHz (Ring oscillator)

And **seven counter/delay macrocells**:
- **CNT0–CNT5:** 8-bit counter/delay (values 1–256)
- **CNT6:** 16-bit counter/delay (values 1–65536)

Each counter divides its clock source by (Counter_Data + 1) in toggle mode, giving a square wave at:
`f_out = f_osc / (2 × (Counter_Data + 1))`

Or in one-shot/edge mode, just divides by Counter_Data.

## Oscillator Strategy

### Option A: Use OSC1 (2.048 MHz) + CNT6 (16-bit)
- Most flexibility: 16-bit gives us divisors up to 65536
- Can hit a wide range of frequencies with good precision
- f_out = 2,048,000 / (2 × N)

### Option B: Use OSC0 (2.048 kHz) + 8-bit counters
- Simpler, lower power
- Limited range: 2048 / (2 × N), N = 1..256
- Max output: 1024 Hz, Min: ~4 Hz
- Not enough resolution for prime ratios

### Option C: Use OSC2 (25 MHz) + cascaded counters
- Highest precision but overkill for audio-range frequencies
- More complex config

**Recommendation: Option A (OSC1 + CNT6)**

## Frequency Calculations

### Base frequency choice
We want f₀ such that all six prime-ratio frequencies are achievable with integer divisors from 2.048 MHz.

For f_out = 2,048,000 / (2 × N), we need N to be an integer.

Let's pick **f₀ = 1024 Hz** (nice power of 2, divides from 2.048 MHz perfectly):
- f₀ = 2,048,000 / (2 × 1000) = 1024 Hz when N = 1000

Actually, let's think differently. We want exact RATIOS between cells, not exact absolute frequencies. So pick f₀ to make all divisors integers.

The six cells need frequencies in ratio 1/13 : 1/11 : 1/7 : 1/5 : 1/3 : 1/1

If f₀ = f_base, then:
- N6 (1/1): f₀
- N5 (1/3): f₀/3
- N4 (1/5): f₀/5
- N3 (1/7): f₀/7
- N2 (1/11): f₀/11
- N1 (1/13): f₀/13

For the divisor from OSC1:
N_cell = 2,048,000 / (2 × f_cell) = 1,024,000 / f_cell

We need N_cell to be an integer for each cell.

f_cell values: f₀, f₀/3, f₀/5, f₀/7, f₀/11, f₀/13

So 1,024,000 / f₀ must be an integer, AND:
1,024,000 / (f₀/3) = 3 × 1,024,000/f₀ must be ≤ 65536 (16-bit limit)
1,024,000 / (f₀/13) = 13 × 1,024,000/f₀ must be ≤ 65536

Let K = 1,024,000 / f₀. Then largest divisor = 13K ≤ 65536, so K ≤ 5041.
And f₀ = 1,024,000 / K.

We want K to be an integer. Some nice choices:
- K = 1000 → f₀ = 1024 Hz, largest N = 13000 ✓ (fits 16-bit)
- K = 2000 → f₀ = 512 Hz, largest N = 26000 ✓
- K = 4000 → f₀ = 256 Hz, largest N = 52000 ✓
- K = 5000 → f₀ = 204.8 Hz, largest N = 65000 ✓

**Best choice: K = 1000, f₀ = 1024 Hz**
- Easy to see on scope
- All divisors fit in 16-bit
- Lowest frequency (1024/13 ≈ 78.8 Hz) is above DC, easily measurable

### Config A Frequencies

| Cell | Ch | Ratio | Frequency | CNT6 Divisor (N) | Exact f_out |
|------|-----|-------|-----------|-------------------|-------------|
| N6 | 5 | 1/1 | 1024 Hz | 1000 | 1024.000 Hz |
| N5 | 4 | 1/3 | 341.3 Hz | 3000 | 341.333 Hz |
| N4 | 3 | 1/5 | 204.8 Hz | 5000 | 204.800 Hz |
| N3 | 2 | 1/7 | 146.3 Hz | 7000 | 146.286 Hz |
| N2 | 1 | 1/11 | 93.1 Hz | 11000 | 93.091 Hz |
| N1 | 0 | 1/13 | 78.8 Hz | 13000 | 78.769 Hz |

All ratios are EXACT because the divisors are exact multiples (1000 × prime).

## Output Pin

Each SLG47004V has 8 GPIOs. We need to route the CNT6 output to a GPIO.
The schematic shows the GreenPAK output connects to the LM324 op-amp circuit.
Need to check which pin in the golden_cell schematic is used for the GreenPAK output signal.

## Programming Method

### Two approaches:

**Approach 1: Go Configure (recommended for first time)**
1. Design the config visually in Go Configure
2. Export NVM as .hex file
3. Program via I2C from Arduino

**Approach 2: Direct register writes from Arduino**
1. Read current NVM to understand default state
2. Modify specific bits for oscillator, counter, output routing
3. Write back to NVM
4. Reset chip to load new config

Approach 1 is safer and better documented. We should use it.

### I2C Programming Protocol (SLG47004V MTP)

The SLG47004V has 4 I2C address spaces (control codes), which is why each chip shows at 4 addresses:
- **0x08:** Register read/write (active configuration)
- **0x09:** NVM read/write
- **0x0A:** EEPROM read/write
- **0x0B:** Reserved/control

To program:
1. Write 256 bytes to NVM space (address 0x09) in 16-byte pages
2. Reset the device (write to register 0xC8 at address 0x08) to reload from NVM
3. Verify by reading registers at address 0x08

### Arduino Programmer Sketch

See `nvm_programmer/nvm_programmer.ino` — reads .hex data from Serial, programs each GreenPAK through the TCA9548A mux.

## Channel → Cell Mapping

Need to determine which TCA9548A channel corresponds to which physical cell position.
Currently we know channels 0–5 all have GreenPAKs.
Physical mapping TBD (may need to test by toggling GPIO and probing test points).

## Golden Cell Signal Flow

From the schematic (golden_cell.kicad_sch):
- **U3** = SLG47004V (GreenPAK) at center-right of cell
- **U2** = LM324DRE4 (quad op-amp) at center-left of cell
- **OA0_OUT** (pin 5) = SLG47004V's internal op-amp output — this is the main signal output
- The GreenPAK's OA0_OUT connects to the LM324 bridge circuit
- The LM324 outputs feed **TORSION_A** and **TORSION_B** (the ring traces)
- **PULSE_IN** feeds into the cell (external trigger)
- **VREF_MID** provides the voltage reference
- **14 of 24 pins are no-connect** — most GPIOs unused
- Only connected: VDD, GND (power), SCL/SDA (I2C), OA0_OUT, and a few others

### Key Design Implication
The signal path uses the GreenPAK's **internal op-amp (OA0)**, NOT a GPIO.
So in Go Configure, we need to:
1. Route the oscillator → counter → OA0 output buffer
2. The OA0 output drives through the LM324 to the torsion ring

This is more elegant than a GPIO square wave — the op-amp can shape the waveform.

## Arduino Sketches Created

| Sketch | Purpose |
|--------|---------|
| `nvm_reader/` | Read & dump NVM from all 6 GreenPAKs (run first!) |
| `nvm_programmer/` | Interactive programmer — read/write/erase/reset per channel |
| `channel_scanner/` | Scan TCA9548A channels for devices |
| `i2c_scanner/` | Basic I2C bus scan |

## Next Steps

1. ✅ Determine oscillator + divider strategy (OSC1 2.048MHz + CNT6 16-bit)
2. ✅ Check golden_cell schematic — signal goes through OA0_OUT (pin 5)
3. ✅ Build Arduino NVM reader sketch
4. ✅ Build Arduino NVM programmer sketch
5. 🔜 **Run NVM reader** — dump factory defaults from all 6 chips (IMPORTANT!)
6. 🔜 **Install Go Configure** — design base oscillator config
7. 🔜 Design oscillator → CNT6 → OA0 output in Go Configure
8. 🔜 Export 6 .hex files with different CNT6 divider values
9. 🔜 Program all 6 GreenPAKs using nvm_programmer
10. 🔜 Verify output frequencies with scope
