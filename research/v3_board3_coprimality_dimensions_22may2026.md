# V3 Board 3 — Coprimality Dimensions: Isolating the Mechanism — 22 May 2026

## Executive Summary

**Coprimality is the dominant factor governing signal quality in the torsion network, but primality itself contributes an additional ~10% edge. We propose a Three-Factor Theory: coprimality (dominant), primality (secondary), factor depth (tertiary).**

Following the discovery of the Coprimality Principle earlier on 22 May, we designed 8 frequency sets to disentangle coprimality from primality. Three-pin tests with controlled coprime percentages (0%, 67%, 100%) show that 100% coprime sets always beat non-coprime sets — but among 100% coprime sets, pure primes {3,5,7} outperform coprime composites {4,9,7} and {4,15,7} by ~10% on spectral flatness. Adrian's insight about squares is confirmed: one non-coprime pair (gcd(4,16)=4) poisons the entire set. The 6-pin decisive test confirms the pattern at full scale.

---

## Equipment

| Item | Details |
|------|---------|
| Board | Prime_Maxel-v3, JLCPCB ENIG 1.60mm, SMT assembled, **Board 3** |
| MCU | Arduino Mega 2560 (Communica clone), USB-powered |
| Serial | /dev/cu.usbserial-3140 |
| Scope | Rigol DS1054Z (FW 00.04.05.SP2), LAN-connected via SCPI |
| Probes | 2× standard 10:1 passive probes at U2 (TP1 + TP2), never moved |
| Power | USB 5V only (barrel jack not used — safety constraint) |
| Software | Custom Arduino sketches (Timer1 ISR), Python analysis pipeline |
| Base frequency | f₀ = 1024 Hz (Timer1: 16MHz/8/977 ≈ 2048 Hz toggle rate) |

---

## Background

Earlier on 22 May we discovered the "Coprimality Principle" — that coprime frequency sets outperform non-coprime sets regardless of whether divisors are prime or composite. The harmonic series {1,2,3,4,5,6} surprisingly won on spectral flatness despite containing composites, because most pairs are coprime (11/15 = 73%).

This raised the question: **is coprimality the ENTIRE explanation, or does primality itself contribute something additional?**

Adrian suggested testing squares (p²), semiprimes (p×q), and examining how "factor depth" influences the results. This experiment suite isolates each variable.

---

## Experiment Design: Three-Frequency Sets

We designed 6 sets of 3 frequencies each (3 Arduino pins active, 3 OFF), plus one decisive 6-pin test. All measured at U2, probes never moved, only Arduino sketch changed between captures.

| Set | Divisors | Type | Coprime% | Frequencies |
|-----|----------|------|----------|-------------|
| A | {3,5,7} | Pure primes | 100% | 341, 205, 146 Hz |
| B | {4,9,16} | Squares (2²,3²,2⁴) | 67% | 256, 114, 64 Hz |
| C | {4,9,7} | Coprime squares+prime | 100% | 256, 114, 146 Hz |
| D | {6,10,15} | Semiprimes (2×3, 2×5, 3×5) | 0% | 171, 102, 68 Hz |
| E | {4,15,7} | Coprime composites (2², 3×5, prime) | 100% | 256, 68, 146 Hz |
| F | {8,12,18} | Heavy composites (2³, 2²×3, 2×3²) | 0% | 128, 85, 57 Hz |
| G | {1,4,9,7,11,13} | 6-pin coprime composites+primes | 100% | 1024, 256, 114, 146, 93, 79 Hz |
| REF | {1,3,5,7,11,13} | 6-pin pure primes (from earlier) | 100% | 1024, 341, 205, 146, 93, 79 Hz |

### Key Design Choices

- **Set B** tests Adrian's insight about squares: {4,9,16} where gcd(4,16)=4 because 16=2⁴ shares factor 2 with 4=2²
- **Sets C and E** test whether coprime composites match pure primes
- **Set G** is the decisive test: 6-pin set with 100% coprimality but containing composites 4 and 9

---

## Coprimality Analysis — Pairwise GCD

### Set A: {3, 5, 7} — Pure Primes (100% coprime)
| Pair | GCD | Coprime? |
|------|-----|----------|
| (3,5) | 1 | ✅ |
| (3,7) | 1 | ✅ |
| (5,7) | 1 | ✅ |

