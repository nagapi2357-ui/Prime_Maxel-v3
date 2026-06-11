# Proposed Wiring Changes — Prime Maxel v3 Main Sheet

Format matches Adrian's spreadsheet. **BOLD = NEW/CHANGED wiring.**

---

## 12V Input Jack & Cap (NO CHANGES)

| Reference | Pin No: | Wired To: | Reference | Pin No: | Wired To: | Reference | Pin No: |
|-----------|---------|-----------|-----------|---------|-----------|-----------|---------|
| J1 | 1 | ----> | C1 | + | ----> | J3 | 8 |
| J1 | 2 | ----> | C1 | - | ----> | GND_PWT | Global Label |
| **J1** | **3** | **----> GND_PWT Global Label** | | | *(was ? not connected — needs NC flag or GND)* | | |

---

## Arduino Mega v3 Shield

### PWM (NO CHANGES except pull-up destination clarification)

| Reference | Pin No: | Wired To: | Reference | Pin No: | Wired To: | Reference | Pin No: |
|-----------|---------|-----------|-----------|---------|-----------|-----------|---------|
| J2 | 1 | ----> | R1 | 10k | ----> | U1 | 22 – SCL |
| J2 | 2 | ----> | R2 | 10k | ----> | U1 | 23 – SDA |
| J2 | 3 | ----> | X | | | | |
| J2 | 4 | ----> | GND_PWT | Global Label | | | |
| J2 | 5-10 | ----> | X | | | | |

### POWER (NO CHANGES)

*Same as current — J3 pins 1-8 unchanged*

### Analog J4, J5, J6, J7 (NO CHANGES)

*All X (not connected) — unchanged*

### Digital J8

| Reference | Pin No: | Wired To: | Notes |
|-----------|---------|-----------|-------|
| J8 | 1 | ----> GND_PWT Global Label | *unchanged* |
| J8 | 2 | ----> GND_PWT Global Label | *unchanged* |
| J8 | 3-34 | ----> X | *unchanged* |
| J8 | 35 | ----> +5V → U1 pin 24 VCC | *unchanged* |
| J8 | 36 | ----> +5V → U1 pin 24 VCC | *unchanged* |

> **NOTE:** PULSE_IN was planned for J8 pin 22 (Arduino digital 22), but current schematic has it as X. **This is intentionally deferred** — PULSE_IN will be connected later once the signal source is confirmed.

---

## I2C Multiplexer (TCA9548A) — U1

| Reference | Pin No: | Wired To: | Reference | Pin No: | Wired To: |
|-----------|---------|-----------|-----------|---------|-----------|
| U1 | 1 – A0 | ----> X (NC) | | | *addr=0x70, keep floating/GND* |
| U1 | 2 – A1 | ----> X (NC) | | | |
| **U1** | **3 – RESET** | **----> +VCC_PWT Global Label** | | | **⚠️ CHANGE: was X. Active-low reset must be tied high!** |
| U1 | 4 – SD0 | ----> COL_SDA0 Label | | | |
| U1 | 5 – SC0 | ----> COL_SCL0 Label | | | |
| U1 | 6 – SD1 | ----> COL_SDA1 Label | | | |
| U1 | 7 – SC1 | ----> COL_SCL1 Label | | | |
| U1 | 8 – SD2 | ----> COL_SDA2 Label | | | |
| U1 | 9 – SC2 | ----> COL_SCL2 Label | | | |
| U1 | 10 – SD3 | ----> COL_SDA3 Label | | | |
| U1 | 11 – SC3 | ----> COL_SCL3 Label | | | |
| U1 | 12 – GND | ----> GND_PWT Global Label | | | *unchanged* |
| U1 | 13 – SD4 | ----> COL_SDA4 Label | | | |
| U1 | 14 – SC4 | ----> COL_SCL4 Label | | | |
| U1 | 15 – SD5 | ----> COL_SDA5 Label | | | |
| U1 | 16 – SC5 | ----> COL_SCL5 Label | | | |
| **U1** | **17 – SD6** | **----> COL_SDA6 Label (UNUSED)** | | | **Ch6 spare — no cells assigned** |
| **U1** | **18 – SC6** | **----> COL_SCL6 Label (UNUSED)** | | | **Ch6 spare — NC flag ok** |
| **U1** | **19 – SD7** | **----> COL_SDA7 Label (UNUSED)** | | | **Ch7 spare — NC flag ok** |
| **U1** | **20 – SC7** | **----> COL_SCL7 Label (UNUSED)** | | | **Ch7 spare — NC flag ok** |
| U1 | 21 – A2 | ----> X (NC) | | | |
| U1 | 22 – SCL | ----> R1 10k ----> J2 pin 1 | | | *unchanged* |
| U1 | 23 – SDA | ----> R2 10k ----> J2 pin 2 | | | *unchanged* |
| U1 | 24 – VCC | ----> +5V Global Label | | | *unchanged* |

