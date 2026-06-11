# Prime_Maxel-v3 — Routing Reference Card
## Print this out for routing!

---

## Board Geometry
- **Center:** (150.0, 105.0)
- **LM324 ring:** R = 39mm (inner), 12 ICs at 30° intervals
- **SLG47004V ring:** R = 52mm (outer), 12 ICs at 30° intervals
- **Orientation:** Components rotated to face radially outward

## Net Classes
| Class | Track Width | Via Drill | Purpose |
|-------|------------|-----------|---------|
| Default | 0.25mm | 0.3mm | General signals |
| Power_Bulk | 0.40mm | — | VCC/GND power |
| Torsion_Bridge | 0.229mm | 0.3mm | **50Ω controlled impedance** |

## Layer Stack
| Layer | Purpose |
|-------|---------|
| F.Cu | Component side, signal routing |
| In1.Cu | GND_PWT ground plane |
| In2.Cu | +VCC_PWT power plane (circular area only) |
| B.Cu | Signal routing (TORSION traces ideal here) |

---

## TORSION NETS (Global — same net connects ALL 12 cells)

### ⚡ TORSION_A
Connects to **every LM324** Pin 1 (1OUT) + Pin 2 (1IN-)
Plus test points: TP1, TP5, TP9, TP13, TP17, TP21, TP25, TP29, TP33, TP37, TP41, TP45

### ⚡ TORSION_B
Connects to **every LM324** Pin 7 (2OUT) + Pin 6 (2IN-) + Pin 9 (3IN-)
Plus test points: TP2, TP6, TP10, TP14, TP18, TP22, TP26, TP30, TP34, TP38, TP42, TP46

---

## PER-CELL WIRING PATTERN (identical for all 12 cells)

Each cell = 1× LM324DRE4 (inner) + 1× SLG47004V (outer) + 1× 0.1µF cap + resistor + test points

### LM324 Pin Map (same pattern every cell)
| Pin | Name | Net | Connect To |
|-----|------|-----|------------|
| 1 | 1OUT | **TORSION_A** | Global ring bus |
| 2 | 1IN- | **TORSION_A** | Global ring bus |
| 3 | 1IN+ | Local | → SLG Pin 5 (OA0_OUT) |
| 4 | VCC | +VCC_PWT | Power plane via |
| 5 | 2IN+ | Local | → SLG Pin 22 (OA1_OUT) |
| 6 | 2IN- | **TORSION_B** | Global ring bus |
| 7 | 2OUT | **TORSION_B** | Global ring bus |
| 8 | 3OUT | Local | → SLG Pin 12 (GPIO0) |
| 9 | 3IN- | **TORSION_B** | Global ring bus |
| 10 | 3IN+ | VREF_MID | Global reference bus |
| 11 | GND | GND_PWT | Ground plane via |
| 12 | 4IN+ | PULSE_IN | Global pulse bus |
| 13 | 4IN- | Local | → LM324 Pin 14 (feedback) |
| 14 | 4OUT | Local | → LM324 Pin 13 + SLG Pin 21 (I0) |

### SLG47004V Pin Map (same pattern every cell)
| Pin | Name | Net | Connect To |
|-----|------|-----|------------|
| 1 | VDD_A | +VCC_PWT | Power plane via |
| 2 | AGND | GND_PWT | Ground plane via |
| 3 | OA0- | Local | Internal (floating/unused?) |
| 4 | OA0+ | Local | Internal (floating/unused?) |
| 5 | OA0_OUT | Local | → LM324 Pin 3 (1IN+) |
| 6 | RH0_A | Local | Internal |
| 7 | RH0_B | Local | Internal |
| 8 | RH1_A | Local | Internal |
| 9 | RH1_B | Local | Internal |
| 10 | SCL | COL_SCLn | I2C clock (to TCA9548A mux) |
| 11 | SDA | COL_SDAn | I2C data (to TCA9548A mux) |
| 12 | GPIO0 | Local | → LM324 Pin 8 (3OUT) |
| 13 | VDD_D | +VCC_PWT | Power plane via |
| 14 | DGND | GND_PWT | Ground plane via |
| 15-20 | IO1-IO6 | Local | Internal (floating/unused?) |
| 21 | I0 | Local | → LM324 Pin 13/14 (4IN-/4OUT) |
| 22 | OA1_OUT | Local | → LM324 Pin 5 (2IN+) |
| 23 | OA1+ | Local | Internal |
| 24 | OA1- | Local | Internal |

