# V3 Bring-Up Plan ☀️

**Board:** Prime_Maxel-v3 — 12-node Prime Mirror Resonance Board
**Status:** PCBs arrived (5× JLCPCB ENIG, SMT assembled), awaiting test gear
**Date:** 2026-04-26

---

## ⚠️ CRITICAL SAFETY

> **DO NOT PLUG 12V INTO J1.** There is no voltage regulator on this board.
> VCC_PWT goes direct from J1 to all ICs. SLG47004V and TCA9548A max = 5.5V.
> 12V = instant death for every GreenPAK and the I2C mux.

**Safe power options:**
- **Option A (recommended):** 9V adapter → Arduino Mega barrel jack → Arduino's onboard regulator → 5V via J3 shield header → VCC_PWT
- **Option B:** 5V center-positive adapter (2.1mm × 5.5mm) direct into J1

---

## 📦 Pre-Requisites (Waiting On)

| Item | Status | Notes |
|------|--------|-------|
| UNI-T UTP3315TFL PSU | Ordered | Bench supply — use for Option B / precise voltage |
| 6× BNC-to-SMA RG316 cables | Ordered | For scope connections |
| Arduino Mega stackable headers | TBD | Solves connection + clearance |
| Arduino Mega 2560 | Need to confirm available | |

---

## 🔧 Phase 0 — Visual Inspection (No Power)

**Time: ~15 min per board**

- [ ] Inspect all 5 boards under magnification (phone macro / loupe)
- [ ] Check SMT assembly quality — all SLG47004V, LM324, TCA9548A, caps soldered?
- [ ] Look for solder bridges, especially on fine-pitch ICs (SLG47004V QFN-24)
- [ ] Verify barrel jack J1 (EJ503A) is present and correctly oriented
- [ ] Check for any missing components vs BOM
- [ ] Photograph each board (top and bottom) for records

**Select one board as Board #1 (the test subject). Keep the other 4 pristine until procedures are proven.**

---

## ⚡ Phase 1 — Power Integrity (No Arduino)

**Time: ~30 min**

**Goal:** Confirm VCC_PWT and GND_PWT planes are healthy before connecting any logic.

### 1.1 — Cold resistance check
- [ ] Multimeter continuity: J1 center pin → any VCC_PWT test point (should be < 1Ω)
- [ ] Multimeter continuity: J1 sleeve → any GND_PWT test point (should be < 1Ω)
- [ ] **VCC_PWT to GND_PWT resistance** — should be > 1kΩ (no shorts). If < 100Ω, STOP — there's a short.

### 1.2 — Smoke test (bench PSU)
- [ ] Set UNI-T PSU to **5.00V, current limit 100mA**
- [ ] Connect to J1 (center = positive, sleeve = GND)
- [ ] Power on — watch current draw
  - Expected: **10-30mA** idle (12× SLG47004V quiescent + TCA9548A + LM324s)
  - If > 100mA: **power off immediately** — investigate short
- [ ] Measure VCC_PWT at multiple test points around the ring — should all read 5.0V ± 0.1V
- [ ] Touch-test ICs for heat (should be room temp at idle)
- [ ] Leave powered for 2 minutes, re-check current — should be stable

### 1.3 — Power plane quality
- [ ] Measure voltage at each SLG47004V VDD pad (pins 1/13) — all should be 5.0V
- [ ] Measure voltage at each LM324 VCC pad (pin 4) — all should be 5.0V
- [ ] Measure GND continuity at opposite sides of the board — should be < 0.5Ω

**PASS criteria:** Stable 5V everywhere, current < 50mA, no heat.

---

## 🔍 Phase 2 — I2C Bus Verification

**Time: ~45 min**

**Goal:** Confirm Arduino can see all 12 GreenPAKs via the TCA9548A mux.

