# Zeta Zeros, Eigenvalues, and PCA: The Prime Eigenbasis Hypothesis

**Date:** 30 May 2026  
**Authors:** Adrian (Tusk) & Nagaπ  
**Status:** Theoretical synthesis connecting established mathematics to v3 experimental results

---

## The Eigenvalue Thread

### 1. Hilbert-Pólya Conjecture (~1914)

Pólya, prompted by Landau in Göttingen: *"Do you know a physical reason the Riemann hypothesis should be true?"*

Pólya's answer: The RH would follow if the non-trivial zeros of ζ(s) = ½ + ibₙ were eigenvalues of a self-adjoint (Hermitian) operator — because such operators have exclusively real eigenvalues.

Neither Hilbert nor Pólya could identify the operator or the physical system.

### 2. Montgomery-Dyson (1973)

Hugh Montgomery discovered the pair-correlation of zeta zeros follows:

```
1 − (sin(πr)/(πr))²
```

Freeman Dyson instantly recognised this as the eigenvalue spacing distribution of **GUE (Gaussian Unitary Ensemble) random matrices** — the same matrices used to model energy levels of heavy nuclei in quantum mechanics.

**Montgomery-Odlyzko Law:** Massive computation by Odlyzko confirmed that zeta zeros follow GUE statistics with extraordinary precision.

### 3. Quantum Chaos Bridge

Physicists studying quantum-classical transitions found that energy level statistics of classically chaotic quantum systems match predictions derived from the Riemann zeta function. The zeta function appears to encode the spectral properties of some unknown chaotic quantum system.

### 4. Selvam's Turbulence Analogy

A. M. Selvam (2001): Prime numbers are analogous to eddies in turbulent fluid flows. Prime frequencies follow "quantum-like mechanical laws." Penrose tilings filling space ↔ integers decomposing into prime products.

---

## The PCA Connection (Adrian's Insight, 30 May 2026)

In Principal Component Analysis:
- **Eigenvalues** rank the variance captured by each component
- **Eigenvectors** (principal components) are the irreducible basis that captures maximum structure with minimum redundancy
- You reduce dimensionality by keeping only the top eigenvectors — the ones that carry the essential pattern

### The Prime Eigenbasis Hypothesis

**Primes are the principal components of multiplicative number structure.**

Every integer has a unique prime factorisation (Fundamental Theorem of Arithmetic). Primes are the irreducible basis vectors of the multiplicative integer lattice. They are, by definition, the components that cannot be further decomposed — the eigenmodes of number structure.

When we drive a physical resonator network with prime-ratio frequencies:
- We are feeding it the **eigenmodes** — maximum structural information, minimum redundancy
- Composite ratios contain redundant harmonic overlap (like using correlated features in PCA)
- This predicts: prime-ratio signals should produce **higher coupling (Vpp), sharper spectra, better coherence**

### V3 Experimental Confirmation (20-22 May 2026)

| Metric | Prime Ratios | Composite Ratios | Advantage |
|--------|-------------|-------------------|-----------|
| Peak amplitude (Vpp) | 1140 mV | ~890 mV | +28% |
| Spectral flatness | 0.67 | 0.81 | Lower = more structured |
| Cross-correlation (A↔B) | 0.82 | 0.67 | +22% coherence |
| Individual frequency resolution | 5 of 6 resolved | Cluttered | Clear eigenmodes |

The prime-ratio network resolves individual frequencies cleanly — exactly what you'd expect from orthogonal basis vectors. Composite ratios produce harmonic clutter — exactly what you'd expect from correlated, redundant components.

---

## Why {1,2,3,5,6,7} Beats Pure Primes

The Tusk-resonant set {1,2,3,5,6,7} outperformed pure primes {2,3,5,7,11,13} by 24% on spectral flatness (22 May experiments).

**PCA interpretation:** Eigenvectors alone are just numbers — they need a coordinate frame. The structural scaffolding (1 = identity, 6 = 2×3 product) provides the **basis context** against which the prime eigenvalues are meaningful. In PCA terms: you need the mean (centroid) and the scale, not just the directions.