---

## CELL POSITIONS & I2C BUS ASSIGNMENT

| Cell | LM324 | SLG | Angle | I2C Bus | SCL Net | SDA Net |
|------|-------|-----|-------|---------|---------|---------|
| 1 | U2 | U3 | +105° | Bus 0 | COL_SCL0 | COL_SDA0 |
| 2 | U4 | U5 | +135° | Bus 0 | COL_SCL0 | COL_SDA0 |
| 3 | U6 | U7 | +165° | Bus 1 | COL_SCL1 | COL_SDA1 |
| 4 | U8 | U9 | -165° | Bus 1 | COL_SCL1 | COL_SDA1 |
| 5 | U10 | U11 | -135° | Bus 2 | COL_SCL2 | COL_SDA2 |
| 6 | U12 | U13 | -105° | Bus 2 | COL_SCL2 | COL_SDA2 |
| 7 | U14 | U15 | -75° | Bus 3 | COL_SCL3 | COL_SDA3 |
| 8 | U16 | U17 | -45° | Bus 3 | COL_SCL3 | COL_SDA3 |
| 9 | U18 | U19 | -15° | Bus 4 | COL_SCL4 | COL_SDA4 |
| 10 | U20 | U21 | +15° | Bus 4 | COL_SCL4 | COL_SDA4 |
| 11 | U22 | U23 | +45° | Bus 5 | COL_SCL5 | COL_SDA5 |
| 12 | U24 | U25 | +75° | Bus 5 | COL_SCL5 | COL_SDA5 |

**I2C pairing:** Adjacent cells share an I2C bus (6 buses → TCA9548A 6 channels used)

---

## ROUTING PRIORITY (per cell)

### Priority 1 — TORSION (0.229mm, 50Ω)
These are the critical measurement nets. Route on **B.Cu** to keep away from power planes.
- TORSION_A: Ring bus connecting all LM324 Pin 1 + Pin 2
- TORSION_B: Ring bus connecting all LM324 Pin 7 + Pin 6 + Pin 9

### Priority 2 — Local LM324↔SLG47004V signals (0.25mm)
5 local connections per cell:
1. SLG Pin 5 (OA0_OUT) → LM324 Pin 3 (1IN+)
2. SLG Pin 22 (OA1_OUT) → LM324 Pin 5 (2IN+)
3. SLG Pin 12 (GPIO0) → LM324 Pin 8 (3OUT)
4. SLG Pin 21 (I0) → LM324 Pin 13 (4IN-) / Pin 14 (4OUT)
5. LM324 Pin 13 → Pin 14 (self-feedback, short trace)

### Priority 3 — I2C bus (0.25mm)
SLG Pin 10 (SCL) + Pin 11 (SDA) → routed to TCA9548A (U1)
Paired cells share bus — route together

### Priority 4 — Global buses
- VREF_MID → every LM324 Pin 10
- PULSE_IN → every LM324 Pin 12

### Priority 5 — Power (via to planes)
- +VCC_PWT: LM324 Pin 4, SLG Pin 1 + Pin 13 → via to In2.Cu
- GND_PWT: LM324 Pin 11, SLG Pin 2 + Pin 14 → via to In1.Cu

---

## ROUTING STRATEGY
1. Start with **Cell 1 (U2/U3, +105°)** — route completely
2. TORSION_A/B run as **ring buses** around the inner ring (R≈39mm) connecting all LM324s
3. Local signals route **radially** between LM324↔SLG47004V along each 30° spoke
4. Vias placed on radial spokes, not Cartesian grid
5. After one cell works, replicate pattern rotating 30° for each subsequent cell