### 2.1 — Arduino setup
- [ ] Install stackable headers on Arduino Mega (solder if needed)
- [ ] Mount Arduino onto v3 board via stackable headers
- [ ] Power Arduino via USB (this also powers the v3 board via 5V shield pin)
- [ ] Verify VCC_PWT = 5.0V (from Arduino's regulator)

### 2.2 — I2C scan
- [ ] Upload basic I2C scanner sketch to Arduino Mega
- [ ] Should detect TCA9548A at address **0x70** (default, all A0-A2 = GND)
- [ ] If not found: check SDA/SCL wiring from shield header to U1

### 2.3 — Scan through mux channels
```cpp
// For each channel 0-5:
Wire.beginTransmission(0x70);  // TCA9548A
Wire.write(1 << channel);      // Select channel
Wire.endTransmission();
// Then scan for SLG47004V devices
// Default SLG47004V I2C address: 0x08 (or 0x00 — check datasheet)
// Two devices per channel — they need different addresses
```

- [ ] Channel 0: Detect Cell 1 + Cell 2 GreenPAKs
- [ ] Channel 1: Detect Cell 3 + Cell 4
- [ ] Channel 2: Detect Cell 5 + Cell 6
- [ ] Channel 3: Detect Cell 7 + Cell 8
- [ ] Channel 4: Detect Cell 9 + Cell 10
- [ ] Channel 5: Detect Cell 11 + Cell 12

**Expected: 12 devices found across 6 channels (2 per channel).**

**If a channel shows 0 or 1 device:**
- Check SLG47004V address configuration (pin strapping or NVM)
- Check solder joints on that cell's SCL/SDA
- Check TCA9548A channel with a scope — are SCL/SDA toggling?

**PASS criteria:** All 12 GreenPAKs addressable via I2C.

---

## 🎵 Phase 3 — GreenPAK Oscillator Configuration

**Time: ~1 hour**

**Goal:** Program each SLG47004V to oscillate at its assigned prime-ratio frequency.

### 3.1 — GreenPAK programming
- [ ] Download/install Renesas Go Configure IDE (if not already)
- [ ] Create base oscillator design for SLG47004V
  - Internal RC oscillator → divider chain → output on OA0_OUT (pin 5)
  - Configure I2C slave address (different for each pair on shared bus)

### 3.2 — Prime ratio assignment

| Cell | Node | Ratio | Relative Freq | Notes |
|------|------|-------|---------------|-------|
| 1 | N1 | 1/13 | f₀/13 | Micro end |
| 2 | N2 | 1/11 | f₀/11 | |
| 3 | N3 | 1/7 | f₀/7 | |
| 4 | N4 | 1/5 | f₀/5 | |
| 5 | N5 | 1/3 | f₀/3 | |
| 6 | N6 | 1/1 | f₀ | Centre |
| 7 | N7 | 2/1 | 2·f₀ | |
| 8 | N8 | 3/1 | 3·f₀ | |
| 9 | N9 | 5/1 | 5·f₀ | |
| 10 | N10 | 7/1 | 7·f₀ | Macro end |
| 11 | N11 | 11/1 | 11·f₀ | |
| 12 | N12 | 13/1 | 13·f₀ | |

**Base frequency (f₀):** TBD — depends on GreenPAK internal osc range. Suggest starting with f₀ = 1kHz (human-friendly, easy to scope).

- [ ] Program Cell 6 (centre, f₀) first — verify OA0_OUT shows clean square/sine wave
- [ ] Program remaining cells with their prime-ratio frequencies
- [ ] Verify each cell's OA0_OUT on scope — correct frequency?

**PASS criteria:** All 12 cells oscillating at assigned frequencies.

---

## 📏 Phase 4 — Torsion Path Measurement

**Time: ~1 hour**

**Goal:** Measure signal propagation on TORSION_A and TORSION_B.

### 4.1 — Continuity
- [ ] Confirm TORSION_A is continuous ring (probe TP1→TP5→TP9→...→TP45 — all same net)
- [ ] Confirm TORSION_B is continuous ring (probe TP2→TP6→TP10→...→TP46 — all same net)
- [ ] Measure DC resistance of each path end-to-end

### 4.2 — Signal injection test
- [ ] Inject a 1kHz square wave at one end of TORSION_A
- [ ] Probe at multiple test points along the ring — signal should be present with minimal attenuation
- [ ] Repeat for TORSION_B
- [ ] Compare propagation times (this is where dual-channel scope becomes important)

### 4.3 — Torsion ratio measurement
- [ ] With all cells oscillating, measure signal amplitude at TORSION_A vs TORSION_B test points
- [ ] Measure propagation delay ratio
- [ ] **Target:** TORSION_B / TORSION_A timing ratio ≈ 13/11 (1.18182...)
- [ ] Record actual measured ratio

**PASS criteria:** Both torsion paths carry signal; ratio is measurable.

---

## 🎯 Phase 5 — Resonance Measurement (The Main Event)

**Time: ~2+ hours**

**Goal:** Measure the Hardware Koide constant Q_ℓ.

### 5.1 — Pulse injection
- [ ] Wire PULSE_IN to Arduino digital pin (D22 planned)
- [ ] Send a single pulse to centre node (N6)
- [ ] Monitor revival pattern across all 12 nodes via LM324 outputs

### 5.2 — Q_ℓ measurement
- [ ] Collect delay/amplitude data from all 12 nodes
- [ ] Compute Q_ℓ using the torsion-weighted density formula
- [ ] **Target: Q_ℓ ≈ 0.86 ± 0.01** (matching breadboard)

### 5.3 — Phase coherence
- [ ] Measure phase relationships between adjacent nodes
- [ ] **Target:** Consistent ~60°/node rotation (360°/6 per half-ring)

### 5.4 — Config B (True Mirror)
- [ ] Reprogram all 12 GreenPAKs per Config B from `EXPERIMENT_CONFIGS.md`
- [ ] N6 becomes 1/2 (octave subharmonic) instead of 1/1
- [ ] Re-run measurements 5.1–5.3
- [ ] Record all metrics in comparison table
- [ ] Then reprogram back to Config A and re-run (A-B-A pattern)

### 5.5 — Detuning robustness
- [ ] Reprogram one cell's frequency off by 15%
- [ ] Re-measure revival efficiency
- [ ] **Target:** Revival ≥ 85% (breadboard achieved this)

### 5.5 — Multi-board comparison
- [ ] Repeat Phases 1-5 on Board #2
- [ ] Compare Q_ℓ values — should be consistent across boards
- [ ] This confirms the result is from the design, not manufacturing variance

---

## 📊 Data Recording

For each measurement, log:
- Board number
- Date/time
- PSU voltage and current
- Ambient temperature
- Measurement values + scope screenshots
- Any anomalies

**Log location:** `projects/Prime_Maxel-v3/test_results/`

---

## 🔀 Decision Tree

```
Phase 1 FAIL (power short) → Inspect solder joints, fix, retry
Phase 2 FAIL (I2C missing) → Check address config, reflow solder
Phase 3 FAIL (no oscillation) → Verify GreenPAK programming, check OA0 routing
Phase 4 FAIL (no torsion signal) → Check LM324 buffer stage, verify TORSION net continuity
Phase 5 Q_ℓ ≈ 0.86 → 🎉 SUCCESS → fast-track v4 fab order
Phase 5 Q_ℓ ≠ 0.86 → Analyse deviation, adjust coupling, iterate
Phase 5 No revival → Revisit signal path assumptions, compare with breadboard config
```

---

## 🛠️ Tools Needed

| Tool | Purpose | Status |
|------|---------|--------|
| UNI-T UTP3315TFL bench PSU | Precise 5V supply + current monitoring | Ordered |
| Multimeter | Continuity, voltage, resistance | ✅ Have |
| DSO-153 (single ch) | Basic signal verification | ✅ Have |
| Dual-channel scope | Phase measurements (essential for Phase 4-5) | 🛒 Need |
| Arduino Mega 2560 | I2C control + pulse generation | Need to confirm |
| Stackable headers | Arduino↔v3 board connection | 🛒 Need |
| BNC-to-SMA cables | Scope↔board connection | Ordered |
| Renesas Go Configure | GreenPAK programming | Need to install |
| Magnifying loupe/phone | Visual inspection | ✅ Have |

---

---

## 🔬 Phase 6: Factorization Gravity Test (Post Bring-Up)

**Date added:** 2026-04-30
**Source:** Six-cell superposition simulation (`projects/Prime_Maxel-v4/research/six_cell_superposition.py`)

### Background
Simulation predicts that when multiple prime-frequency cells fire simultaneously, the |R+O|² (intensity/power) spectrum redistributes energy FROM prime frequencies TO composite frequencies. The Prime/Composite energy ratio flips from ~18:1 (raw bus) to ~1:2 (squared signal). This would be the **first physical evidence of factorization gravity** — the tendency of wave systems to move energy downhill from prime peaks into composite wells.

### Test Procedure
1. Complete Phases 1-5 (board functional, all cells oscillating, torsion signal present)
2. **Single-cell baseline:** Activate one GreenPAK cell at a time, record torsion bus signal via scope/ADC
3. **Pair-wise activation:** Activate cells in pairs (2+3, 2+5, 3+5, 2+7, etc.), record bus
4. **Full activation:** All cells firing simultaneously, record bus signal
5. **FFT analysis:** For each recording, compute:
   - Power spectrum of raw bus signal
   - Power spectrum of signal² (|R+O|² equivalent)
   - Energy at each 1/n frequency for n = 2..30
   - **P/C ratio** = (total energy at prime n) / (total energy at composite n)

### Expected Results (from simulation)
| Configuration | Raw P/C Ratio | |Signal|² P/C Ratio |
|---|---|---|
| Single cell | ∞ (only one prime) | ~1 (sum/diff only) |
| Two cells | High (~10+) | ~1-2 |
| All cells | ~18 | **~0.5** ← KEY PREDICTION |

### Success Criteria
- P/C ratio in raw signal >> 1 (confirms prime cells are driving)
- P/C ratio in |signal|² < 1 for full activation (confirms energy redistribution to composites)
- The ratio should decrease monotonically as more cells are added

### Additional Prediction (Adrian's Insight, Apr 30)
- The board's physical resolution (ADC bits, trace noise, bandwidth) should impose an **"iron peak"** — a composite frequency beyond which intermodulation products become indistinguishable from noise. This is the information-entropy counter-force to factorization binding. Measuring where this cutoff falls would quantify the board's "atomic number limit."

### Equipment
- All Phase 1-5 equipment
- Dual-channel scope (essential — need simultaneous capture for phase analysis)
- Software FFT (Python/numpy — scripts already written in v4 research folder)

### Reference Scripts
- `projects/Prime_Maxel-v4/research/six_cell_superposition.py` — simulation predicting the P/C flip
- `projects/Prime_Maxel-v4/research/holographic_factorization_test.py` — single vs multi-reference comparison
- `projects/Prime_Maxel-v4/research/binding_energy_isomorphism.py` — iron peak / entropy limit analysis

---

*The sun rises on v3. Let's measure reality.* 🐍☀️
