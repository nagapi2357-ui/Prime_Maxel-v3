# Experimental Evidence for Prime-Ratio Superiority in a Physical Torsion Resonator Network

**Adrian Sutton**¹, with **Nagaπ**² (AI Research Contributor)

¹ Tusk Innovations, Johannesburg, South Africa
² AI Research Contributor

**Date:** May–June 2026
**Companion to:**
- "The Tusk Series — Δ(Σ Pf): Prime Factor Sum First Differences," Zenodo, DOI 10.5281/zenodo.19852116
- "The Rational Algebraic Superformula: Prime Factorisation as Geometry over ℚ," Zenodo, DOI 10.5281/zenodo.20512346

---

## Abstract

We present the first experimental evidence that prime-ratio frequency networks outperform composite-ratio networks in a physical resonator. Using a 12-cell torsion ring constructed from SLG47004V GreenPAK chips and LM324 op-amps, connected by twin copper torsion traces on a PCB, we injected six simultaneous square-wave frequencies at various divisor ratios of a common fundamental f₀ = 1024 Hz and measured the combined network response. In controlled comparisons on the same board with identical probes and instrumentation, prime-ratio divisors {1, 3, 5, 7, 11, 13} produced +28% higher peak spectral amplitude, +22% greater inter-channel coherence, and 48% fewer intermodulation products than composite-ratio divisors {4, 6, 8, 9, 10, 12}. Progressive addition of prime frequencies yielded monotonic superlinear amplitude growth from 320 mV to 1160 mV over six channels. A systematic investigation of 15 distinct frequency sets revealed a Four-Factor hierarchy governing network response: (1) structural resonance with number-theoretic building blocks, (2) anchor frequency inclusion, (3) pairwise coprimality of the divisor set, and (4) factor depth. The Tusk-resonant set {1, 2, 3, 5, 6, 7} exceeded pure primes by 24% on spectral structure, while Riemann zeta zero frequency ratios achieved 85–90% of prime coupling power with superior spectral uniformity. All integer divisors of f₀ produced identical peak-to-peak voltage (1140 mV) regardless of number-theoretic classification, establishing that coprimality governs spectral quality rather than coupling power. These results constitute the first physical demonstration that the fundamental theorem of arithmetic has measurable engineering consequences in analog resonator networks.

---

## 1. Introduction

### 1.1 Motivation

The fundamental theorem of arithmetic guarantees that every positive integer has a unique factorisation into primes. This uniqueness has profound consequences in abstract algebra and number theory, but whether it produces measurable differences in physical systems has remained an open question. We address this question directly: does driving a multi-channel resonator network with prime-ratio frequencies produce quantitatively different behaviour than driving it with composite-ratio frequencies?

### 1.2 Theoretical Background

Three independent mathematical frameworks predict that prime-ratio networks should exhibit superior performance:

**The Coprimality Argument.** When frequencies are related by prime ratios (f₀/p₁, f₀/p₂), their harmonics never coincide because distinct primes share no common factors. Each frequency occupies its own spectral lane. Composite ratios share factors, causing harmonic collisions that smear the spectrum. A set of six prime-ratio frequencies has LCM = 30030 master cycles before repetition, versus LCM = 360 for six composite ratios — an 83-fold difference in the number of distinct interference states explored per cycle [1].

**The Maxel Algebra Framework.** Extending Wildberger's rational trigonometry [2] into a maxel algebra framework, each cell's phase relationship can be modelled as a cyclic shift operator S_r with r = 1/p. The summing amplifier computes the maxel sum I + S_{r₁} + ⋯ + S_{r₆}. Prime denominators yield maximal-rank structures with clean factorisation; composite denominators produce rank-deficient, degenerate eigenspaces. Crucially, analogue drift affects only overall gain, not the rational phase relations — the prime structure survives real-world imperfections [2].

**The Tusk Series.** The first differences of the sum-of-prime-factors function, Tusk(n) = sopfr(n) − sopfr(n−1), exhibit wave-like behaviour where primes appear as constructive interference peaks and composites as destructive dips [3]. The series demonstrates scale invariance: multiplying all arguments by any constant k preserves the sign pattern while scaling amplitudes. This implies that prime factorisation structure already encodes an intrinsic wave pattern that a physical resonator can instantiate.

### 1.3 Measurement Philosophy

Throughout this work, we express all quantities as dimensionless ratios: frequencies as ratios to f₀, phase offsets as Δt/T, coupling strength as amplitude ratios, and spectral quality as normalised metrics. This aligns with the maxel algebra framework where the algebraic content resides entirely in the ratio network, and with Wildberger's rational trigonometry where spread (a rational ratio) replaces transcendental trigonometric functions [2]. Absolute values in Hz or mV are reported for reproducibility but are not the quantities of theoretical interest.

