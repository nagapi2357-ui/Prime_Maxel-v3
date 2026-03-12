# Prime_Maxel-v3 — PCB Design Brief
### For Professional PCB Layout Completion
**Project Owner:** Adrian (Tusk Innovations)
**Date:** 5 March 2026
**KiCad Version:** 9.x
**Target Manufacturer:** JLCPCB (4-layer, standard spec)

---

## 1. Project Objective

Prime_Maxel-v3 is a **research instrument** for investigating Prime Wave Torsion (PWT) — an experimental theory exploring relationships between prime number distribution and electromagnetic field behaviour.

The PCB is designed as an **Arduino Mega shield** that hosts **12 identical analog measurement cells** ("Golden Cells") arranged in a **circular/radial pattern** around the board. Each cell contains a programmable mixed-signal IC and a quad op-amp configured as a torsion bridge — a balanced differential measurement circuit.

**The board's purpose is to:**
- Generate controlled analog signals via programmable GreenPAK ICs
- Measure differential "torsion" signals between paired bridge arms (TORSION_A / TORSION_B)
- Route these signals through concentric ring traces on the back copper layer (B.Cu)
- Aggregate data via I2C bus through a multiplexer back to the Arduino Mega
- Enable iterative experimentation with different signal configurations

**This is a proof-of-concept research board**, not a commercial product. Signal integrity of the torsion bridge traces is the highest priority.

---

## 2. Component Selection & Rationale

### Main Sheet Components

| Ref | Component | Purpose |
|-----|-----------|---------|
| **J1** | EJ503A barrel jack | 12V DC power input |
| **C1** | 100µF electrolytic | Bulk input decoupling |
| **U1** | TCA9548APWR | 8-channel I2C multiplexer — routes I2C bus to individual Golden Cells, preventing address conflicts (all SLG47004V share the same I2C address) |
| **R1, R2** | 10kΩ | I2C pull-up resistors (SDA, SCL) |
| **J2–J8** | Pin headers | Arduino Mega shield connectors (2×18 main + 1×8/1×10 auxiliary). Standard Arduino Mega R3 shield footprint |
| **MH1–MH6** | Mounting holes | Board mechanical mounting |

### Per Golden Cell (×12 instances)

| Ref | Component | Purpose |
|-----|-----------|---------|
| **U_odd** (U3, U5, U7…) | **SLG47004V** (Silego/Renesas GreenPAK) | Programmable mixed-signal IC. Contains configurable op-amps, comparators, LUTs, counters, and analog routing. Programmed via I2C. Generates the excitation signals and provides configurable analog front-end |
| **U_even** (U2, U4, U6…) | **LM324DRE4** (TI quad op-amp) | Four op-amp channels configured as differential torsion bridge measurement circuit. Specific pins connect to TORSION_A and TORSION_B nets |
| **C** (C2–C37) | 0.1µF 0603 ceramic | Local decoupling capacitor for each IC pair |
| **R** (R3–R26) | 10kΩ 0402/0603 | Bias/feedback resistors for op-amp configuration |
| **TP** (TP1–TP48) | Test points | Probe points for each cell's signals during experimentation |

### Why These Components

- **SLG47004V:** Chosen for its unique combination of programmable analog + digital in a single IC. Allows reconfiguring the measurement circuit without board redesign — critical for iterative research. I2C programmable.
- **LM324DRE4:** Industry-standard quad op-amp, rail-to-rail, low cost, well-characterised. Four channels per package allows a complete bridge in one IC. SOIC-14 package for hand-soldering feasibility.
- **TCA9548A:** Necessary because all 12 SLG47004V ICs share the same fixed I2C address. The mux allows individual addressing of each cell.

---

## 3. Circuit Principles

### Torsion Bridge Concept

Each Golden Cell implements a **differential measurement bridge** using the LM324's four op-amp channels:

```
TORSION_A net:  Pin 1 (1OUT) ←→ Pin 2 (1IN-)
TORSION_B net:  Pin 6 (2IN-) ←→ Pin 7 (2OUT) ←→ Pin 9 (3IN-)
```

- **TORSION_A** and **TORSION_B** are the two arms of the bridge
- The SLG47004V drives excitation signals into the bridge via its configurable analog outputs (RH0_A → TORSION_B net, RH0_B → TORSION_A net)
- The differential voltage between TORSION_A and TORSION_B represents the "torsion" measurement
- Each cell's TORSION signals route to **concentric ring traces** on B.Cu, creating a physical geometry that is part of the experiment

### Signal Flow

