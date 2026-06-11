# Prime_Maxel-v3 POC — Concept & Schematic Guide
*Nagaπ for Tusk Innovations | 14 Feb 2026*

---

## PART 1: CONCEPTUAL OVERVIEW

### What Is This POC?

The Prime_Maxel-v3 is a **12-node Prime Mirror Resonance Board** — a custom PCB 
that scales the breadboard experiment (8× NE555 oscillator ring) into a programmable, 
impedance-controlled circuit using modern mixed-signal ICs.

**In one sentence:** We're building a circuit where the geometry of the traces and 
the timing of the oscillators both encode prime number relationships, and we measure 
whether this produces a stable, reproducible resonance signature (the Hardware Koide 
constant Q_ℓ ≈ 0.86).

### The Breadboard → PCB Bridge

| Breadboard (Done ✓) | PCB POC (Building Now) |
|---|---|
| 8× NE555 timers | 12× SLG47004V (programmable mixed-signal) |
| Fixed resistors set prime ratios | I2C-programmable oscillator config |
| 47pF + 1MΩ passive coupling | LM324 op-amp active coupling + 0.1µF decoupling |
| Point-to-point wiring | Impedance-controlled Torsion Bridge traces (11/13 ratio) |
| Scope probes on breadboard | Arduino Mega reads via TCA9548A I2C mux |
| 8 nodes (X7→Centre→X5up) | 12 nodes (full Mod-24 Bingo pattern) |
| Q_ℓ ≈ 0.86 measured | Q_ℓ ≈ 0.86 target (with tighter variance) |

### Why 12 Nodes?

- **Mod-24 lattice / 2 = 12**: The 24-cell geometry has 12 node pairs
- **Binary Tetrahedral Group**: Order 24, with 12 distinct orientations
- **Bingo Signature**: 12 evenly-spaced measurement points on the torsion bridge
- **Practical**: Fits TCA9548A (8 I2C channels × 2 addresses = 16 slots)

### What Does Each Golden Cell Do?

Each of the 12 identical cells contains:

```
┌─────────────────────────────────────────────┐
│                GOLDEN CELL (×12)             │
│                                              │
│  SLG47004V (GreenPAK)         LM324 (Op-Amp)│
│  ┌──────────┐                 ┌────────────┐ │
│  │ Internal  │  OA0_OUT ──→── │ Ch1: Buffer │ │
│  │ Oscillator│  OA1_OUT ──→── │ Ch2: Gain   │ │
│  │ + LUTs    │                │ Ch3: Compare│ │
│  │ + I2C     │  ←── GPIO0 ── │ Ch4: Inject │ │
│  │ Config    │                └────────────┘ │
│  └──────────┘                    │           │
│       │                      ┌───┴───┐       │
│   VDD─┤─────────────────────→│ 0.1µF │       │
│   GND─┤─────────────────────→│  Cap  │       │
│       │                      └───────┘       │
│   SCL/SDA → TCA9548A (Main Sheet)            │
└─────────────────────────────────────────────┘
```

**SLG47004V role:** Programmable oscillator (replaces NE555). Its internal 
oscillator frequency is set via I2C to match the prime-ratio timing from the 
breadboard. The GreenPAK also has internal op-amps (OA0, OA1) and LUTs for 
signal processing.

**LM324 role:** Signal conditioning. 
- Ch1: Unity-gain buffer (isolates the SLG47004V output)
- Ch2: Gain stage (amplifies weak resonance signals for measurement)
- Ch3: Comparator (detects threshold crossings for revival timing)
- Ch4: Pulse injection (injects test pulses, like the pushbutton on breadboard)

**Cap role:** Decoupling (keeps power clean per cell, like the breadboard's 
tantalum + ceramic pair).

### The 12-Node Mirror Ring

The 12 cells are arranged as an extended prime mirror around the 1/1 centre:

```
Node:  N1    N2    N3    N4    N5    N6   │  N7    N8    N9    N10   N11   N12
Ratio: 1/13  1/11  1/7   1/5   1/3   1/1  │  2/1   3/1   5/1   7/1   11/1  13/1
       ←── Micro (1/p) ──── Centre ────── Macro (p/1) ──→
```

This extends the breadboard's 8-stage mirror (X7→X5up) to include the 11/13 
prime pair — the **Torsion Bridge** spokes from the Mod-24 lattice.

### The Torsion Bridge Traces

Two impedance-controlled traces run between the 12 cells:
- **TORSION_A** (11-prime path): Length L
- **TORSION_B** (13-prime path): Length L × 13/11 = L × 1.18182...

The 18.18% length difference encodes the 11/13 prime ratio physically in the 
copper. Both traces are 9.0 mil wide (0.229mm) for 50Ω characteristic impedance.

### What We Measure