---

## Golden Cell Sub-sheets — **NEW WIRING (The Main Event)**

### I2C Wiring: 2 Cells Per TCA9548A Channel

Each pair of Golden Cells shares one TCA9548A channel. Connect using **net labels** on the main sheet:

| TCA9548A Ch | Label on U1 output | Golden Cell | Hier Pin | Net Label to Use |
|-------------|-------------------|-------------|----------|-----------------|
| **Ch0** | COL_SCL0 | Cell 0 (Golden Cell) | COL_SCL | COL_SCL0 |
| **Ch0** | COL_SDA0 | Cell 0 (Golden Cell) | COL_SDA | COL_SDA0 |
| **Ch0** | COL_SCL0 | Cell 1 (Golden Cell1) | COL_SCL | COL_SCL0 |
| **Ch0** | COL_SDA0 | Cell 1 (Golden Cell1) | COL_SDA | COL_SDA0 |
| **Ch1** | COL_SCL1 | Cell 2 (Golden Cell2) | COL_SCL | COL_SCL1 |
| **Ch1** | COL_SDA1 | Cell 2 (Golden Cell2) | COL_SDA | COL_SDA1 |
| **Ch1** | COL_SCL1 | Cell 3 (Golden Cell3) | COL_SCL | COL_SCL1 |
| **Ch1** | COL_SDA1 | Cell 3 (Golden Cell3) | COL_SDA | COL_SDA1 |
| **Ch2** | COL_SCL2 | Cell 4 (Golden Cell4) | COL_SCL | COL_SCL2 |
| **Ch2** | COL_SDA2 | Cell 4 (Golden Cell4) | COL_SDA | COL_SDA2 |
| **Ch2** | COL_SCL2 | Cell 5 (Golden Cell5) | COL_SCL | COL_SCL2 |
| **Ch2** | COL_SDA2 | Cell 5 (Golden Cell5) | COL_SDA | COL_SDA2 |
| **Ch3** | COL_SCL3 | Cell 6 (Golden Cell6) | COL_SCL | COL_SCL3 |
| **Ch3** | COL_SDA3 | Cell 6 (Golden Cell6) | COL_SDA | COL_SDA3 |
| **Ch3** | COL_SCL3 | Cell 7 (Golden Cell7) | COL_SCL | COL_SCL3 |
| **Ch3** | COL_SDA3 | Cell 7 (Golden Cell7) | COL_SDA | COL_SDA3 |
| **Ch4** | COL_SCL4 | Cell 8 (Golden Cell8) | COL_SCL | COL_SCL4 |
| **Ch4** | COL_SDA4 | Cell 8 (Golden Cell8) | COL_SDA | COL_SDA4 |
| **Ch4** | COL_SCL4 | Cell 9 (Golden Cell9) | COL_SCL | COL_SCL4 |
| **Ch4** | COL_SDA4 | Cell 9 (Golden Cell9) | COL_SDA | COL_SDA4 |
| **Ch5** | COL_SCL5 | Cell 10 (Golden Cell10) | COL_SCL | COL_SCL5 |
| **Ch5** | COL_SDA5 | Cell 10 (Golden Cell10) | COL_SDA | COL_SDA5 |
| **Ch5** | COL_SCL5 | Cell 11 (Golden Cell11) | COL_SCL | COL_SCL5 |
| **Ch5** | COL_SDA5 | Cell 11 (Golden Cell11) | COL_SDA | COL_SDA5 |

