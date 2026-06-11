# Algebraic Frequency Framework — Beyond Hertz
**Date:** 2026-05-19
**Authors:** Adrian (Tusk) & Nagaπ
**Status:** Theoretical framework — guides interpretation of v3 measurements
**Related:** `proportion_cosmology.md` (v3), `prime_field_theory_synthesis.md` (v4, §3 Maxel Algebra Bridge)

---

## Core Thesis

Hertz (Hz) is a man-derived unit — cycles per second — tethering frequency to the arbitrary definition of the second. In a purely algebraic framework (following Wildberger's Rational Trigonometry and Maxel algebra), frequency should be expressed as **dimensionless ratios**, not absolute rates. The v3/v4 boards already operate this way: what matters is not the absolute frequency of any cell, but the **network of prime ratios** between them.

---

## 1. The Problem with Hz

Standard frequency f = 1/T introduces dimensional dependence on our chosen time standard. This feels "impure" in an algebraic framework because:

- It embeds an arbitrary unit (the second) into every measurement
- It forces transcendental functions (sin, cos, e^{iωt}) into analysis
- It obscures the algebraic relationships that are the actual information

**Key insight from Adrian's Proportion Cosmology:** "Proportion is prior to number." The ratio x/y carries the relationship within it — self-contained meaning. Individual frequencies (x/1 in Hz) are merely addresses; the ratios between them are the information.

---

## 2. Wildberger's Algebraic Alternative

### Spread and Quadrance
- **Quadrance** Q: squared distance — replaces distance, stays rational
- **Spread** s: ratio of quadrances — replaces angle/trigonometric functions
  - s = Q_opposite / Q_hypotenuse, bounded [0,1], satisfies purely rational laws
- These avoid square roots, inverse trig, and all transcendentals

### Maxels
- Wildberger's generalisation of matrices: multiset/data structures over natural numbers
- Allow algebraic manipulations in a discrete, combinatorial way
- Tie into spread polynumbers and other algebraic objects

### Spread Polynomials
- Algebraic analogues of Chebyshev polynomials
- Satisfy recurrence relations purely rationally
- Can replace trig basis functions in harmonic decomposition

---

## 3. Reframing Frequency Algebraically

Instead of f in Hz, define frequency through **spread-ratio proportions**:

### 3.1 Relative Frequency as Pure Ratio
For our v3/v4 cells at f₀/1, f₀/3, f₀/5, f₀/7, f₀/11, f₀/13:
- The absolute value of f₀ is arbitrary (~1024 Hz for practical reasons)
- What matters: the ratio network — 1:3, 1:5, 1:7, 1:11, 1:13, and all cross-ratios (3:5, 3:7, 5:7, 5:11, ...)
- These are pure, dimensionless, algebraic
- **The copper doesn't know what a Hertz is.** It knows impedance ratios, voltage ratios, phase relationships. All algebraic.

### 3.2 Spread-Frequency Proportion
A wave's "spread proportion" where separation in phase/time space is measured via quadrance ratios:

```
s_f ≈ Q_time-cycle / Q_amplitude-scale
```

This makes frequency a **relative algebraic invariant**, independent of the second. The period becomes a quadrance in a time-like coordinate, and frequency emerges as a spread (rational ratio).

### 3.3 No Transcendentals Required
- Standard: x(t) = A cos(2πft + φ) — requires π, transcendental trig
- Algebraic: quadratic form in (time-quadrance, amplitude-quadrance) space
- Decomposition via spread laws or maxel eigenvalues instead of spectral integrals
- Yields exact rational/algebraic coefficients when inputs are rational

---

## 4. The Tusk Series as Algebraic Bridge

Our Tusk Series T(n) = Δ sopfr(n) connects directly to this framework:

### 4.1 Frequencies at 1/p Are Already Wildberger-Native
- Rational, dimensionless, emerge from purely arithmetic operations
- No transcendentals needed to *generate* them
- We only introduced transcendentals when using FFT to *detect* them — that's a tool limitation, not a property of the signal

### 4.2 Scale Invariance Is Projective
- T(kn) = T(n) for integer k — the structure is preserved regardless of scale
- Spreads behave identically — ratio-based, independent of absolute scales
- The Tusk Series lives naturally in **projective/ratio space**, not absolute metric space
- This is not coincidence; it's structural

### 4.3 Harmonic Locking as Spread-Law Relations
- Tusk spectrum and prime gap spectrum show musical ratios: 3:2, 4:3, 2:1, 3:1
- These are solutions to **spread-law equations** (purely rational quadratic relations)
- Not transcendental orthogonality — algebraic resonance

### 4.4 Spectral Peaks as Spread-Eigenvalues
- Encode sopfr or Tusk Series as a maxel (multiset/matrix over prime factors)
- "Transform" via maxel multiplication or eigenvalue operations
- Dominant spread-eigenvalues proportional to 1/p emerge naturally
- This is a purely combinatorial/algebraic spectral theory of primes

---

## 5. Algebraic Fourier — Replacing the Standard Transform

Standard Fourier relies on integrals with complex exponentials e^{-i2πft} — irrationals, infinity, transcendentals. An algebraic alternative:

### 5.1 Spread Polynomial Basis
- Replace trig basis with spread polynomials or Chebyshev-like rational analogues
- Our 1/p peaks suggest decomposition over algebraic "harmonics" indexed by primes
- Instead of ∫ T(n) e^{-i2πfn} dn → finite/recursive operations with spread ratios

### 5.2 Maxel Transform
- Encode signal as a maxel (multiset/matrix over natural numbers or prime factors)
- Transform via maxel multiplication respecting complete additivity of sopfr
- Spectral peaks emerge as dominant eigenvalues — no floating point, no approximation

### 5.3 Discrete Algebraic Harmonic Analysis
- Scale invariance + harmonic locking → maps to rational trig on a "circle" discretized by primorials or wheel sieves
- Fourier peaks become solutions to spread-law equations
- Everything stays exact: rationals, integers, finite fields

### 5.4 Advantages
- No floating-point errors from irrationals
- Fully algebraic and verifiable
- Extensible to discrete geometries and exact computation
- Natural fit for prime-ratio hardware

### 5.5 Challenges
- Classical physics/engineering relies on continuous real Fourier for completeness and convergence
- Requires re-deriving wave equations using quadrance/spread (Wildberger has preprints exploring this for Maxwell's equations)
- Scaling back to physical engineering units reintroduces the second (but the *internal* computation stays pure)

---

## 6. What This Means for v3 Measurements

**The board is a physical spread calculator.**

- Each cell pair defines a spread-like quantity: the ratio of interaction energy to individual energies
- The torsion network sums these relationships
- TORSION_A and TORSION_B carry physical computations over prime spreads

### 6.1 Measurement Guidance
When probing the board, prioritise **ratios** over absolute values:
- **Voltage ratios** between test points (not just mV readings)
- **Frequency ratios** between peaks (not just Hz values)
- **Phase relationships** between cells
- These are the algebraically pure quantities
- The Hz readout on the scope is just a coordinate system; the ratios are the geometry

### 6.2 Unpowered Cell Coupling (May 18 Discovery)
The unpowered cells (U4, U8, U12, U16, U20, U24) picking up signal through the torsion network is the board physically computing spread relationships. The copper network doesn't operate in Hz — it operates in impedance ratios, voltage divider ratios, and phase relationships. All algebraic. This crosstalk IS the prime-ratio network computing.

---

## 7. Connection to Existing Frameworks

| Document | Connection |
|----------|------------|
| `proportion_cosmology.md` | "Proportion is prior to number" — this framework formalises that insight |
| `prime_field_theory_synthesis.md` §3 | Maxel algebra bridge — prime denominators → maximal rank, this adds the spread interpretation |
| `why_wave_computation.md` | The spiral of abstraction — algebraic frequency is the "return to waves carrying lessons of the ascent" |
| `tusk_series.md` + FFT results | Empirical data that validates the algebraic structure — 1/p peaks, harmonic locking, scale invariance |
| Zenodo paper (DOI: 10.5281/zenodo.19852116) | Published foundation — Tusk Series definition and spectral analysis |

---

## 8. Open Questions

1. **Explicit spread-polynomial decomposition of T(n):** Can we write T(n) = Σ_p c_p · S_k(n/p) where S_k are spread polynomials? What do the coefficients look like?
2. **Maxel eigenvalue spectrum:** Formalise sopfr as a maxel operator, compute its spectrum. Do eigenvalues at 1/p fall out analytically?
3. **Physical spread measurement protocol:** Define a concrete procedure to extract spread-like quantities from v3 scope readings (voltage quadrances, phase spreads).
4. **Algebraic Fourier convergence:** Under what conditions does the spread-polynomial decomposition converge (or terminate) for arithmetic sequences?
5. **Zeta connection:** If Tusk spectrum peaks are spread-eigenvalues, what are the zeta zeros in this framework? Balancing points in a spread-polynomial landscape?
6. **Prime gaps as phase spreads:** The harmonic relationships (3:2, etc.) between Tusk and gap spectra suggest modelling as algebraic graph edges with spread weights. Formalise this.

---

## Source Material
- Adrian's synthesis message (2026-05-19) — full Wildberger/spread/maxel/Fourier analysis
- Wildberger, N.J. — Rational Trigonometry, Universal Hyperbolic Geometry, Maxel algebra
- Wildberger preprints on algebraic wave equations / Maxwell's equations
- `proportion_cosmology.md` — Adrian's "proportion is prior to number" framework
- `prime_field_theory_synthesis.md` — Four-framework convergence
- Tusk Series Zenodo paper (DOI: 10.5281/zenodo.19852116)