```
Arduino Mega (I2C) → TCA9548A Mux → SLG47004V (program/configure)
                                          ↓
                                    Excitation signals
                                          ↓
                                    LM324 Bridge Circuit
                                    (TORSION_A ↔ TORSION_B)
                                          ↓
                                    Concentric ring traces (B.Cu)
                                          ↓
                                    Test points for measurement
```

### Power Distribution

- **+VCC_PWT** (12V regulated): Fed from J1 barrel jack, distributed to all cells
- **GND_PWT**: Common ground for all analog circuitry
- Power and ground have dedicated internal planes (see Layer Stackup below)

### I2C Bus

- Single I2C bus from Arduino → TCA9548A → 12× SLG47004V
- 10kΩ pull-ups on SDA/SCL
- Bus routed as standard signal traces (Default net class)

---

## 4. Physical Board Layout & Characteristics

### Board Shape & Dimensions

The board has a **composite shape**: a rectangular Arduino Mega shield section on one side, transitioning into a **large circular area** where the 12 Golden Cells are arranged radially. The circular section is the experimental area.

### Layer Stackup (4-Layer)

| Layer | Assignment | Purpose |
|-------|-----------|---------|
| **F.Cu** (Top) | Signal routing, component pads | SMD components mounted here. I2C bus, signal routing |
| **In1.Cu** | **GND_PWT ground plane** | Continuous ground pour covering full board area. Reference plane for signal integrity |
| **In2.Cu** | **+VCC_PWT power plane** | Power pour covering circular Golden Cell area only (does NOT extend into Arduino shield section, which gets power from the Arduino) |
| **B.Cu** (Bottom) | **TORSION ring traces** | Critical signal layer — concentric ring traces for TORSION_A and TORSION_B. This layer's geometry is part of the experiment |

**Stackup specs (targeting JLCPCB JLC04161H-7628):**
- Total thickness: 1.6mm
- Copper weight: 2oz (0.07mm) all layers
- Core: FR4, εr = 4.5
- Prepreg: 0.127mm

### Component Placement

- **Arduino shield connectors** (J2–J8): Fixed positions matching Arduino Mega R3 header layout
- **TCA9548A** (U1): Near Arduino headers for short I2C runs
- **Barrel jack** (J1) + bulk cap (C1): Board edge, near power input
- **12 Golden Cells**: Arranged **radially** around the circular board area at equal angular spacing (30° apart). Each cell cluster contains:
  - 1× LM324DRE4 (SOIC-14)
  - 1× SLG47004V (QFN-like)
  - 1× 0.1µF 0603 capacitor
  - 1× 10kΩ resistor
  - 4× test points
- **Mounting holes**: At standard Arduino shield positions + additional for circular section

### Net Classes (Pre-configured)

| Net Class | Track Width | Clearance | Via Drill | Nets |
|-----------|------------|-----------|-----------|------|
| **Default** | 0.25mm | 0.2mm | 0.3mm | All general signals, I2C |
| **Power_Bulk** | 0.4mm | 0.2mm | 0.3mm | +VCC_PWT, GND_PWT |
| **Torsion_Bridge** | 0.229mm | 0.2mm | 0.3mm | TORSION_A, TORSION_B, VREF_MID*, PULSE_IN* |

The 0.229mm Torsion_Bridge width was calculated for ~50Ω characteristic impedance on the 4-layer stackup (9.0mil trace, 7.6mil effective after etch compensation).

### B.Cu Torsion Ring Geometry

**This is the most critical and unique aspect of the layout:**

- B.Cu contains **concentric ring traces** (arcs/circles) centred on the circular board area
- **TORSION_A** connects to one ring (outer), **TORSION_B** to another (inner)
- Each Golden Cell's LM324 torsion pins connect via vias down to B.Cu and then to the appropriate ring
- The ring geometry, spacing, and concentricity are intentional and should be preserved
- Traces from component pads to the rings should be as short and symmetric as possible

### DRC Rules

A JLCPCB-matched custom DRC rules file (`Prime_Maxel-v3.kicad_dru`) is included. Key constraints:
- Min trace: 0.09mm (our min is 0.229mm)
- Min clearance: 0.09mm
- Min via drill: 0.2mm (ours: 0.3mm)
- Copper-to-edge: 0.3mm
- All our design values are comfortably above JLCPCB minimums

---

## 5. Current Status & What Needs Completing

### Already Done ✅
- Complete schematic (main sheet + 12 Golden Cell sub-sheets)
- All components placed on PCB
- Board outline defined
- GND plane (In1.Cu) — full board coverage
- VCC plane (In2.Cu) — circular area coverage
- Concentric torsion ring traces on B.Cu (partially routed)
- Net classes and DRC rules configured
- Courtyard overlaps resolved