1. **Revival Efficiency**: After injecting a pulse at the centre node (N6), 
   measure how cleanly the signal returns through the ring. 
   Target: ≥ 95% (breadboard achieved 90-95%)

2. **Hardware Koide Constant (Q_ℓ)**: Compute from the measured delays across 
   all 12 nodes using the torsion-weighted density formula.
   Target: Q_ℓ ≈ 0.86 ± 0.01

3. **Torsion Ratio**: The ratio of signal propagation times on TORSION_A vs 
   TORSION_B should converge to 13/11 = 1.18182...
   Target: measured ratio within 0.1% of 13/11

4. **Phase Coherence**: The 12 Bingo nodes should show a consistent 60°/node 
   phase rotation (360°/6 per half-ring), matching the Mod-24 lattice geometry.

5. **Detuning Robustness**: Deliberately mis-tune one node's oscillator by 15%. 
   Revival should remain ≥ 85% (breadboard achieved this).

### Expected Outcome

If the PCB measurements match or improve on the breadboard:
- **Q_ℓ ≈ 0.86** is confirmed as a hardware fixed point (not a breadboard artifact)
- The 11/13 torsion ratio is physically measurable in trace propagation
- **Prime geometry creates reproducible resonance** — not coincidence
- This validates the path toward Extropic TSU integration (QPf → E(x) mapping)

If Q_ℓ drifts significantly or revival collapses:
- We learn what the breadboard's parasitics were actually contributing
- We adjust coupling (cap values, op-amp gains) and re-test
- This is still valuable — negative results refine the theory

---

## PART 2: SCHEMATIC EDITING GUIDE

### Step 0: Preparation
1. Open KiCad 9 → Open project `Prime_Maxel-v3.kicad_pro`
2. **Save a backup** of `golden_cell.kicad_sch` before editing
3. We'll work in the Golden Cell sub-sheet

### Step 1: Reduce from 70 to 12 Component Sets

In the Golden Cell schematic:

1. Open `golden_cell.kicad_sch` (double-click the hierarchical sheet box on main sheet)
2. You should see 70 groups of (SLG47004V + LM324 + Cap)
3. **Select and delete 58 groups**, keeping only 12
4. Keep the ones with the lowest reference numbers for cleanliness:
   - Keep: U2-U13 (SLG47004V), U5-U16 range (LM324), C2-C13 (Caps)
   - Delete everything else
5. After deleting, run **Annotate Schematic** (Tools → Annotate) to renumber cleanly:
   - SLG47004V: U2 through U13 (nodes N1-N12)
   - LM324: U14 through U25 (one per node)  
   - Caps: C2 through C13 (one per node)

**Tip:** Select a group by drawing a box around one SLG47004V + its LM324 + Cap, 
then Delete. Repeat 58 times. It's tedious but straightforward.

### Step 2: Wire the Signal Connections (Per Cell)

For EACH of the 12 cells, wire these connections:

**SLG47004V → LM324 (signal output path):**
```
SLG47004V OA0_OUT (pin 5)  →  LM324 1IN+ (pin 3)   [Buffer input]
SLG47004V OA1_OUT (pin 22) →  LM324 2IN+ (pin 5)   [Gain input]
```

**LM324 → SLG47004V (feedback/inject path):**
```
LM324 3OUT (pin 8)  →  SLG47004V GPIO0 (pin 12)   [Comparator out → digital in]
LM324 4OUT (pin 14) →  SLG47004V IO0 (pin 21)      [Inject → analog in]
```

**LM324 self-wiring (unused channels tied safely):**
```
LM324 1IN- (pin 2)  →  LM324 1OUT (pin 1)    [Unity gain feedback]
LM324 2IN- (pin 6)  →  wire to gain resistor network (see Step 4)
LM324 3IN+ (pin 10) →  GND_PWT               [Comparator reference]
LM324 3IN- (pin 9)  →  LM324 2OUT (pin 7)    [Comparator input from gain stage]
LM324 4IN+ (pin 12) →  signal from Arduino via connector
LM324 4IN- (pin 13) →  LM324 4OUT (pin 14)   [Unity gain on inject]
```

**How to wire in KiCad:**
- Press `W` to start a wire
- Click on pin endpoint → drag to destination pin → click to finish
- Use **labels** for connections that span distance (Place → Net Label, or press `L`)

### Step 3: Wire I2C to TCA9548A

Each SLG47004V has SCL (pin 10) and SDA (pin 11).

