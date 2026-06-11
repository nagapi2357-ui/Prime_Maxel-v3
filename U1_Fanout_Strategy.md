# U1 (TCA9548A) I2C Fanout Strategy

## U1 Position & Orientation
- **Location:** (150, 105), no rotation
- **Package:** TSSOP-24 (0.65mm pad pitch)
- **Pads 1-12:** Left side (top to bottom)
- **Pads 13-24:** Right side (bottom to top)

## U1 Pin Map

```
              R1 (SDA pullup)          R2 (SCL pullup)
              (146, 99)                (154, 99)
                  |                        |
          Net-(U1-SDA)               Net-(U1-SCL)
                  |                        |
         ┌───────┴────────────────────────┴───────┐
         │  1  A0  (NC)           24  VCC (+VCC)  │
         │  2  A1  (NC)           23  SDA (master)│ ← from R1
         │  3  VCC (+VCC)         22  SCL (master)│ ← from R2
         │  4  SDA0 (COL_SDA0)    21  A2  (NC)   │
         │  5  SCL0 (COL_SCL0)    20  SC7 (NC)   │
         │  6  SDA1 (COL_SDA1)    19  SD7 (NC)   │
         │  7  SCL1 (COL_SCL1)    18  SC6 (NC)   │
         │  8  SDA2 (COL_SDA2)    17  SD6 (NC)   │
         │  9  SCL2 (COL_SCL2)    16  SCL5        │
         │ 10  SDA3 (COL_SDA3)    15  SDA5        │
         │ 11  SCL3 (COL_SCL3)    14  SCL4        │
         │ 12  GND  (GND_PWT)     13  SDA4        │
         └────────────────────────────────────────┘
```

## The Problem
Left-side pads 4-11 carry **8 I2C channel signals** (SDA0-3, SCL0-3) at 0.65mm pitch.
Right-side pads 13-16 carry **4 more** (SDA4-5, SCL4-5).

Running all traces straight down from the left side causes shorts — traces are too close at 0.65mm pitch with 0.25mm tracks + 0.2mm clearance (= 0.45mm minimum pitch needed, but pairs interleave SDA/SCL).

## Fanout Strategy

### Left Side (Pads 4-11) — Channels 0-3

**Key insight:** Each spoke only needs its own SDA+SCL pair. Route each pair to a **via** that drops to B.Cu, then run on B.Cu to the spoke.

```
     LEFT SIDE FANOUT (top view)
     
     Pad 4  (SDA0) ──→ short stub LEFT  ──→ Via_SDA0  ↓B.Cu→ south to spoke 1
     Pad 5  (SCL0) ──→ short stub LEFT  ──→ Via_SCL0  ↓B.Cu→ south to spoke 1
     Pad 6  (SDA1) ──→ short stub LEFT  ──→ Via_SDA1  ↓B.Cu→ to spoke 2
     Pad 7  (SCL1) ──→ short stub LEFT  ──→ Via_SCL1  ↓B.Cu→ to spoke 2
     Pad 8  (SDA2) ──→ stub DOWN-LEFT   ──→ Via_SDA2  ↓B.Cu→ to spoke 3
     Pad 9  (SCL2) ──→ stub DOWN-LEFT   ──→ Via_SCL2  ↓B.Cu→ to spoke 3
     Pad 10 (SDA3) ──→ stub DOWN-LEFT   ──→ Via_SDA3  ↓B.Cu→ to spoke 4
     Pad 11 (SCL3) ──→ stub DOWN-LEFT   ──→ Via_SCL3  ↓B.Cu→ to spoke 4
```

**Via placement:** Stagger vias in two columns to the LEFT of U1:
- Column A: x ≈ 145.5mm (SDA vias — ~1mm from pad edge)
- Column B: x ≈ 144.5mm (SCL vias — ~2mm from pad edge)
- Y positions: match or slightly offset from pad Y positions
- This gives 1mm between via columns (plenty for 0.6mm vias + 0.2mm clearance)

**Approximate via positions:**
| Net      | Via X   | Via Y    | Notes |
|----------|---------|----------|-------|
| COL_SDA0 | 145.5   | 103.4    | Pad 4 stub left |
| COL_SCL0 | 144.5   | 104.0    | Pad 5 stub left-down |
| COL_SDA1 | 145.5   | 104.7    | Pad 6 stub left |
| COL_SCL1 | 144.5   | 105.3    | Pad 7 stub left-down |
| COL_SDA2 | 145.5   | 106.0    | Pad 8 stub left |
| COL_SCL2 | 144.5   | 106.6    | Pad 9 stub left-down |
| COL_SDA3 | 145.5   | 107.3    | Pad 10 stub left |
| COL_SCL3 | 144.5   | 107.9    | Pad 11 stub left-down |

### Right Side (Pads 13-16) — Channels 4-5

These are less congested. Fan out to the RIGHT:

```
     Pad 13 (SDA4) ──→ stub RIGHT ──→ Via_SDA4  ↓B.Cu→ to spoke 5
     Pad 14 (SCL4) ──→ stub RIGHT ──→ Via_SCL4  ↓B.Cu→ to spoke 5
     Pad 15 (SDA5) ──→ stub RIGHT ──→ Via_SDA5  ↓B.Cu→ to spoke 6
     Pad 16 (SCL5) ──→ stub RIGHT ──→ Via_SCL5  ↓B.Cu→ to spoke 6
```

**Via positions:**
| Net      | Via X   | Via Y    |
|----------|---------|----------|
| COL_SDA4 | 154.5   | 108.6    |
| COL_SCL4 | 155.5   | 107.9    |
| COL_SDA5 | 154.5   | 107.3    |
| COL_SCL5 | 155.5   | 106.6    |

### Master Bus (Pads 22-23)

Already routed via R1/R2 pullups — looks good in Screenshot 04. No changes needed.

### Power (Pads 3, 24, 12)

- Pad 3 (+VCC_PWT) and Pad 24 (+VCC_PWT): Connect to VCC plane via vias (In2.Cu)
- Pad 12 (GND_PWT): Connect to GND plane via via (In1.Cu)

## Step-by-Step Routing Instructions

### Step 1: Delete existing COL_SCL/SDA traces at U1
Select and delete the straight-line traces currently running down the left side of U1 that are causing shorts.

### Step 2: Route left-side fanout (F.Cu → Via → B.Cu)
1. Set grid to **0.25mm**
2. Start trace at **Pad 4** (COL_SDA0), route LEFT ~1mm, place via
3. Start trace at **Pad 5** (COL_SCL0), route LEFT ~2mm, angle down slightly, place via
4. Repeat for pads 6-11, alternating SDA→column A, SCL→column B
5. Each via drops to B.Cu

### Step 3: Route B.Cu traces from vias to spokes
On B.Cu, route each SDA/SCL pair from their vias outward toward their respective spoke's SLG47004V (U5 equivalent).

### Step 4: Route right-side fanout
Same pattern but mirrored — pads 13-16 fan out RIGHT to vias, then B.Cu to spokes 5-6.

## Grid Settings Reminder
- **0.25mm** for I2C fanout routing
- **0.05mm** if you need fine adjustment near TSSOP pads

---

# Spoke 1 Remaining Components: TP5, TP6, TP7, C5, C6

## Current Positions
| Ref  | Position (x, y)        | Net(s)                        |
|------|------------------------|-------------------------------|
| U4   | (122.42, 132.58)       | LM324 (quad op-amp)           |
| U5   | (113.23, 141.77)       | SLG47004V (GreenPAK)          |
| C7   | (120.03, 139.37)       | GND_PWT / VREF_MID            |
| R5   | (127.73, 125.15)       | Voltage divider               |
| R6   | (129.85, 127.27)       | Voltage divider               |
| TP8  | (113.59, 147.78)       | PULSE_IN                      |
| TP5  | (107.22, 141.41)       | TORSION_A                     |
| TP6  | (109.34, 143.53)       | TORSION_B                     |
| TP7  | (111.47, 145.66)       | VREF_MID                      |
| C5   | (115.63, 134.97)       | +VCC_PWT / GND_PWT (decoupling for U4) |
| C6   | (117.83, 137.17)       | +VCC_PWT / GND_PWT (decoupling for U5) |

## Routing Plan for Remaining Components

All components are at -135° rotation (tangential to the circular array).

### C5 (0.1µF decoupling for U4)
- Pad 1 (+VCC_PWT) → short trace to U4 pin 4 (+VCC_PWT) — same net, ~7mm away
- Pad 2 (GND_PWT) → via to In1.Cu GND plane
- **Or better:** Both caps connect through the power planes — just add vias from each pad to their respective plane layers

### C6 (0.1µF decoupling for U5)
- Pad 1 (+VCC_PWT) → short trace to U5 pin 1 or 13 (+VCC_PWT)
- Pad 2 (GND_PWT) → via to In1.Cu GND plane
- Place as close to U5 VCC/GND pins as possible

### TP5 (TORSION_A test point)
- Pad 1 → connect to TORSION_A net
- Already on the TORSION_A trace path — tap off the existing trace or add a short stub

### TP6 (TORSION_B test point)
- Pad 1 → connect to TORSION_B net
- Same approach as TP5

### TP7 (VREF_MID test point)
- Pad 1 → connect to VREF_MID net (Golden Cell 1)
- Tap off the C7 → U4 pin 10 VREF_MID trace

### Routing Order
1. **C5 first** — decoupling cap, connect VCC pad to U4 VCC, GND pad via to plane
2. **C6 next** — same for U5
3. **TP5** — stub from TORSION_A trace
4. **TP6** — stub from TORSION_B trace  
5. **TP7** — stub from VREF_MID trace

All connections are short stubs (< 5mm). Use 0.25mm grid, Default net class (0.25mm track) for test point stubs. Decoupling cap traces use Power_Bulk (0.4mm) since they're on power nets.
