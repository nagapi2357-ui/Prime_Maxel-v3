# SLG47004V GreenPAK — Internal Blocks & Capabilities

## Overview
The SLG47004V is an **AnalogPAK** — a programmable mixed-signal IC in a 3×3mm STQFN-24 package. It's one of the more analog-heavy GreenPAKs, with op-amps, rheostats, and analog switches alongside the standard digital logic.

## Key Internal Blocks

### Oscillators (3 types)
1. **RC OSC (OSC0)** — Low-frequency, 2.048 kHz (default)
   - Low power, always available
   - Can be sourced from GPIO1 instead (external clock input)
   - This is the primary clock for all CNT/DLY blocks
   
2. **LF OSC** — Low-frequency oscillator (alternate)

3. **Ring OSC (OSC1)** — High-frequency, ~25 MHz
   - Can be sourced from GPIO4 instead (external clock input)
   - Higher power consumption

### Counters/Delays (CNT/DLY) — 7 blocks!
- **CNT0/DLY0 through CNT6/DLY6**
- Each can be configured as:
  - **Counter** — counts clock edges, outputs pulse at terminal count
  - **Delay** — one-shot delay from trigger
  - **Frequency detect** — outputs HIGH if input frequency exceeds threshold
- Counter data is programmable (stored in NVM)
- Clock source: OSC0 (2.048 kHz) or OSC1 (25 MHz) or external
- **Can be used as frequency dividers!**

### D Flip-Flops (DFFs) — 18 blocks
- Standard edge-triggered flip-flops
- Can create toggle (÷2) dividers by connecting Q̅ → D
- Chain multiple for ÷4, ÷8, ÷16 etc.

### Look-Up Tables (LUTs) — 20 blocks
- 2, 3, or 4-input configurable logic
- Can implement any boolean function
- Use for signal routing, gating, combining

### Pattern Generator — 1 block
- 16-stage pipe delay
- Can generate complex output patterns
- Clocked by OSC0 or OSC1

### Op-Amps — 2 blocks (OPAMP0, OPAMP1)
- Programmable bandwidth (up to 8 MHz)
- Rail-to-rail input
- 125 dB open-loop gain
- Can be configured as: amplifier, comparator, buffer, bandpass filter
- **Already connected to external components on the v3 board (the LM324 replacement path)**

### Digital Rheostats — 2 blocks (RH0, RH1)
- 10-bit resolution (1024 steps)
- Can be controlled via I2C dynamically
- Great for adjustable filter parameters

### Analog Comparators (ACMPs) — 3 blocks
- Programmable hysteresis
- Can trigger digital events from analog thresholds

### Analog Switches — 2 blocks
- Route analog signals between pins

### GPIO — 8 pins
- Configurable as input, output, or analog function
- Each pin has a configurable output source from the matrix

### Other
- **Temperature sensor** (1 channel)
- **Voltage reference** (VDD/2 or other programmable levels)
- **I2C interface** — for programming and dynamic control
- **EEPROM** — 256 bytes of user data
- **Auto-Trim** — can periodically adjust rheostat to compensate for drift

## Frequency Generation Strategies for Prime Ratios

### Strategy A: Internal Oscillator + Counter Dividers
- OSC0 at 2.048 kHz → CNT/DLY configured as dividers
- 2048 / 2 = 1024 Hz (f₀/1) ✅
- 2048 / 6 = 341.3 Hz (f₀/3) ✅  
- 2048 / 10 = 204.8 Hz (f₀/5) ✅
- 2048 / 14 = 146.3 Hz (f₀/7) ✅
- 2048 / 22 = 93.1 Hz (f₀/11) ✅
- 2048 / 26 = 78.8 Hz (f₀/13) ✅
- **Problem: Only 7 CNT/DLY blocks, but we need 6 frequencies = 6 dividers per chip**
- **Each GreenPAK chip could generate ONE frequency** (one divider per chip)
- This works! Each of the 6 GreenPAKs generates its own prime frequency from the shared 2.048 kHz oscillator

### Strategy B: External Clock from Mega + Internal Dividers
- Mega provides a 2048 Hz master clock to one GPIO
- GreenPAK divides it using CNT/DLY blocks
- Same math as Strategy A but clock comes from outside
- Advantage: can change master frequency dynamically

### Strategy C: DFF Toggle Chain
- Feed OSC0 into a chain of DFFs configured as T flip-flops
- Each stage divides by 2: 2048 → 1024 → 512 → 256 → 128 → 64
- Only gives power-of-2 divisions — NOT suitable for prime ratios
- Could combine with LUT logic for odd divisors but gets complex

### Strategy D: Op-Amp Oscillator (Wien Bridge)
- Use the internal op-amps to build analog oscillators
- Frequency set by rheostat + external capacitors
- Can generate sine waves (not just square waves!)
- Application note AN-CM-324 shows exactly this with SLG47004
- **Problem: v3 board's external components are fixed — would need different R/C values**

## Recommended Approach: Strategy A (One Frequency Per Chip)

Each GreenPAK generates one prime-ratio frequency:
- GreenPAK on Ch 0 (U3): 2048/2 = 1024 Hz
- GreenPAK on Ch 1 (U5): 2048/6 = 341.3 Hz
- GreenPAK on Ch 2 (U7): 2048/10 = 204.8 Hz
- GreenPAK on Ch 3 (U9): 2048/14 = 146.3 Hz
- GreenPAK on Ch 4 (U11): 2048/22 = 93.1 Hz
- GreenPAK on Ch 5 (U13): 2048/26 = 78.8 Hz

### Configuration per chip:
1. Enable OSC0 (2.048 kHz) — may already be enabled in factory config
2. Configure one CNT/DLY as counter with appropriate divider value
3. Route counter output to the GPIO pin connected to the paired LM324 input
4. All other blocks can be powered down to minimize noise

### Advantages over Mega Direct Drive:
- **Cleaner signal** — no bodge wires, shorter signal path
- **Independent timing** — each chip has its own oscillator, no ISR jitter
- **Lower impedance output** — GreenPAK GPIO vs Mega GPIO
- **All internal to the PCB** — proper routing, proper ground planes
- **Dynamically adjustable** — can change divider values via I2C without re-flashing

### What we need to figure out:
1. Which GPIO pin on the SLG47004V connects to the LM324 1IN+ on the v3 PCB?
2. What's the factory NVM config for OSC0? (check the dump we have)
3. How to write to RAM registers via I2C (register map needed)
4. Can we use Go Configure to design the config and export register values?

## I2C Register Map Summary
- **NVM space:** Addresses 0x00-0xFF (256 bytes = 2048 bits)
- **EEPROM space:** Separate 256-byte block  
- **RAM space:** Live registers, same layout as NVM but volatile
- **Register 0xE3:** NVM erase control — **DO NOT TOUCH**
- **I2C slave address bits:** Located in NVM — erasing NVM resets these!
- To write RAM only: use the RAM register address space (different I2C sub-address range)

## Go Configure Software
- Already installed: `go-configure-sw-hub-v6.53.001-mac.dmg`
- Has simulation capability
- Can export NVM data as hex or bit-level file
- Existing project: `V3 Board SLG47004V.aap` — this is JLCPCB's factory config!

## Safety Checklist for Board 3
- [ ] Dump factory NVM before any writes
- [ ] Identify I2C address bits in NVM dump
- [ ] Only write to RAM registers (volatile)
- [ ] Verify with scope after each change
- [ ] Keep Go Configure project file as reference
- [ ] Do NOT issue NVM erase (0xE3) commands
- [ ] Power down unused analog blocks to reduce noise
