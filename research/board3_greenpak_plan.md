# Board 3 — GreenPAK Bring-Up Plan

## Board Inventory
- Board 1: DOA (fab damage)
- Board 2: Active bench board — GreenPAKs bricked, bodge wires for Mega direct drive, all torsion measurements done here
- **Board 3: FRESH** — factory GreenPAKs intact ← THIS ONE
- Board 4: Spare
- Board 5: Spare

## Golden Rules ⚠️
1. **ONLY power via Mega USB** — barrel jack feeds power back into Mega
2. **NEVER 12V** — fries GreenPAK chips
3. **NO NVM ERASE** until we fully understand write protection
4. **RAM-ONLY programming first** — volatile, safe, resets on power cycle
5. **Dump factory NVM first** — before touching anything
6. **One chip at a time** — verify each step before moving to next

## Phase 1: Verification (Day 1)

### Step 1: Power up, I2C scan
- Plug Mega USB only
- Run `i2c_scanner.ino` 
- Verify TCA9548A responds at 0x70
- Select each mux channel (0-5), scan for GreenPAK (expect 0x08)
- **STOP if any channel doesn't respond** — investigate before continuing

### Step 2: Factory NVM dump
- Run `nvm_reader.ino` on all 6 channels
- Save as `factory_nvm_dump_board3_YYYY-MM-DD.txt`
- Compare with Board 2's factory dump — should be identical (same JLCPCB batch)
- **This is our insurance policy**

### Step 3: Read GreenPAK register map
- Dump all register pages (NVM, EEPROM, RAM)
- Document the factory I2C slave address bits (which NVM offset?)
- Document any write protection bits
- Understand what's at 0xE3 (erase control register)

## Phase 2: RAM Programming (Day 2)

### Step 4: Design prime frequency config
- SLG47004V internal blocks available:
  - RC oscillator (configurable frequency)
  - Counter/dividers (programmable)
  - LUT (look-up tables for logic)
  - Output matrix (route to pins)
- Goal: Generate prime-ratio square waves from internal oscillator
- OR: Accept external clock from Mega, use internal dividers for /1, /3, /5, /7, /11, /13

### Step 5: Write config to RAM (Channel 0 first)
- Program via I2C → TCA9548A → Ch 0 → GreenPAK RAM
- RAM is volatile — power cycle resets to factory NVM
- Verify by reading back
- Check output pin with scope

### Step 6: Iterate on all 6 channels
- One channel at a time
- Verify each before moving to next
- Different prime divisor per channel

## Phase 3: Torsion Measurement (Day 2-3)

### Step 7: Compare GreenPAK-generated vs Mega-generated primes
- Same torsion probing methodology as May 20
- FFT analysis, ring survey
- Do the GreenPAK-buffered signals produce cleaner/different results?

## Phase 4: NVM Programming (Day 3+ — OPTIONAL)

### Step 8: Write to NVM (only if RAM testing successful)
- Set write protection bits FIRST
- Write one chip at a time
- Verify after each write
- Keep factory backup for restore
- Remember: 1000 write cycle limit

## What We Need to Research First
1. SLG47004V datasheet — internal oscillator specs, counter blocks, output routing
2. Go Configure (Renesas tool) — can we simulate our config before writing?
3. I2C register map for RAM programming vs NVM programming
4. Which NVM bytes control I2C slave address (to NEVER touch those)
5. Write protection bit locations and how to set them

## Alternative: Hybrid Approach
Keep Mega generating prime frequencies (proven working) but use GreenPAK for:
- Cleaner signal conditioning (replace bodge wire path)
- Phase-locked dividers (tighter frequency accuracy)
- Additional signal processing (PWM, filtering)
- This is lower risk — GreenPAKs don't need to generate frequencies, just process them