For cells N1-N8 (first 8), use hierarchical labels:
```
U2  SCL → label "COL_SCL0"    U2  SDA → label "COL_SDA0"
U3  SCL → label "COL_SCL0"    U3  SDA → label "COL_SDA0"    (same channel, different I2C addr)
U4  SCL → label "COL_SCL1"    U4  SDA → label "COL_SDA1"
U5  SCL → label "COL_SCL1"    U5  SDA → label "COL_SDA1"
U6  SCL → label "COL_SCL2"    U6  SDA → label "COL_SDA2"
U7  SCL → label "COL_SCL2"    U7  SDA → label "COL_SDA2"
U8  SCL → label "COL_SCL3"    U8  SDA → label "COL_SDA3"
U9  SCL → label "COL_SCL3"    U9  SDA → label "COL_SDA3"
```

For cells N9-N12 (remaining 4):
```
U10 SCL → label "COL_SCL4"    U10 SDA → label "COL_SDA4"
U11 SCL → label "COL_SCL4"    U11 SDA → label "COL_SDA4"
U12 SCL → label "COL_SCL5"    U12 SDA → label "COL_SDA5"
U13 SCL → label "COL_SCL5"    U13 SDA → label "COL_SDA5"
```

This uses 6 of the TCA9548A's 8 channels (2 devices per channel).

**In KiCad:** Use Place → Global Label (Ctrl+L) with these exact names.
They'll automatically connect to the matching labels on the main sheet.

### Step 4: Add Gain Resistors (Optional, Can Add Later)

For each LM324 Ch2 (gain stage), you'll want a feedback resistor network.
For now, you can skip this and add it after the basic wiring is verified.
When ready:
- Add 2× resistors per cell (10kΩ + 10kΩ for unity gain, or 10kΩ + 100kΩ for 10× gain)
- Wire: LM324 pin 6 → junction of R_in (to ground) and R_fb (to pin 7)

### Step 5: Wire the Torsion Bridge Nets

Add two global labels to the Golden Cell:
```
Place Global Label: "TORSION_A"  
Place Global Label: "TORSION_B"
```

Connect TORSION_A to the OA0_OUT chain (daisy-chain through all 12 cells).
Connect TORSION_B to the OA1_OUT chain.

These nets are already assigned to the Torsion_Bridge netclass in Board Setup ✓

### Step 6: Fix Main Sheet Issues

On the main sheet (`Prime_Maxel-v3.kicad_sch`):

1. **Power conflict:** The +VCC_PWT and +5V nets are tied together. 
   If intentional (Arduino 5V powers the cells), that's fine — just add a 
   **PWR_FLAG** symbol on the +VCC_PWT net to suppress the ERC warning.

2. **Dangling labels:** COL_SCL6, COL_SCL7, COL_SDA6, COL_SDA7 are unused 
   (we only need 0-5). Either delete them or add "no connect" flags.

3. **J1 pin 3:** Add a wire to GND or add a no-connect flag.

### Step 7: Run ERC and Verify

1. **Annotate:** Tools → Annotate Schematic (reset all, annotate)
2. **ERC:** Inspect → Electrical Rules Check
3. Target: **< 50 errors** (down from 2,942!)
4. Remaining errors should only be:
   - Floating SLG47004V pins we haven't connected yet (IO1-IO6, RH0/RH1)
   - These can be addressed with no-connect flags for now

### Step 8: Update PCB

1. Tools → Update PCB from Schematic
2. This will remove the 58 deleted components and update nets
3. The 12 remaining cells + main sheet components will be placed
4. Then we run the Master Sync script for positioning

---

## Quick Reference: Pin Connections Per Golden Cell

```
SLG47004V          LM324              Function
─────────          ─────              ────────
Pin 1  VDD_A    ← +VCC_PWT           Power (already wired ✓)
Pin 2  AGND     ← GND_PWT            Power (already wired ✓)
Pin 5  OA0_OUT  → Pin 3  (1IN+)      Buffer input
Pin 22 OA1_OUT  → Pin 5  (2IN+)      Gain input  
Pin 12 GPIO0    ← Pin 8  (3OUT)      Comparator → digital
Pin 21 IO0      ← Pin 14 (4OUT)      Pulse inject
Pin 10 SCL      → COL_SCLx label     I2C clock
Pin 11 SDA      → COL_SDAx label     I2C data
Pin 13 VDD_D    ← +VCC_PWT           Digital power (already wired ✓)
Pin 14 DGND     ← GND_PWT            Digital ground (already wired ✓)

LM324 self-wiring:
Pin 2  (1IN-)   → Pin 1  (1OUT)      Unity gain feedback
Pin 6  (2IN-)   → gain resistor network (or → Pin 7 for unity)
Pin 9  (3IN-)   → Pin 7  (2OUT)      Comparator input  
Pin 10 (3IN+)   → GND_PWT            Reference
Pin 12 (4IN+)   → Arduino signal     Pulse source
Pin 13 (4IN-)   → Pin 14 (4OUT)      Unity gain feedback
Pin 4  VCC      ← +VCC_PWT           (already wired ✓)
Pin 11 GND      ← GND_PWT            (already wired ✓)
```