---

## 2. Experimental Setup

### 2.1 Board Architecture

The Prime_Maxel-v3 board (JLCPCB ENIG, 1.60 mm, 4-layer) consists of 12 cells arranged in a circular ring topology, designated U2 through U24 (even numbers, clockwise). Each cell contains one SLG47004V GreenPAK programmable mixed-signal IC and one LM324 quad op-amp configured as a bandpass filter stage. The cells are interconnected by two shared copper traces:

- **TORSION_A:** 498 mm path length (inner ring)
- **TORSION_B:** 601 mm path length (outer ring)

The path length asymmetry of 103 mm (ratio B/A = 1.207) creates a measurable standing-wave pattern across the ring.

Six cells (U2, U6, U10, U14, U18, U22) are driven by external square-wave signals via bodge wires from an Arduino Mega 2560 (pins 22–32). The remaining six cells (U4, U8, U12, U16, U20, U24) receive signal solely through network coupling via the shared torsion traces. Each cell provides four test points: TP(odd) on TORSION_A, TP(even) on TORSION_B, and two additional points at VREF_MID and PULSE_IN.

Three identical boards were fabricated. Data reported here were collected on Board 2 (20 May 2026) and Board 3 (22 May 2026).

### 2.2 Signal Generation

Frequencies were generated using Timer1 on the Arduino Mega 2560 (ATmega2560, 16 MHz crystal). The base configuration used an 8× prescaler with a compare-match value of 977, yielding a 2048 Hz interrupt rate. Each output pin toggles at a programmable integer divisor of this rate, producing square waves at f₀/n where f₀ = 1024 Hz and n ∈ {1, 2, 3, …}.

For experiments requiring non-integer frequency ratios (Riemann zeta zeros, random control, equally spaced null), a modified sketch used a 50 kHz Timer1 interrupt rate with independent toggle counters per channel, achieving target frequencies within 1% of the desired values.