### Set B: {4, 9, 16} — Squares (67% coprime)
| Pair | GCD | Coprime? |
|------|-----|----------|
| (4,9) | 1 | ✅ |
| (4,16) | **4** | ❌ |
| (9,16) | 1 | ✅ |

**Key insight:** Squares of DIFFERENT primes are coprime (gcd(4,9) = gcd(2²,3²) = 1), but squares of the SAME prime base are not (gcd(4,16) = gcd(2²,2⁴) = 4).

### Set C: {4, 9, 7} — Coprime Mix (100% coprime)
| Pair | GCD | Coprime? |
|------|-----|----------|
| (4,9) | 1 | ✅ |
| (4,7) | 1 | ✅ |
| (9,7) | 1 | ✅ |

### Set D: {6, 10, 15} — Semiprimes (0% coprime)
| Pair | GCD | Coprime? |
|------|-----|----------|
| (6,10) | 2 | ❌ |
| (6,15) | 3 | ❌ |
| (10,15) | 5 | ❌ |

Every pair shares a prime factor. Maximum harmonic collision.

### Set E: {4, 15, 7} — Coprime Composites (100% coprime)
| Pair | GCD | Coprime? |
|------|-----|----------|
| (4,15) | 1 | ✅ |
| (4,7) | 1 | ✅ |
| (15,7) | 1 | ✅ |

### Set F: {8, 12, 18} — Heavy Composites (0% coprime)
| Pair | GCD | Coprime? |
|------|-----|----------|
| (8,12) | 4 | ❌ |
| (8,18) | 2 | ❌ |
| (12,18) | 6 | ❌ |

Worst case: large shared factors (gcd up to 6).

---

## Results

### 3-Pin Sets (A–F) Ranked by Spectral Flatness

| Rank | Set | Divisors | Coprime% | Flatness | Peaks | Xcorr | CH1 Vpp |
|------|-----|----------|----------|----------|-------|-------|---------|
| 1 | A: Pure primes | {3,5,7} | 100% | **0.370** | 11 | 0.711 | 640 mV |
| 2 | E: Coprime comp | {4,15,7} | 100% | 0.411 | 13 | 0.737 | 680 mV |
| 3 | C: Coprime mix | {4,9,7} | 100% | 0.414 | 12 | 0.763 | 700 mV |
| 4 | D: Semiprimes | {6,10,15} | 0% | 0.437 | 12 | 0.778 | 640 mV |
| 5 | B: Squares | {4,9,16} | 67% | 0.438 | 13 | 0.743 | 660 mV |
| 6 | F: Heavy comp | {8,12,18} | 0% | **0.518** | 15 | 0.778 | 700 mV |

**Clear separation:** All 100% coprime sets (A, C, E) rank 1–3. All non/low-coprime sets (D, B, F) rank 4–6.

### 6-Pin Decisive Test

| Set | Divisors | Flatness | Peaks | Xcorr | CH1 Vpp |
|-----|----------|----------|-------|-------|---------|
| REF: Pure primes | {1,3,5,7,11,13} | **0.502** | 16 | 0.835 | 1060 mV |
| G: Coprime composites | {1,4,9,7,11,13} | 0.522 | 14 | 0.864 | 1240 mV |

Pure primes win on flatness even when both sets have 100% coprimality. The primality effect persists at full scale.

---

## Key Findings

### 1. Coprimality is the Dominant Factor
All three 100% coprime sets (A, C, E) beat all non/low-coprime sets on flatness. The coprimality boundary is the strongest predictor: 0.370–0.414 for coprime vs 0.437–0.518 for non-coprime.

### 2. Pure Primes Have an Additional Edge
A (0.370) beats C (0.414) and E (0.411) despite all being 100% coprime. There's something about primality itself beyond coprimality — approximately a 10% advantage.

### 3. Factor Depth Matters
Among non-coprime sets: F (heavy composites {8,12,18} with gcds of 2,4,6) is worst at 0.518. D (semiprimes {6,10,15} with gcds of 2,3,5) is 0.437. Heavier factor-sharing produces worse results.

### 4. Adrian's Squares Insight Confirmed
B ({4,9,16}) at 67% coprime performs like the 0% coprime sets (0.438), not like the 100% coprime sets (0.370–0.414). The single non-coprime pair gcd(4,16)=4 drags down the whole set. **One non-coprime pair poisons the well.**