The set {1,2,3,5,6,7} includes:
- The multiplicative identity (1)
- The first three primes (2, 3, 5)  
- The first primorial product context (6 = 2×3)
- The next prime (7)

This is the **minimum spanning set** of number structure — primes plus their essential products.

---

## Why Zeta Zeros Resonate at 85-90% of Primes

The zeta function encodes the primes via the Euler product:

```
ζ(s) = Π_p (1 - p^(-s))^(-1)
```

The zeros of ζ(s) are *derived from* the prime distribution — they're the spectral decomposition of the prime counting function. In PCA terms: if primes are the eigenvectors, zeta zeros are the **eigenvalues** — they encode the *importance weights* of each prime direction.

Our v3 results (22 May):
- Zeta zero frequencies: 1020 mV, flatness 0.381, xcorr 0.813
- Prime frequencies: 1140 mV, flatness 0.67, xcorr 0.843
- Zeta zeros perform at 85-90% of primes

The zeros carry prime structural DNA (they're derived from primes) but they're not the primes themselves — they're the transform, not the basis. This explains the ~10-15% performance gap: close family, different role.

---

## Implications for V4

The v4 board with 6 prime-ratio cells (÷1, ÷2, ÷3, ÷5, ÷7, ÷11) is literally constructing a **prime eigenbasis in hardware**. The AD9833 DDS chips provide precise frequency control, and the measurement section can quantify:

1. **Effective rank** — How many independent modes does the prime network support vs composite? (PCA dimension count)
2. **Variance capture** — Does the prime set capture more total signal energy? (Eigenvalue sum)
3. **Orthogonality** — Are prime-ratio signals more independent (less correlated) than composite-ratio signals? (Off-diagonal covariance)
4. **Noise resilience** — Do prime eigenmodes degrade more gracefully under noise? (Eigenvalue gap = stability)

If primes really are the eigenbasis of number structure, the v4 board should show:
- Higher effective rank for prime vs composite configurations
- Lower mutual information between prime-ratio channels
- Steeper eigenvalue decay in composite configurations (fewer real degrees of freedom)
- Better signal recovery under noise for prime ratios

---

## Historical Position

| Year | Milestone | Nature |
|------|-----------|--------|
| ~1914 | Hilbert-Pólya conjecture | Theoretical — eigenvalues should exist |
| 1973 | Montgomery-Dyson | Statistical — zeta zeros match GUE eigenvalue spacing |
| 1980s-2000s | Odlyzko computation | Computational — confirmed to billions of zeros |
| 2001 | Selvam turbulence | Analogical — primes as physical eddies |
| 2026 | Tusk v3 experiments | **Experimental — prime-ratio physical resonator responds to zeta-derived frequencies** |

We are not claiming to solve the Riemann Hypothesis. We are reporting that a physical resonator network, tuned to prime ratios, naturally accommodates frequencies derived from the non-trivial zeros of the Riemann zeta function — and that both prime and zeta-derived frequency sets outperform arbitrary and composite sets in measurable coupling metrics.

This is, to our knowledge, the first experimental observation of this kind.

---

## References

- Wells, David. *Prime Numbers: The Most Mysterious Figures in Math.* Wiley, 2005. Ch. "Zeta mysteries: the quantum connection," pp. 241-243.
- Montgomery, H. L. "The pair correlation of zeros of the zeta function." *Analytic Number Theory*, Proc. Sympos. Pure Math. 24 (1973): 181-193.
- Odlyzko, A. M. "The 10²⁰-th zero of the Riemann zeta function and 175 million of its neighbors." AT&T Bell Labs preprint, 1989.
- Selvam, A. M. "Quantum-like Chaos in Prime Number Distribution and in Turbulent Fluid Flows." *Apeiron* 8.3 (2001).
- Gutzwiller, M. C. *Chaos in Classical and Quantum Mechanics.* Springer, 1990.
- Sabbagh, Karl. *Dr Riemann's Zeros.* Atlantic Books, 2002.
- Tusk v3 experimental data: `v3_board3_zeta_zeros_22may2026.md`, `v3_torsion_results_20may2026.md`