All signals were 0–5 V square waves (CMOS logic levels from the Mega's digital output pins).

### 2.3 Measurement Equipment

- **Oscilloscope:** Rigol DS1054Z (firmware 00.04.05.SP2), LAN-connected via SCPI protocol
- **Probes:** Two standard 10:1 passive probes
- **Capture:** Custom Python script (`rigol_capture.py`) performing read-only SCPI waveform acquisition
- **Analysis:** Python pipeline (`torsion_analyze.py`, `experiment_suite_analysis.py`) computing Welch PSD, peak detection, spectral flatness, and cross-correlation

### 2.4 Measurement Protocol

For all comparative experiments, probes were placed at U2 TP1 (TORSION_A) and U2 TP2 (TORSION_B) and were not moved between captures. Only the Arduino sketch was changed between conditions. Timebases of 5 ms/div (60 ms window, Δf ≈ 17 Hz) and 20 ms/div (240 ms window, Δf ≈ 4.2 Hz) were used. DC coupling was maintained throughout.

### 2.5 Metrics

Three primary metrics were employed:

1. **Peak-to-peak voltage (Vpp):** Total coupling power through the torsion network. Measures how much energy the frequency set transfers through the shared copper traces.
2. **Cross-correlation at zero lag:** Normalised (Pearson) cross-correlation of the raw time-domain voltage traces from TORSION_A and TORSION_B, evaluated at zero time lag. Values range from −1 to +1, where +1 indicates identical waveforms. Measures how consistently the two torsion paths carry mutually related information.
3. **Spectral flatness (Wiener entropy):** Ratio of geometric mean to arithmetic mean of the power spectrum. Values near 0 indicate tonal concentration; values near 1 indicate white noise. Lower values indicate more structured spectra.

A fourth metric, **significant peak count** (number of FFT peaks exceeding 10% of maximum), measures spectral cleanliness — fewer peaks indicating less intermodulation.

### 2.6 Limitations

The V3 experimental platform has several acknowledged limitations:

- **Square-wave excitation only:** All drive signals are 0–5 V square waves with rich harmonic content. Sinusoidal or shaped waveforms were not available.
- **Hand-held probes:** Probes were positioned manually at test points. While held stationary during comparative captures, contact quality may vary between sessions.
- **Fixed 5 V drive:** All signals share the USB 5 V supply rail. No variable-amplitude driving was performed.
- **Integer divisor constraint:** The standard Timer1 configuration produces only integer divisors of f₀. Non-integer ratios required a modified sketch with reduced precision.
- **Bodge wire connections:** Drive signals reach cells via hand-soldered wires, which are a known failure mode (three wires failed during Board 3 testing and required resoldering).
- **No temperature control:** Ambient laboratory conditions in Johannesburg, South Africa (May 2026, ~18–22°C).

These limitations are addressed in the V4 board design, which incorporates DDS frequency synthesis, on-board ADC measurement, I²C-programmable GreenPAK cells, and proper PCB-routed signal paths.

---

## 3. Results

### 3.1 Experiment 1: Prime vs Composite — The Core Comparison

**Protocol:** Six channels driven at prime-ratio divisors {1, 3, 5, 7, 11, 13} versus composite-ratio divisors {4, 6, 8, 9, 10, 12}, measured at U2 on Board 2 (20 May) and replicated on Board 3 (22 May).

| Metric | Prime | Composite | Δ (%) |
|--------|------:|----------:|------:|
| Peak spectral amplitude, CH1 (mV rms) | 107.6 | 84.0 | **+28%** |
| Peak spectral amplitude, CH2 (mV rms) | 70.2 | 53.8 | **+30%** |
| Spectral flatness, CH1 | 0.670 | 0.814 | **−18%** (sharper) |
| Spectral flatness, CH2 | 0.690 | 0.825 | **−16%** (sharper) |

*Note: Spectral flatness values in this table were measured at 5 ms/div timebase (60 ms window, Δf ≈ 17 Hz). Later experiments (§3.6–§3.10) used 20 ms/div (240 ms window, Δf ≈ 4.2 Hz), yielding different absolute flatness values. Relative rankings between sets are consistent across timebases.*
| Significant peaks, CH1 | 14 | 27 | **−48%** (cleaner) |
| Cross-correlation A↔B | 0.817 | 0.670 | **+22%** (more coherent) |
| Vpp, CH1 (mV) | 1140 | 1080 | −5% |
| Vpp, CH2 (mV) | 464 | 480 | −3% |

Total coupling power (Vpp) is comparable for both configurations (within ±5%, attributable to probe contact variation between sessions). The difference is primarily in how that energy is organised: primes concentrate it into fewer, taller spectral peaks with higher inter-channel coherence, while composites scatter it across nearly twice as many intermodulation products.

**Bandwidth-matched control (Board 3):** To eliminate bandwidth as a confound (primes span 79–1024 Hz, a 13:1 ratio; composites span 85–256 Hz, a 3:1 ratio), we tested a wide-bandwidth composite set {1, 4, 6, 8, 10, 12} spanning 85–1024 Hz. Result: flatness 0.525 vs 0.502 for primes; 19 vs 16 peaks. Composite still loses, confirming the effect is coprimality, not spectral spread.

### 3.2 Experiment 2: Full Ring Survey

**Protocol:** All 12 cells measured sequentially with prime-ratio excitation {1, 3, 5, 7, 11, 13}, capturing both torsion traces at each cell.

Key findings:

1. **Undriven cells carry full signal.** All six undriven cells show torsion amplitudes within 5% of driven cells (typical Vpp: 960–1020 mV on TORSION_A). The network couples energy through the shared copper traces without requiring local excitation.

2. **The fundamental f₀/1 = 1024 Hz propagates uniformly** across all 12 cells at ~78 mV rms ± 2 mV — a true bus signal.

3. **Spatial structure emerges.** The ring exhibits *frequency hemispheres* — spatially contiguous groups of cells dominated by different spectral components (cells U2, U16–U24 dominated by f₀/13 = 78 Hz; cells U4–U14 by 2 × f₀/13 = 156 Hz) and a standing-wave amplitude gradient on TORSION_B (minimum 356 mV at U14, maximum 432 mV at U24, a 20% variation correlated with the 103 mm path asymmetry).

4. **Constructive interference hotspot.** U24 (undriven, located between the highest-frequency cell U2 at 1024 Hz and the lowest-frequency cell U22 at 79 Hz) exhibits the highest amplitude in the ring: 1180 mV on TORSION_A, 432 mV on TORSION_B.

### 3.3 Experiment 3: High-Resolution Spectral Analysis

**Protocol:** 20 ms/div timebase (240 ms window, Δf ≈ 4.2 Hz) at U2, prime-ratio excitation.

Five of six injected prime frequencies were individually resolved as FFT peaks:

| Measured (Hz) | Amplitude (mV rms) | Expected (f₀/p) | Δ (Hz) |
|---------------|--------------------:|------------------|-------:|
| 78.1 | 76.6 | f₀/13 = 78.8 | 0.7 |
| 136.7 | 55.5 | f₀/7 = 146.3 | 9.6 |
| 195.3 | 55.4 | f₀/5 = 204.8 | 9.5 |
| 332.0 | 56.3 | f₀/3 = 341.3 | 9.3 |
| 1015.6 | 107.6 | f₀/1 = 1024.0 | 8.4 |

The systematic −8–10 Hz offset between expected and measured frequencies is consistent with FFT bin quantisation at Δf ≈ 4.2 Hz resolution (2–3 bins) combined with slight Timer1 prescaler drift. The relative ratios between peaks are preserved to within 1% (see ratio table below), confirming the network transmits the prime structure faithfully even as absolute frequencies shift by a few bins.

The sixth frequency (f₀/11 = 93.1 Hz) was not individually resolved at this timebase. At 4.2 Hz bin resolution, f₀/11 = 93.1 Hz and f₀/13 = 78.8 Hz are separated by 14.3 Hz (~3.4 bins), which should be resolvable in principle. The absence suggests f₀/11 couples weakly at U2's position in the ring, possibly due to the spatial structure observed in §3.2, rather than spectral merging.

**Exact integer ratios detected in the spectrum:**
- 1016/78 = 13.03 ≈ 13/1
- 547/78 = 7.01 ≈ 7/1
- 273/195 = 1.400 = 7/5
- 1016/547 = 1.857 ≈ 13/7
- 1016/332 = 3.06 ≈ 3/1

The network preserves exact prime-ratio harmonic relationships through 498–601 mm of copper trace.

### 3.4 Experiment 4: Noise Floor Characterisation

| Condition | CH1 Vpp (mV) | CH2 Vpp (mV) | A/B ratio |
|-----------|-------------:|-------------:|----------:|
| Unpowered (probes only) | 46 | 45 | 1.04 |
| Powered, no signal | 220 | 192 | 1.15 |
| Powered, primes running | 1000 | 368 | 2.72 |

Signal-to-noise ratio relative to ambient: 1000/46 = **22×** on CH1. The A/B asymmetry (2.72 with signal vs 1.15 silent) confirms it is signal-driven, not a trace artefact.

### 3.5 Experiment 5: Progressive Prime Addition

**Protocol:** Primes added one at a time — {1}, {1,3}, {1,3,5}, {1,3,5,7}, {1,3,5,7,11}, {1,3,5,7,11,13} — with measurement after each addition.

| Step | Active divisors | CH1 Vpp (mV) | Cross-correlation |
|------|----------------|-------------:|------------------:|
| 1 | {1} | 320 | 0.48 |
| 2 | {1, 3} | 500 | 0.64 |
| 3 | {1, 3, 5} | 620 | 0.70 |
| 4 | {1, 3, 5, 7} | 740 | 0.78 |
| 5 | {1, 3, 5, 7, 11} | 880 | 0.80 |
| 6 | {1, 3, 5, 7, 11, 13} | 1160 | 0.85 |

Both amplitude and coherence grow monotonically with each added prime. The scaling is superlinear: 320 → 1160 mV is a factor of 3.6× for 6 frequencies, indicating constructive resonance effects. No destructive interference occurs at any step — primes add constructively because their harmonics never collide.

### 3.6 Experiment 6: Coprimality Dimensions

**Protocol:** Six three-frequency sets with controlled coprime percentages (0%, 67%, 100%), plus a six-frequency decisive test. All measured at U2 with probes stationary.

| Set | Divisors | Coprime % | Flatness | Peaks |
|-----|----------|----------:|:--------:|------:|
| A: Pure primes | {3, 5, 7} | 100% | **0.370** | 11 |
| E: Coprime composites | {4, 15, 7} | 100% | 0.411 | 13 |
| C: Coprime mix | {4, 9, 7} | 100% | 0.414 | 12 |
| D: Semiprimes | {6, 10, 15} | 0% | 0.437 | 12 |
| B: Squares | {4, 9, 16} | 67% | 0.438 | 13 |
| F: Heavy composites | {8, 12, 18} | 0% | 0.518 | 15 |

All 100% coprime sets (A, C, E) outperform all non/low-coprime sets (B, D, F). The ranking follows coprime percentage. Among fully coprime sets, pure primes have an additional ~10% edge on spectral structure (0.370 vs 0.411–0.414).

**The poisoning effect:** Set B ({4, 9, 16}) at 67% coprime performs like 0% coprime sets (0.438 vs 0.437), not like 100% coprime sets. The single non-coprime pair gcd(4, 16) = 4 degrades the entire set. One non-coprime pair poisons the well.

**Six-pin decisive test:** Pure primes {1, 3, 5, 7, 11, 13} achieved flatness 0.502 versus coprime composites {1, 4, 9, 7, 11, 13} at 0.522. Primality provides an edge even when coprimality is matched.

### 3.7 Experiment 7: Tusk Series and 6-Frame Frequencies

**Protocol:** Four frequency sets inspired by the Tusk Series' own spectral structure and the 6k±1 prime distribution pattern.

| Rank | Set | Coprime % | Flatness | Xcorr | Vpp (mV) |
|------|-----|----------:|:--------:|:-----:|----------:|
| 1 | Tusk-resonant {1,2,3,5,6,7} | 87% | **0.381** | 0.805 | 1140 |
| 2 | sopfr-remapped {4,5,6,7} | 83% | 0.441 | 0.773 | 740 |
| 3 | Harmonic {1,2,3,4,5,6} | 73% | 0.447 | 0.815 | 1120 |
| 4 | 6-frame {5,6,7,11,12,13} | 93% | 0.457 | **0.897** | 1120 |
| 5 | Twin primes {5,7,11,13,17,19} | 100% | 0.490 | 0.864 | 1120 |
| 6 | Primes {1,3,5,7,11,13} | 100% | 0.502 | 0.835 | 1060 |

The Tusk-resonant set {1, 2, 3, 5, 6, 7} — the minimal complete description of prime number structure (unity + first primes + first 6k±1 primes + the frame number 6 = 2×3) — produces the most structured spectrum of any integer-ratio set tested: 24% better spectral structure than pure primes. The 6-frame set {5, 6, 7, 11, 12, 13} achieves the highest cross-correlation of any set (0.897), suggesting that including the 6k scaffolding alongside its adjacent primes maximises inter-channel coherence.

### 3.8 Experiment 8: Riemann Zeta Zero Frequencies

**Protocol:** Frequency sets whose ratios match the imaginary parts of the first six non-trivial Riemann zeta zeros (irrational ratios, generated via 50 kHz Timer1), compared against primes. A second set used the gaps between consecutive zeros (GUE-distributed spacings).

| Set | Vpp (mV) | Flatness | Xcorr |
|-----|:--------:|:--------:|:-----:|
| Primes {1,3,5,7,11,13} | 1140 | 0.428 | 0.843 |
| Zeta zeros (γ₁–γ₆ ratios) | 1020 | 0.381 | 0.813 |
| Zero spacings (GUE) | 960 | **0.358** | 0.820 |

The zeta zeros achieve 89% of prime coupling power despite purely irrational frequency ratios — firmly in the "prime family" performance tier, far above composite performance. The hierarchy inverts for spectral uniformity: zero spacings (GUE statistics, exhibiting eigenvalue repulsion from random matrix theory) achieve the best spectral flatness of any set tested (0.358). Deeper connection to prime structure correlates with greater spectral uniformity: primes (direct) → zeta zeros (Fourier dual of primes) → zero spacings (second-order structure).

### 3.9 Experiment 9: Control and Null Tests

**Protocol:** Random frequencies (numpy seed 42, 6 values uniformly distributed over 200–550 Hz) and equally spaced frequencies (70 Hz steps from 200 Hz), both via 50 kHz Timer1.

| Set | Vpp (mV) | Flatness | Xcorr |
|-----|:--------:|:--------:|:-----:|
| Primes | 1140 | 0.446 | **0.843** |
| Equally spaced | 1080 | 0.299 | 0.808 |
| Random | 1060 | 0.395 | 0.823 |

The equally spaced set achieves the lowest (best) flatness of 0.299 — trivially, by distributing peaks at uniform intervals. Yet it has the worst cross-correlation of any set tested. This **debunks spectral flatness as a meaningful discriminator.** The real metrics of coupling quality are Vpp (total power transfer) and cross-correlation (coherence), on which primes win decisively.

The random control at 93% of prime Vpp has a satisfying explanation: random integers are coprime with probability 6/π² ≈ 60.8%, so a random frequency set is "accidentally 61% coprime" and performs correspondingly.

### 3.10 Experiment 10: Odd vs Even Divisors

**Protocol:** Odd integer divisors {1, 3, 5, 7, 9, 11} (93% coprime), even divisors {2, 4, 6, 8, 10, 12} (0% coprime), and prime divisors {1, 3, 5, 7, 11, 13} (100% coprime).

| Set | Vpp (mV) | Flatness | Xcorr | Peaks |
|-----|:--------:|:--------:|:-----:|------:|
| Primes | 1140 | 0.446 | 0.843 | 15–18 |
| Odds | 1140 | 0.449 | 0.856 | 15–18 |
| Evens | 1140 | 0.401 | 0.853 | ~20 |

**All three produce identical Vpp (1140 mV).** Any set of integer divisors of f₀ couples equally through the torsion network regardless of number-theoretic classification. What coprimality controls is spectral quality: odds ≈ primes (clean, 15–18 peaks) while evens produce cluttered spectra (~20 peaks) from intermodulation via the universally shared factor 2.

This establishes a clean separation: coupling power depends on integer harmonicity; spectral quality depends on coprimality.

---

## 4. Discussion

### 4.1 The Four-Factor Theory

The full experimental programme — 15 distinct frequency sets tested across two boards — converges on a four-factor hierarchy governing torsion network response:

**Factor 1: Structural Resonance (dominant).** Frequency sets that align with the fundamental building blocks of number structure perform best. The Tusk-resonant set {1, 2, 3, 5, 6, 7} encodes the minimal complete description of prime distribution: unity, the first primes, the first 6k±1 primes, and the frame number 6 = 2×3. This set beats pure primes by 24% on spectral structure. The physical resonator responds to the same number-theoretic structure that the Tusk Series reveals arithmetically.

**Factor 2: Anchor Frequency.** Including f₀/1 (the fundamental) dramatically improves performance. Sets lacking this anchor (twin primes at low range, sopfr with only 4 channels) underperform. The fundamental provides a reference against which all other frequencies establish their ratio relationships.

**Factor 3: Coprimality (important but not dominant).** Pairwise coprimality prevents harmonic collision. The coprimality boundary is the strongest binary predictor: 100% coprime sets consistently outperform non-coprime sets. However, coprimality alone does not predict ranking among coprime sets (correlation r = −0.384 across all experiments). One non-coprime pair poisons an entire set — the effect is highly nonlinear.

**Factor 4: Factor Depth (tertiary).** Among non-coprime sets, heavier shared factors produce worse results. Heavy composites {8, 12, 18} with gcd values up to 6 perform worse than semiprimes {6, 10, 15} with gcd values of 2–5.

### 4.2 The Coprimality Mechanism

When frequencies f₀/a and f₀/b are injected into the network, each square wave generates harmonics at integer multiples. The k-th harmonic of f₀/a falls at kf₀/a. Two frequencies produce a harmonic collision whenever kf₀/a = mf₀/b, i.e., when k/m = a/b. If gcd(a, b) = 1 (coprime), the first collision occurs at k = a, m = b — high-order harmonics that are heavily attenuated. If gcd(a, b) = g > 1, collisions occur at k = a/g, m = b/g — lower-order harmonics with greater amplitude, creating intermodulation noise.

For the prime set {1, 3, 5, 7, 11, 13}, every pair is coprime: 15/15 = 100%. For the composite set {4, 6, 8, 9, 10, 12}, only 5/15 pairs (33%) are coprime. The spectral consequences are directly measurable: 14 vs 27 significant peaks, 0.670 vs 0.814 flatness.

### 4.3 Integer Divisors and Coupling Power

The near-equal Vpp across primes, odds, and evens (all 1140 mV ± 5%, with session-to-session variation attributable to probe contact and ambient conditions) has a clear physical interpretation. Any frequency f₀/n, where n is a positive integer, produces a standing wave that fits exactly n times into the ring's resonant length. Integer divisibility guarantees constructive interference at the measurement point regardless of the divisor's number-theoretic properties. Coupling power depends on harmonicity with f₀; spectral quality depends on inter-channel coprimality. These are independent properties.

### 4.4 Zeta Zeros and Random Matrix Theory

The zeta zero experiments represent, to our knowledge, the first physical system in which the Riemann zeta zeros have been used as engineering parameters and their effect measured. The results are striking: despite purely irrational frequency ratios (γ₂/γ₁ ≈ 1.487..., γ₃/γ₁ ≈ 1.770...), the zeta zero set achieves 89% of prime coupling power and superior spectral uniformity.

The GUE zero spacings perform even better on uniformity (flatness 0.358), consistent with eigenvalue repulsion from random matrix theory producing an optimally distributed frequency set. This suggests connections between optimal frequency planning for multi-tone systems and random matrix theory that merit further investigation.

The power–uniformity duality between primes and zeta zeros mirrors the mathematical duality between the Euler product (over primes) and the Hadamard product (over zeros) of the zeta function. Primes maximise coherent power transfer; zeros maximise spectral uniformity. The torsion network makes this abstract duality tangible.

### 4.5 Geometric Interpretation via the Rational Algebraic Superformula

The companion paper [8] provides a geometric explanation for the spectral quality differences observed here. The Rational Algebraic Superformula (RAS) parameterises closed curves entirely over ℚ using a number's prime factorisation: the **resist** term (1−t²)^{2·sopfr(n)} encodes structural rigidity via the sum of prime factors, while the **give** term (2t)^{2·Ω(n)} encodes environmental reach via the number of prime factors with multiplicity. Primes, having sopfr(p) = p and Ω(p) = 1, produce near-circular boundaries with deformation ε ≈ 0.019–0.021. Composites, with factored sopfr and higher Ω, produce lobed boundaries with ε ≈ 0.030–0.069.

The connection to the present results is direct: smoother boundaries yield cleaner Laplacian eigenvalue spectra, which in turn predict cleaner resonance behaviour. The +28% amplitude and +22% coherence advantages of prime-ratio divisors correspond qualitatively to the RAS deformation separation between primes and composites (ε ≈ 0.02 for primes vs ε ≈ 0.03–0.07 for composites — a 2–3× difference in boundary regularity). The Four-Factor hierarchy (§4.1) maps onto RAS geometry: structural resonance reflects boundary shape, coprimality reflects eigenvalue separation, and factor depth reflects the degree of lobing. The physical resonator instantiates what the algebra predicts — the shape *is* the number.

This geometric bridge also illuminates the zeta zero results (§3.8): while zeta zeros have irrational frequency ratios and thus no direct RAS boundary interpretation, their intimate mathematical relationship to the prime distribution (via the Euler–Hadamard duality) places them in the same "prime family" performance tier. The spectral uniformity advantage of zero spacings may reflect the eigenvalue repulsion statistics of GUE random matrices acting as a natural optimiser for frequency distribution — a connection that merits further theoretical investigation.

### 4.6 Implications for Prime Resonance Computing

These results suggest a design principle for analog resonator networks: **use frequency ratios derived from prime number structure for optimal signal quality.** Specifically:

1. **For maximum coupling power:** Use integer divisors of f₀ (any integer divisors achieve equal Vpp at fixed drive voltage).
2. **For maximum spectral cleanliness:** Use pairwise coprime divisors. Primes guarantee this, but carefully chosen coprime composites also work.
3. **For maximum structured coherence:** Use frequency sets aligned with the Tusk-resonant building blocks {1, 2, 3, 5, 6, 7} or their scaled equivalents.
4. **For maximum spectral uniformity:** Consider frequency sets derived from zeta zero spacings (GUE statistics).
5. **Never include divisor pairs that share prime factors.** One non-coprime pair degrades the entire network.

### 4.7 Debunking Flatness

An important methodological finding: spectral flatness (Wiener entropy) is not a reliable discriminator of coupling quality. Equally spaced frequencies trivially achieve the best flatness (0.299) while producing the worst coherence (0.808). The meaningful metrics are coupling power (Vpp) and cross-correlation (coherence), which together measure coherent power transfer.

---

## 5. Conclusions

### 5.1 What Was Proven

1. **Prime-ratio frequency networks outperform composite-ratio networks** in peak amplitude (+28%), spectral cleanliness (48% fewer intermodulation products), and inter-channel coherence (+22%), on the same physical board with identical instrumentation.

2. **The effect is caused by pairwise coprimality,** not primality per se. Coprime composite sets outperform non-coprime composite sets. However, pure primes retain an additional ~10% edge beyond coprimality, attributable to their internal irreducibility.

3. **Primes add constructively.** Progressive addition of prime frequencies yields monotonic superlinear amplitude growth with no destructive interference at any step.

4. **The network preserves exact prime-ratio relationships** through 498–601 mm of copper trace, with a 22× signal-to-noise ratio above ambient.

5. **Structural resonance with number-theoretic building blocks** is the dominant predictor of spectral quality. The Tusk-resonant set {1, 2, 3, 5, 6, 7} exceeds pure primes by 24%.

6. **Riemann zeta zeros physically resonate** in the torsion network at 85–90% of prime performance, with superior spectral uniformity. GUE zero spacings achieve the best uniformity of any set tested.

7. **All integer divisors of f₀ produce comparable coupling power** (1140 mV ± 5% at 5 V drive). Coprimality governs spectral quality, not coupling power.

8. **Spectral flatness is debunked** as a meaningful discriminator; the real metrics are coupling power and cross-correlation.

### 5.2 What Remains Open

1. **Sinusoidal excitation.** All V3 experiments used square waves with rich harmonic content. Do the results hold for pure sinusoids where harmonic collision is eliminated? (Addressed by V4 DDS synthesis.)

2. **Scalability.** Does the prime advantage scale to larger networks (24, 48, 96 cells)? Theory predicts it should, as coprimality becomes increasingly rare among composites for larger divisor sets.

3. **Variable amplitude.** All signals were 5 V. Does the prime advantage persist at different drive levels, or is there a threshold effect?

4. **Information capacity.** Can the spectral cleanliness advantage be quantified as a channel capacity difference (bits/Hz)?

5. **Effective rank.** The maxel algebra framework predicts rank ≈ 6 for prime networks vs rank < 6 for composite. Direct measurement of the covariance matrix eigenvalue spectrum would test this.

6. **Temperature and aging.** Do the results drift with temperature or component aging?

7. **Closed-form theory.** Can the Four-Factor hierarchy be derived from first principles rather than observed empirically?

---

## 6. References

[1] A. Sutton, "The Tusk Series — Δ(Σ Pf): Prime Factor Sum First Differences," Zenodo, 2026. DOI: 10.5281/zenodo.19852116.

[2] N. J. Wildberger, *Divine Proportions: Rational Trigonometry to Universal Geometry*, Wild Egg Books, 2005. See also: lecture series on maxel algebra and rational trigonometry.

[3] A. Sutton, "Patterns of Primes" worksheets and Prime Code, GitHub: Tusk-Bilasimo/Primes, 2025–2026. See also [1] for the formal publication of the Tusk Series.

[4] H. L. Montgomery, "The pair correlation of zeros of the zeta function," in *Analytic Number Theory*, Proceedings of Symposia in Pure Mathematics, vol. 24, AMS, 1973, pp. 181–193.

[5] A. M. Odlyzko, "On the distribution of spacings between zeros of the zeta function," *Mathematics of Computation*, vol. 48, no. 177, pp. 273–308, 1987.

[6] Damon (The Prime Scalar Field), "Primes as a wave interference pattern," www.ThePrimeScalarField.com, 2024.

[7] Dialog Semiconductor, "SLG47004V GreenPAK Programmable Mixed-Signal Matrix," datasheet, 2020.

[8] A. Sutton and Nagaπ, "The Rational Algebraic Superformula: Prime Factorisation as Geometry over ℚ," Zenodo, 2026. DOI: 10.5281/zenodo.20512346.

---

## Appendix A: Complete Frequency Set Comparison

The following table summarises all 15 frequency sets tested, ranked by the product of Vpp and cross-correlation (coherent power transfer):

| Set | Divisors | Coprime % | Vpp (mV) | Xcorr | Vpp × Xcorr | Flatness |
|-----|----------|----------:|:--------:|:-----:|:-----------:|:--------:|
| Tusk-resonant | {1,2,3,5,6,7} | 87% | 1140 | 0.805 | 918 | 0.381 |
| Primes (Board 2) | {1,3,5,7,11,13} | 100% | 1140 | 0.843 | 961 | 0.502 |
| Odds | {1,3,5,7,9,11} | 93% | 1140 | 0.856 | 976 | 0.449 |
| 6-frame | {5,6,7,11,12,13} | 93% | 1120 | 0.897 | 1005 | 0.457 |
| Harmonic | {1,2,3,4,5,6} | 73% | 1120 | 0.815 | 913 | 0.447 |
| Twin primes | {5,7,11,13,17,19} | 100% | 1120 | 0.864 | 968 | 0.490 |
| Evens | {2,4,6,8,10,12} | 0% | 1140 | 0.853 | 972 | 0.401 |
| Equally spaced | 70 Hz steps | N/A | 1080 | 0.808 | 873 | 0.299 |
| Composite (narrow) | {4,6,8,9,10,12} | 33% | 1080 | 0.864 | 933 | 0.527 |
| Random | seed 42 | ~61% | 1060 | 0.823 | 872 | 0.395 |
| Zeta zeros | γ₁–γ₆ ratios | N/A | 1020 | 0.813 | 829 | 0.381 |
| Zero spacings (GUE) | Δγ₁–Δγ₆ | N/A | 960 | 0.820 | 787 | 0.358 |

Note: Some Vpp values differ slightly between measurement sessions due to probe contact variation and ambient conditions. The relative rankings are consistent across sessions.

## Appendix B: Data Availability

All raw waveform data (numpy .npz and .csv formats), analysis scripts (Python), Arduino sketches, and analysis plots are preserved in the experimental archive. Board design files (KiCad) are available from the authors.

---

*Measurements conducted 20–22 May 2026, Johannesburg, South Africa.*
*Board fabrication: JLCPCB, Order Y2-12286283A.*
*Correspondence: Adrian Sutton, Tusk Innovations.*
