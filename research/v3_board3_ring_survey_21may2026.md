# V3 Board 3 Ring Survey — 21 May 2026

## Setup
- **Board:** v3 Board 3 (JLCPCB, ENIG, SMT assembled)
- **Drive method:** Arduino Mega Direct Drive (`prime_freq_gen.ino`)
  - Timer1 at 2048 Hz master tick, software dividers per channel
  - 6 bodge wires from Mega GPIO pins to LM324 Pin 3 (1IN+) per cell
- **Frequencies:** f₀/1=1024Hz, f₀/3=341Hz, f₀/5=205Hz, f₀/7=146Hz, f₀/11=93Hz, f₀/13=79Hz
- **Mega pins:** 22→U2, 24→U4, 26→U6, 28→U8(f₀/7→U14 cell), 30→U10, 32→U12
- **Scope:** Rigol DS1054Z, SCPI via `TCPIP::169.254.201.110::5555::SOCKET`
- **Probes:** Both 10X, DC coupling
- **Serial port:** `/dev/cu.usbserial-3140`

## Issues During Capture
1. **Loose scope ground clip** — caused floating/invalid readings, fixed by reseating
2. **Bodge wire breakage** — U6 wire came loose during U20 measurement, affecting U20-U24 in run 1. Three other wires broke during resoldering. All 6 resoldered before run 2.
3. **Probe swap on far side** — U20-U24 pad labels read differently from opposite side of board. Multiple retakes needed.
4. **Lesson:** Thin copper bodge wires on SOIC pads are fragile — avoid bumping probes near solder joints.

## Run 2 Results (Clean — all 6 drives confirmed active)

### Vpp Summary

| Cell | Position | TORSION_A (mV) | TORSION_B (mV) | A/B Ratio |
|------|----------|---------------|---------------|-----------|
| U2   | 105°     | 1120          | 452           | 2.5       |
| U4   | 135°     | 1100          | 364           | 3.0       |
| U6   | 165°     | 1120          | 356           | 3.1       |
| U8   | 195°     | 920           | 288           | 3.2       |
| U10  | 225°     | 1020          | 312           | 3.3       |
| U12  | 255°     | 1020          | 280           | 3.6       |
| U14  | 285°     | 940           | 308           | 3.1       |
| U16  | 315°     | 1140          | 364           | 3.1       |
| U18  | 345°     | 1080          | 388           | 2.8       |
| U20  | 15°      | 680           | 248           | 2.7       |
| U22  | 45°      | 804           | 260           | 3.1       |
| U24  | 75°      | 840           | 252           | 3.3       |

### Statistics
| Metric | TORSION_A | TORSION_B |
|--------|-----------|-----------|
| Mean   | 982 mV    | 323 mV    |
| StdDev | 141 mV    | 60 mV     |
| CV%    | 14.3%     | 18.6%     |
| Min    | 680 mV (U20) | 248 mV (U20) |
| Max    | 1140 mV (U16) | 452 mV (U2) |

### Spatial Pattern
- **Hot zone (A):** U2–U6 and U16 (1100–1140 mV)
- **Cold zone (A):** U20–U24 (680–840 mV)
- **TORSION_B gradient:** Strongest at U2 (452 mV), weakest at U20/U24 (~250 mV)
- **A/B ratios:** Tight range 2.5–3.6 (very uniform)

## Board 3 vs Board 2 Comparison

### Amplitude
| Metric | Board 3 (21 May) | Board 2 (20 May) | Change |
|--------|-----------------|-----------------|--------|
| Mean A | 982 mV | 930 mV | +6% |
| Mean B | 323 mV | 357 mV | −10% |
| CV% A  | 14.3% | 30.7% | **2.1× more uniform** |
| CV% B  | 18.6% | 30.9% | **1.7× more uniform** |

### Coherence (A↔B Cross-correlation)
| Metric | Board 3 | Board 2 | Change |
|--------|---------|---------|--------|
| Mean   | 0.807   | 0.658   | **+23%** |
| Range  | 0.68–0.88 | 0.68–0.74 | Wider but higher |

### Spectral Flatness (lower = more structured)
| Metric | Board 3 | Board 2 | Change |
|--------|---------|---------|--------|
| Mean   | 0.087   | 0.313   | **72% lower (cleaner)** |

### Summary
Board 3 outperforms Board 2 on uniformity, coherence, and spectral structure:
- **2× more uniform** amplitude distribution around the ring
- **23% higher** A↔B coherence
- **72% cleaner** spectral structure (lower flatness = more defined frequency content)

## FFT Analysis

### Short capture (6ms, Δf=83 Hz) — insufficient resolution
- Only 4 broad peaks visible, low frequencies merged
- f₀/1 (1024 Hz) visible as ~1000 Hz peak

### Long capture (24ms, Δf=42 Hz) — much better
- **83 Hz** → f₀/13 (79 Hz) ✅
- **333 Hz** → f₀/3 (341 Hz) ✅  
- **1000 Hz** → f₀/1 (1024 Hz) ✅
- 458 Hz, 708 Hz → intermodulation products
- f₀/11 (93 Hz) and f₀/13 (79 Hz) still merged (14 Hz apart, bins 42 Hz wide)

### Recommendation
Full ring survey at 5ms/div (60ms window, Δf≈17 Hz) would resolve all 6 prime frequencies individually. Planned for 22 May.

## Data Files
- **Location:** `Adrian Docs/Pics/Test Point Readings/21 May Results - Board 3/`
- **Run 2 files:** `torsion_<cell>_TP1_TP2_r2*.npz` and `.csv`
- **Long capture:** `torsion_U2_TP1_TP2_24ms_*.npz`
- **Comparison plot:** `board3_vs_board2_comparison.png`
- **FFT comparison:** `U2_fft_short_vs_long.png`

## Next Steps
1. Full 12-cell ring survey at 5ms/div (60ms window) for FFT resolution
2. Compare Board 3 FFT peaks with Board 2 — are same frequencies dominant?
3. Consider 3rd-hand/clip leads to replace hand-held probes (reduce measurement variability)