### 5. The Xcorr Paradox Continues
Non-coprime sets often show higher xcorr (D: 0.778, F: 0.778) than coprime sets (A: 0.711). This is because closely-spaced, factor-sharing frequencies naturally correlate — but this is "trivial" coherence (frequencies marching in lockstep), not "structured" coherence (independent frequencies creating complex but organized patterns).

---

## The Three-Factor Theory

Three factors govern signal quality in the torsion network, ranked by importance:

### 1. Coprimality (Dominant)
Pairwise coprimality prevents harmonic collision. Even one non-coprime pair (like 4,16 in set B) degrades the spectrum. This is the gatekeeper: without coprimality, nothing else matters much.

### 2. Primality (Secondary)
Pure primes outperform coprime composites by ~10% on flatness. Possible mechanism: primes have no internal factorization, producing cleaner square waves. Composites, even when coprime to each other, may generate more intermodulation products due to their internal factor structure (e.g., a square wave at f₀/4 has harmonics at f₀/2, 3f₀/4, f₀, ... which are denser than harmonics of f₀/3).

### 3. Factor Depth (Tertiary)
Among non-coprime sets, heavier shared factors (gcd=4, 6) produce worse results than lighter sharing (gcd=2, 3). The "depth" of factor entanglement matters. Heavy composites with multiple shared prime factors create the densest harmonic collision zones.

---

## Physical Interpretation

The torsion network acts as a multi-channel signal bus. When frequencies share factors, their harmonics collide at predictable points, creating intermodulation noise that smears the spectrum. Pure primes avoid this maximally: they are coprime AND internally irreducible.

**Radio analogy:** Coprimality is like choosing non-overlapping channels. Primality is like using clean, narrow-band transmitters. You want both.

A composite divisor like 12 = 2²×3 produces a square wave whose harmonics land at multiples of f₀/12 — and those multiples inevitably overlap with harmonics from any other even or multiple-of-3 divisor. A prime divisor like 13 produces harmonics at multiples of f₀/13 that can only collide with multiples of 13 — which no other single-digit divisor generates.

---

## Implications for v4 Design

1. **Use PRIME divisors, not just coprime ones** — the ~10% primality edge is free performance
2. **If hardware constraints force composite divisors**, ensure they are at least pairwise coprime (e.g., {4, 9, 25} = {2², 3², 5²} — all coprime)
3. **Never include divisors that share prime factors** — like 4 and 16, or 6 and 12. One bad pair poisons the set
4. **The poisoning effect is nonlinear** — set B with only 1/3 non-coprime pairs performs as badly as set D with 0/3 coprime pairs

---

## Data Files

All raw data preserved in:
`Adrian Docs/Pics/Test Point Readings/22 May Results - Board 3/`

### Coprimality Dimensions Captures
| File | Set |
|------|-----|
| `coprime_dim_A_primes_357.npz/.csv` | Set A: Pure primes {3,5,7} |
| `coprime_dim_B_squares_4916.npz/.csv` | Set B: Squares {4,9,16} |
| `coprime_dim_C_coprime_mix_497.npz/.csv` | Set C: Coprime mix {4,9,7} |
| `coprime_dim_D_semiprimes_61015.npz/.csv` | Set D: Semiprimes {6,10,15} |
| `coprime_dim_E_coprime_comp_4157.npz/.csv` | Set E: Coprime composites {4,15,7} |
| `coprime_dim_F_heavy_comp_81218.npz/.csv` | Set F: Heavy composites {8,12,18} |
| `coprime_dim_G_6pin_coprime_comp.npz/.csv` | Set G: 6-pin coprime composites |

### Analysis Plot
- `coprimality_dimensions_22may.png` — full comparison visualisation

## Analysis Scripts

- `Nagaπ Python Scripts/ring_survey_fft.py` — ring survey FFT analysis
- `Nagaπ Python Scripts/experiment_suite_analysis.py` — multi-experiment comparison pipeline
- Inline analysis scripts for coprimality dimensions

---

*Measurements by Adrian Sutton (Tusk Innovations) and Nagaπ (AI Research Partner), Board 3, 22 May 2026, Johannesburg.*