**How to wire in KiCad:** Place a net label "COL_SCL0" on the COL_SCL hierarchical pin of Golden Cell 0 and Golden Cell 1. This connects them to U1 pin 5 (SC0) which already has a "COL_SCL0" label.

### TORSION_A / TORSION_B — Global Labels (Shared Bus)

| Golden Cell | Hier Pin | Connect To |
|-------------|----------|------------|
| ALL 12 cells | TORSION_A | **Global Label "TORSION_A"** |
| ALL 12 cells | TORSION_B | **Global Label "TORSION_B"** |

**How:** Place a global label "TORSION_A" on each cell's TORSION_A hierarchical pin. Same for TORSION_B. All 12 cells share the same bus.

### PULSE_IN — Global Label (Common Signal)

| Golden Cell | Hier Pin | Connect To |
|-------------|----------|------------|
| ALL 12 cells | PULSE_IN | **Global Label "PULSE_IN"** |

**How:** Place a global label "PULSE_IN" on each cell's PULSE_IN hierarchical pin. Later, connect PULSE_IN to an Arduino digital pin (e.g., J8 pin 22 = Arduino D22).

### VREF_MID — Self-Contained (NO Main Sheet Wiring Needed)

| Golden Cell | Hier Pin | Connect To |
|-------------|----------|------------|
| ALL 12 cells | VREF_MID | **Nothing on main sheet** — each cell generates its own VREF_MID internally via R5/R6/C4 voltage divider |

**How:** The VREF_MID hierarchical pin can be **removed** from the sub-sheet boundary, OR left unconnected on the main sheet with NC flags. Since it's per-cell internal, it doesn't need to cross the sheet boundary.

> ⚠️ Actually, looking at the golden cell schematic — VREF_MID is a hierarchical label that feeds into U3 pin 10 (3IN+). The voltage divider R5/R6/C4 generates it inside the sub-sheet. So the main sheet pin is an **input** that's already driven internally. **Leave it unconnected on the main sheet** and add NC flags, OR remove it from the sub-sheet boundary.

---

## Summary of Changes

| # | Change | Where | Priority |
|---|--------|-------|----------|
| 1 | **Tie U1 RESET (pin 3) to +VCC_PWT** | Main sheet, U1 | 🔴 Critical |
| 2 | **Wire COL_SCL/SDA labels to 12 Golden Cells** (2 per channel) | Main sheet, cell hier pins | 🔴 Critical |
| 3 | **Add TORSION_A global label** to all 12 cells | Main sheet, cell hier pins | 🔴 Critical |
| 4 | **Add TORSION_B global label** to all 12 cells | Main sheet, cell hier pins | 🔴 Critical |
| 5 | **Add PULSE_IN global label** to all 12 cells | Main sheet, cell hier pins | 🟡 Important |
| 6 | **NC flags on VREF_MID** for all 12 cells (or remove pin) | Main sheet or sub-sheet | 🟢 Cleanup |
| 7 | **NC flags on U1 Ch6/Ch7** (pins 17-20) | Main sheet, U1 | 🟢 Cleanup |
| 8 | **J1 pin 3** — add NC flag or wire to GND | Main sheet, J1 | 🟢 Cleanup |
| 9 | **Add C5 0.1µF on U3 VCC** (pin 4) inside golden cell | Sub-sheet | 🟡 Important |

---

## Board Setup Fix (While You're At It)

| Setting | Current | Should Be | Why |
|---------|---------|-----------|-----|
| Torsion_Bridge track width | 0.203 mm | **0.229 mm** (9.0 mil) | 50Ω impedance target |