### Needs Completion 🔧
1. **TORSION signal routing (B.Cu):** Connect all 12 cells' TORSION_A and TORSION_B pins to their respective concentric rings via short via drops. Some cells partially connected, others not yet.
2. **I2C bus routing (F.Cu):** Route SDA/SCL from TCA9548A to each SLG47004V through the mux channels.
3. **Power trace routing:** Connect +VCC_PWT and GND_PWT to all component power pins (via planes where possible, with vias to internal layers).
4. **Remaining signal connections:** SLG47004V ↔ LM324 inter-chip signals within each cell (these are local, short runs).
5. **Via stitching:** Ground via stitching around torsion traces for return path integrity.
6. **DRC clean-up:** Resolve remaining unconnected nets and any violations.
7. **Silkscreen:** Component labels and board markings.

### Routing Priority Order (Recommended)
1. ① GND vias to In1.Cu plane
2. ② Power vias to In2.Cu plane + power traces
3. ③ **TORSION traces** (critical — matched impedance, symmetric)
4. ④ I2C bus (SDA/SCL to each cell)
5. ⑤ Remaining inter-chip signals
6. ⑥ Optimization and DRC cleanup

---

## 6. Files Included

| File | Description |
|------|-------------|
| `Prime_Maxel-v3.kicad_pro` | Project file (net classes, DRC settings) |
| `Prime_Maxel-v3.kicad_sch` | Main schematic (Arduino shield + mux) |
| `golden_cell.kicad_sch` | Golden Cell sub-sheet schematic |
| `Prime_Maxel-v3.kicad_pcb` | PCB layout (partially routed) |
| `Prime_Maxel-v3.kicad_dru` | Custom DRC rules (JLCPCB specs) |
| `Adrian/` | Custom footprint library |

---

## 7. Key Design Constraints & Notes

1. **The concentric ring geometry on B.Cu is intentional** — do not simplify or straighten these traces. They are part of the experimental design.
2. **Torsion traces should be impedance-matched** at ~50Ω (0.229mm width on this stackup).
3. **Symmetry matters** — try to keep TORSION_A and TORSION_B trace lengths similar within each cell.
4. **The Arduino shield header positions are fixed** — standard Mega R3 pinout.
5. **All components are on F.Cu (top)**, B.Cu is reserved for torsion rings and minimal routing.
6. **Target manufacturer: JLCPCB** — 4-layer, 1.6mm, 2oz copper, FR4, HASL finish.
7. **This is a research prototype** — first revision. Test points are provided for probing.

---

## 8. Test Points — Oscilloscope Probing

Each Golden Cell includes **4 test points** (48 total across 12 cells) specifically designed for oscilloscope probing during experimentation. These are critical for the board's research function.

### Test Point Assignments Per Cell

| Test Point | Connected To | Purpose |
|-----------|-------------|---------|
| **TP_A** | TORSION_A net | Probe torsion bridge arm A — allows differential measurement with TP_B |
| **TP_B** | TORSION_B net | Probe torsion bridge arm B — the complementary arm |
| **TP_VREF** | VREF_MID net | Reference voltage midpoint — baseline for differential measurements |
| **TP_PULSE** | PULSE_IN net | Excitation/pulse signal from SLG47004V — verify stimulus waveform |

### Layout Considerations for Test Points

- **Accessibility:** Test points should be placed on **F.Cu (top layer)** with adequate clearance for oscilloscope probe tips (~2.54mm / 100mil pad recommended)
- **Proximity:** Each TP should be as close as possible to its corresponding Golden Cell to minimize trace length and parasitic effects
- **Ground reference:** Each cell cluster should have a nearby **GND test point or via** for the oscilloscope probe ground clip. Consider adding a GND TP near each cell or ensuring exposed GND vias are accessible
- **Grouping:** The 4 TPs per cell should be grouped together in a consistent orientation across all 12 cells, making it intuitive to probe any cell
- **Labelling:** Silkscreen labels (TP_A, TP_B, VREF, PULSE + cell number) are important — the researcher needs to quickly identify which cell and signal they're probing
- **Pad style:** Through-hole test point pads (loop or keyhole style) are preferred over SMD pads, as they allow clip-on probe tips for hands-free measurement during extended testing sessions

### Probing Use Cases

1. **Differential torsion measurement:** Probe TP_A and TP_B simultaneously on dual-channel scope to observe the differential signal between bridge arms
2. **Stimulus verification:** Probe TP_PULSE to confirm the GreenPAK is generating the expected excitation waveform
3. **Reference baseline:** Probe TP_VREF to establish the DC operating point and check for drift
4. **Cross-cell comparison:** Probe the same signal (e.g., TP_A) across multiple cells to compare responses at different radial positions

---

*For questions, contact Adrian at Tusk Innovations.*
