# Prime_Maxel-v3 — Experimental Torsion Resonator Network

> First experimental evidence that prime-ratio frequency networks outperform composite-ratio networks in a physical resonator.

**Published:** [Zenodo DOI 10.5281/zenodo.20637347](https://doi.org/10.5281/zenodo.20637347)

## Overview

Prime_Maxel-v3 is a 12-cell torsion resonator ring built to test whether prime-ratio frequency relationships produce measurably different coupling behaviour compared to composite ratios. Each cell pairs a **SLG47004V GreenPAK** mixed-signal IC with an **LM324 op-amp**, connected via twin shared copper torsion traces on a 4-layer PCB fabricated by JLCPCB. An **Arduino Mega 2560** generates six independent square-wave channels using Timer1, fed into the ring through bodge wires. Output is captured on a **Rigol DS1054Z** oscilloscope and processed through a Python analysis pipeline.

Fifteen distinct frequency sets were tested across prime, composite, Fibonacci, zeta-zero, and coprimality configurations — producing the **Four-Factor Theory** of resonator coupling.

## Key Results

- **+28%** peak spectral amplitude (prime vs composite ratios)
- **+22%** inter-channel coherence
- **48% fewer** intermodulation products
- **Superlinear** amplitude growth across 6 prime channels (320 → 1160 mV)
- **15 distinct frequency sets** tested → Four-Factor Theory
- Tusk-resonant set {1, 2, 3, 5, 6, 7} exceeds pure primes by **24%**
- Riemann zeta zeros resonate at **85–90%** of prime performance
- All integer divisors produce identical coupling power — **coprimality governs spectral quality**

## Board Images

| Top | Bottom |
|-----|--------|
| ![Board top](docs/board_top.png) | ![Board bottom](docs/board_bottom.png) |

![Full board render](docs/board_all.png)

## Architecture

```
Arduino Mega (Timer1) → 6× square-wave channels → bodge wires
    ↓
12× cells (SLG47004V + LM324) in circular ring
    ↓
TORSION_A (498 mm) / TORSION_B (601 mm) shared copper traces
    ↓
Rigol DS1054Z → Python analysis pipeline
```

## Repository Structure

- `arduino/` — All Arduino sketches (prime, composite, zeta zero, progressive, coprimality experiments, etc.)
- `Nagaπ Python Scripts/` — Analysis pipeline (rigol_capture.py, torsion_analyze.py, experiment_suite_analysis.py)
- `research/` — Experimental results, detailed write-ups per experiment, and the published paper
- `LTspice_Sim/` — SPICE simulations of the golden cell circuit
- `Go Configure/` — GreenPAK configuration files
- `docs/` — Board renders
- `Libraries/` — Custom KiCad symbols and footprints
- KiCad project files at root

## Companion Publications

- **Prime Resonance Theory:** DOI [10.5281/zenodo.20541350](https://doi.org/10.5281/zenodo.20541350)
- **The Tusk Series:** DOI [10.5281/zenodo.19852116](https://doi.org/10.5281/zenodo.19852116)
- **Rational Algebraic Superformula:** DOI [10.5281/zenodo.20512346](https://doi.org/10.5281/zenodo.20512346)
- **Prime Tree Architecture:** DOI [10.5281/zenodo.20609886](https://doi.org/10.5281/zenodo.20609886)

## License

- **Hardware** (KiCad files): [CERN-OHL-S v2](https://ohwr.org/cern_ohl_s_v2.txt)
- **Code** (Arduino/Python): [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- **Research papers**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

See [LICENSE](LICENSE) for details.

## Author

**Adrian Sutton** — [Tusk Innovations](https://github.com/nagapi2357-ui)

AI Research Contributor: **Nagaπ**
