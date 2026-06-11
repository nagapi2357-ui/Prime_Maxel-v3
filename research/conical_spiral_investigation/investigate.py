#!/usr/bin/env python3
"""Conical/helical spiral investigation: does π − Φ² ≈ 0.5236 appear in 3D prime structures?"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sympy import primerange, fibonacci
from scipy.spatial import KDTree
from collections import Counter
import os, json

OUT = "/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/research/conical_spiral_investigation"
PHI = (1 + np.sqrt(5)) / 2
CUBIT = np.pi - PHI**2  # ≈ 0.52359877...
GOLDEN_ANGLE = 2*np.pi*(1 - 1/PHI)  # ≈ 2.39996... rad ≈ 137.5077°

print(f"Constants: π={np.pi:.10f}, Φ={PHI:.10f}, Φ²={PHI**2:.10f}, cubit={CUBIT:.10f}")
print(f"Golden angle = {np.degrees(GOLDEN_ANGLE):.4f}°")
print(f"cubit in degrees = {np.degrees(CUBIT):.4f}°")
print(f"π/6 = {np.pi/6:.10f} (should match cubit)")

# Generate primes
primes = np.array(list(primerange(2, 1_000_003)))
N = len(primes)
print(f"\n{N} primes loaded (up to {primes[-1]})")

results = {}

# ============================================================
# 1. CONICAL GOLDEN SPIRAL WITH PRIMES
# ============================================================
print("\n" + "="*60)
print("1. CONICAL GOLDEN SPIRAL — 3D angles between consecutive points")

for label, rfunc, zfunc in [
    ("sqrt_linear", lambda p: np.sqrt(p), lambda p: p),
    ("cbrt_log", lambda p: p**(1/3), lambda p: np.log(p)),
]:
    theta = np.arange(N) * GOLDEN_ANGLE
    r = rfunc(primes)
    z = zfunc(primes)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    # 3D vectors between consecutive points
    dx = np.diff(x); dy = np.diff(y); dz = np.diff(z)
    vecs = np.column_stack([dx, dy, dz])
    norms = np.linalg.norm(vecs, axis=1)
    
    # Angles between consecutive displacement vectors
    dots = np.sum(vecs[:-1] * vecs[1:], axis=1)
    n1 = norms[:-1]; n2 = norms[1:]
    cos_angles = np.clip(dots / (n1 * n2), -1, 1)
    angles = np.arccos(cos_angles)
    
    mean_a = np.mean(angles)
    median_a = np.median(angles)
    std_a = np.std(angles)
    
    # Check how many angles are near cubit
    near_cubit = np.sum(np.abs(angles - CUBIT) < 0.01)
    near_pi6 = np.sum(np.abs(angles - np.pi/6) < 0.01)
    
    print(f"\n  [{label}] mean={mean_a:.6f}, median={median_a:.6f}, std={std_a:.6f}")
    print(f"  Angles within 0.01 of cubit: {near_cubit}/{len(angles)} ({100*near_cubit/len(angles):.2f}%)")
    print(f"  cubit/mean = {CUBIT/mean_a:.6f}, mean/cubit = {mean_a/CUBIT:.6f}")
    
    # Histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    counts, bins, _ = ax.hist(angles, bins=200, density=True, alpha=0.7, color='steelblue')
    ax.axvline(CUBIT, color='red', lw=2, label=f'cubit = {CUBIT:.4f} rad')
    ax.axvline(mean_a, color='orange', lw=2, ls='--', label=f'mean = {mean_a:.4f}')
    ax.axvline(np.pi/6, color='green', lw=1, ls=':', label=f'π/6 = {np.pi/6:.4f}')
    ax.set_xlabel('Angle (radians)'); ax.set_ylabel('Density')
    ax.set_title(f'3D Consecutive Angles — Conical Golden Spiral ({label})')
    ax.legend(); plt.tight_layout()
    fig.savefig(f"{OUT}/1_angles_{label}.png", dpi=150)
    plt.close()
    
    results[f"1_{label}"] = {"mean": float(mean_a), "median": float(median_a), 
                              "std": float(std_a), "near_cubit_pct": float(100*near_cubit/len(angles))}

# 3D plot of first 2000 primes on cone
theta_plot = np.arange(2000) * GOLDEN_ANGLE
r_plot = np.sqrt(primes[:2000])
z_plot = primes[:2000].astype(float)
x_plot = r_plot * np.cos(theta_plot)
y_plot = r_plot * np.sin(theta_plot)

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(x_plot, y_plot, z_plot, c=z_plot, cmap='viridis', s=1, alpha=0.6)
ax.set_title('Primes on Conical Golden Spiral (first 2000)')
ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z = p(n)')
plt.colorbar(sc, shrink=0.5, label='Prime value')
fig.savefig(f"{OUT}/1_cone_3d.png", dpi=150)
plt.close()

# ============================================================
# 2. HELICAL PRIME MAPPING — test α values
# ============================================================
print("\n" + "="*60)
print("2. HELICAL PRIME MAPPING — testing α values")

alphas = np.linspace(0.1, 3.0, 300)
# For each α, measure collinearity / alignment quality
# Use first 10000 primes for speed
p_hel = primes[:10000].astype(float)

def alignment_score(alpha, ps):
    """Lower = more aligned. Measure variance of nearest-neighbor distances."""
    x = np.cos(ps * alpha)
    y = np.sin(ps * alpha)
    z = ps / ps.max()  # normalize
    pts = np.column_stack([x, y, z])
    tree = KDTree(pts)
    dd, _ = tree.query(pts, k=2)
    nn_dist = dd[:, 1]
    return np.std(nn_dist) / np.mean(nn_dist)  # CV of NN distances

scores = []
for a in alphas:
    scores.append(alignment_score(a, p_hel))
scores = np.array(scores)

# Find minima (most regular structure)
from scipy.signal import argrelmin
minima_idx = argrelmin(scores, order=5)[0]
minima_alphas = alphas[minima_idx]
minima_scores = scores[minima_idx]

# Sort by score
order = np.argsort(minima_scores)
top_minima = minima_alphas[order[:20]]

print(f"  Top alignment minima (α values): {top_minima[:10].round(4)}")
print(f"  Score at α=cubit({CUBIT:.4f}): {alignment_score(CUBIT, p_hel):.6f}")
print(f"  Score at α=golden_angle({GOLDEN_ANGLE:.4f}): {alignment_score(GOLDEN_ANGLE, p_hel):.6f}")

# Check cubit neighbors
cubit_idx = np.argmin(np.abs(alphas - CUBIT))
cubit_score = scores[cubit_idx]
cubit_rank = np.sum(scores < cubit_score)
print(f"  Cubit score rank: {cubit_rank}/{len(scores)} (lower=better alignment)")

# Is cubit near a minimum?
nearest_min = top_minima[np.argmin(np.abs(top_minima - CUBIT))]
print(f"  Nearest minimum to cubit: α={nearest_min:.4f} (diff={abs(nearest_min-CUBIT):.4f})")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(alphas, scores, 'b-', lw=0.8)
ax.axvline(CUBIT, color='red', lw=2, label=f'cubit={CUBIT:.4f}')
ax.axvline(GOLDEN_ANGLE, color='green', lw=1.5, ls='--', label=f'golden angle={GOLDEN_ANGLE:.4f}')
for m in top_minima[:5]:
    ax.axvline(m, color='orange', lw=1, ls=':', alpha=0.7)
ax.set_xlabel('α'); ax.set_ylabel('Alignment score (CV of NN distances)')
ax.set_title('Helical Prime Mapping — Alignment vs α')
ax.legend(); plt.tight_layout()
fig.savefig(f"{OUT}/2_helix_alpha_scan.png", dpi=150)
plt.close()

# 3D plot at α = cubit
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')
ps_plot = primes[:3000].astype(float)
xh = np.cos(ps_plot * CUBIT)
yh = np.sin(ps_plot * CUBIT)
zh = ps_plot
sc = ax.scatter(xh, yh, zh, c=zh, cmap='plasma', s=1, alpha=0.5)
ax.set_title(f'Primes on Helix (α = cubit ≈ {CUBIT:.4f})')
ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z = p(n)')
fig.savefig(f"{OUT}/2_helix_cubit_3d.png", dpi=150)
plt.close()

results["2_helix"] = {
    "cubit_score": float(alignment_score(CUBIT, p_hel)),
    "cubit_rank": int(cubit_rank),
    "total_alphas": len(alphas),
    "top_minima": top_minima[:10].tolist(),
    "nearest_min_to_cubit": float(nearest_min),
}

# ============================================================
# 3. NEAREST-NEIGHBOR DISTANCES on conical spiral
# ============================================================
print("\n" + "="*60)
print("3. NEAREST-NEIGHBOR DISTANCES on conical spiral")

# Use sqrt/linear mapping, first 50000 primes
p3 = primes[:50000].astype(float)
theta3 = np.arange(len(p3)) * GOLDEN_ANGLE
r3 = np.sqrt(p3)
z3 = p3
x3 = r3 * np.cos(theta3)
y3 = r3 * np.sin(theta3)

pts3 = np.column_stack([x3, y3, z3])
tree3 = KDTree(pts3)
dd3, _ = tree3.query(pts3, k=2)
nn3 = dd3[:, 1]

mean_nn = np.mean(nn3)
median_nn = np.median(nn3)
print(f"  NN distances: mean={mean_nn:.4f}, median={median_nn:.4f}, std={np.std(nn3):.4f}")
print(f"  cubit / mean_nn = {CUBIT/mean_nn:.6f}")
print(f"  mean_nn / cubit = {mean_nn/CUBIT:.6f}")

# Normalized NN distances
nn_norm = nn3 / mean_nn
# Check if cubit appears as a ratio
print(f"  Fraction of NN distances within 5% of cubit: {np.mean(np.abs(nn3 - CUBIT)/CUBIT < 0.05)*100:.2f}%")

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(nn3, bins=300, density=True, alpha=0.7, color='steelblue')
ax.axvline(CUBIT, color='red', lw=2, label=f'cubit={CUBIT:.4f}')
ax.axvline(mean_nn, color='orange', lw=2, ls='--', label=f'mean={mean_nn:.4f}')
ax.set_xlabel('NN Distance'); ax.set_ylabel('Density')
ax.set_title('Nearest-Neighbor Distances on Conical Golden Spiral')
ax.legend(); ax.set_xlim(0, np.percentile(nn3, 99)); plt.tight_layout()
fig.savefig(f"{OUT}/3_nn_distances.png", dpi=150)
plt.close()

# Also log-scaled version
fig, ax = plt.subplots(figsize=(10, 6))
log_nn = np.log(nn3)
ax.hist(log_nn, bins=200, density=True, alpha=0.7, color='teal')
ax.axvline(np.log(CUBIT), color='red', lw=2, label=f'ln(cubit)={np.log(CUBIT):.4f}')
ax.set_xlabel('ln(NN Distance)'); ax.set_ylabel('Density')
ax.set_title('Log Nearest-Neighbor Distances'); ax.legend(); plt.tight_layout()
fig.savefig(f"{OUT}/3_nn_log.png", dpi=150)
plt.close()

results["3_nn"] = {"mean": float(mean_nn), "median": float(median_nn), 
                    "cubit_over_mean": float(CUBIT/mean_nn)}

# ============================================================
# 4. PROJECTION ALIGNMENTS
# ============================================================
print("\n" + "="*60)
print("4. PROJECTION ALIGNMENTS")

p4 = primes[:5000].astype(float)
theta4 = np.arange(len(p4)) * GOLDEN_ANGLE
r4 = np.sqrt(p4)
z4 = p4
x4 = r4 * np.cos(theta4)
y4 = r4 * np.sin(theta4)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for ax, (a, b, la, lb) in zip(axes, [(x4,y4,'x','y'), (x4,z4,'x','z'), (y4,z4,'y','z')]):
    ax.scatter(a, b, s=0.3, alpha=0.4, c='navy')
    ax.set_xlabel(la); ax.set_ylabel(lb)
    ax.set_title(f'{la}-{lb} projection')
    ax.set_aspect('auto')
plt.suptitle('2D Projections of Conical Golden Spiral (5000 primes)')
plt.tight_layout(); fig.savefig(f"{OUT}/4_projections.png", dpi=150); plt.close()

# Also log-z version
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
z4log = np.log(p4)
x4l = np.sqrt(p4) * np.cos(theta4)
y4l = np.sqrt(p4) * np.sin(theta4)
for ax, (a, b, la, lb) in zip(axes, [(x4l,y4l,'x','y'), (x4l,z4log,'x','ln(z)'), (y4l,z4log,'y','ln(z)')]):
    ax.scatter(a, b, s=0.3, alpha=0.4, c='darkred')
    ax.set_xlabel(la); ax.set_ylabel(lb)
    ax.set_title(f'{la}-{lb} projection (log z)')
plt.suptitle('2D Projections — log z scaling')
plt.tight_layout(); fig.savefig(f"{OUT}/4_projections_logz.png", dpi=150); plt.close()
print("  Projections saved.")

# ============================================================
# 5. CONE OPENING ANGLE
# ============================================================
print("\n" + "="*60)
print("5. CONE OPENING ANGLE")

# For primes on cone: r = sqrt(p), z = p → half-angle = arctan(r/z) = arctan(1/sqrt(p))
# This varies per point. For "bulk" angle: fit a cone.
# r vs z relationship: r = sqrt(z) → r/z = 1/sqrt(z) → angle decreases
# Better: the cone envelope. r = sqrt(z), so dr/dz = 1/(2*sqrt(z))
# At a given z, half-angle = arctan(r/z) = arctan(1/sqrt(z))

# Statistical approach: for each prime, compute arctan(r/z)
p5 = primes[:50000].astype(float)
half_angles = np.arctan(np.sqrt(p5) / p5)  # = arctan(1/sqrt(p))

# This just gives arctan(1/sqrt(p)) which is smooth, not very interesting
# Better: look at the angle of the line from origin to each point in (r, z) space
# The "cone" is not a true cone since r = sqrt(z), it's a paraboloid

# More interesting: what angle α makes a ray from origin pass through the most primes (within tolerance)?
# Ray: r = z * tan(α) → sqrt(p) ≈ p * tan(α) → tan(α) ≈ 1/sqrt(p)
# Each prime defines its own angle. Let's histogram these.

angles5 = np.arctan2(np.sqrt(p5), p5)  # half-angle for each prime
# These will all be small and decreasing. Not a fixed cone.

# Alternative: in full 3D, compute angle from z-axis to each point
# angle = arctan(r/z) same thing.

# Let's try: what fixed cone angle captures the most primes in angular *bins*?
# Actually the structure is a paraboloid, not a cone. Let's note that.

# More interesting: angular density on the cone surface
# In (theta, phi) spherical coords where phi = polar angle from z-axis
phi5 = np.arctan2(np.sqrt(p5), p5)
print(f"  Polar angles range: {np.degrees(phi5.min()):.4f}° to {np.degrees(phi5.max()):.4f}°")
print(f"  arctan(cubit) = {np.degrees(np.arctan(CUBIT)):.4f}°")
print(f"  The structure is a paraboloid (r=√z), not a true cone.")

# Check: at what prime value does the polar angle equal arctan(cubit)?
# arctan(1/√p) = arctan(0.5236) → 1/√p = 0.5236 → p = 1/0.5236² ≈ 3.647
# So only near p=3 (trivially small). Note this.
p_at_cubit = 1.0 / CUBIT**2
print(f"  Polar angle = arctan(cubit) at p ≈ {p_at_cubit:.2f}")

results["5_cone"] = {
    "note": "Structure is paraboloid r=sqrt(z), not fixed cone",
    "polar_angle_range_deg": [float(np.degrees(phi5.min())), float(np.degrees(phi5.max()))],
    "arctan_cubit_deg": float(np.degrees(np.arctan(CUBIT))),
    "p_at_cubit_angle": float(p_at_cubit),
}

# ============================================================
# 6. FIBONACCI SPIRAL ON CONE — deviations from primes
# ============================================================
print("\n" + "="*60)
print("6. FIBONACCI vs PRIME positions on cone — deviations")

# Generate Fibonacci numbers up to max prime
fibs = []
a, b = 1, 1
while b <= primes[-1]:
    fibs.append(b)
    a, b = b, a+b
fibs = np.array(fibs, dtype=float)
print(f"  {len(fibs)} Fibonacci numbers up to {int(fibs[-1])}")

# For each Fibonacci number, find nearest prime
fib_nearest_prime = []
for f in fibs:
    idx = np.searchsorted(primes, f)
    candidates = []
    if idx < len(primes): candidates.append(primes[idx])
    if idx > 0: candidates.append(primes[idx-1])
    nearest = min(candidates, key=lambda p: abs(p - f))
    fib_nearest_prime.append(nearest)
fib_nearest_prime = np.array(fib_nearest_prime, dtype=float)

deviations = fibs - fib_nearest_prime
rel_deviations = deviations / fibs

print(f"  Mean deviation: {np.mean(np.abs(deviations)):.2f}")
print(f"  Mean relative deviation: {np.mean(np.abs(rel_deviations)):.6f}")

# On cone: 3D distance between Fibonacci point and nearest prime point
n_fib = np.arange(len(fibs))
theta_fib = n_fib * GOLDEN_ANGLE
r_fib = np.sqrt(fibs)
x_fib = r_fib * np.cos(theta_fib)
y_fib = r_fib * np.sin(theta_fib)
z_fib = fibs

# For nearest primes, we need their index in prime list to get their cone position
prime_indices = np.searchsorted(primes, fib_nearest_prime)
theta_pnear = prime_indices * GOLDEN_ANGLE
r_pnear = np.sqrt(fib_nearest_prime)
x_pnear = r_pnear * np.cos(theta_pnear)
y_pnear = r_pnear * np.sin(theta_pnear)
z_pnear = fib_nearest_prime

dist_3d = np.sqrt((x_fib - x_pnear)**2 + (y_fib - y_pnear)**2 + (z_fib - z_pnear)**2)

# Normalize by Fibonacci value
dist_norm = dist_3d / fibs

print(f"  3D distances (Fib→nearest prime on cone): mean={np.mean(dist_3d):.2f}")
print(f"  Normalized: mean={np.mean(dist_norm):.6f}")
print(f"  Any normalized distance ≈ cubit? Closest: {dist_norm[np.argmin(np.abs(dist_norm - CUBIT))]:.6f}")

# Check ratios
for i in range(min(30, len(fibs))):
    if dist_3d[i] > 0:
        ratio = dist_3d[i] / CUBIT
        if abs(ratio - round(ratio)) < 0.05 and round(ratio) > 0:
            print(f"    Fib={int(fibs[i])}: 3D dist={dist_3d[i]:.4f}, dist/cubit={ratio:.4f} ≈ {round(ratio)}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
ax1.scatter(fibs[fibs<1e5], deviations[fibs<1e5], s=10, alpha=0.7)
ax1.axhline(0, color='gray', ls='--')
ax1.set_xlabel('Fibonacci number'); ax1.set_ylabel('Deviation (Fib - nearest prime)')
ax1.set_title('Fibonacci-Prime Deviations')
ax2.scatter(np.arange(len(dist_norm)), dist_norm, s=10, alpha=0.7, c='darkred')
ax2.axhline(CUBIT, color='red', lw=2, label=f'cubit={CUBIT:.4f}')
ax2.set_xlabel('Fibonacci index'); ax2.set_ylabel('Normalized 3D distance')
ax2.set_title('Normalized 3D Distance (Fib→Prime on Cone)')
ax2.legend(); plt.tight_layout()
fig.savefig(f"{OUT}/6_fib_deviations.png", dpi=150); plt.close()

results["6_fibonacci"] = {
    "mean_deviation": float(np.mean(np.abs(deviations))),
    "mean_rel_deviation": float(np.mean(np.abs(rel_deviations))),
    "mean_3d_distance": float(np.mean(dist_3d)),
}

# ============================================================
# 7. VOLUME SHELLS
# ============================================================
print("\n" + "="*60)
print("7. VOLUME SHELLS — spherical shell prime counts")

p7 = primes[:50000].astype(float)
theta7 = np.arange(len(p7)) * GOLDEN_ANGLE
r7 = np.sqrt(p7)
x7 = r7 * np.cos(theta7)
y7 = r7 * np.sin(theta7)
z7 = p7

# Radial distance from origin in 3D
R7 = np.sqrt(x7**2 + y7**2 + z7**2)  # ≈ sqrt(p + p²) for large p, ≈ p

# Shell widths
n_shells = 200
shell_edges = np.linspace(0, np.max(R7), n_shells + 1)
shell_counts, _ = np.histogram(R7, bins=shell_edges)
shell_centers = 0.5 * (shell_edges[:-1] + shell_edges[1:])
shell_width = shell_edges[1] - shell_edges[0]

# Density: counts / shell volume (4π r² dr)
shell_volumes = 4 * np.pi * shell_centers**2 * shell_width
shell_density = shell_counts / np.where(shell_volumes > 0, shell_volumes, 1)

# Normalize
shell_density_norm = shell_density / np.max(shell_density)

# FFT of shell counts to look for periodicity
from numpy.fft import fft, fftfreq
ft = np.abs(fft(shell_counts - np.mean(shell_counts)))
freqs = fftfreq(len(shell_counts), d=shell_width)
pos = freqs > 0
peak_freq = freqs[pos][np.argmax(ft[pos])]
peak_period = 1.0 / peak_freq if peak_freq > 0 else np.inf

print(f"  Shell width: {shell_width:.2f}")
print(f"  Dominant period in shell counts: {peak_period:.4f}")
print(f"  period / cubit = {peak_period / CUBIT:.4f}")
print(f"  cubit / period = {CUBIT / peak_period:.6f}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
ax1.bar(shell_centers, shell_counts, width=shell_width*0.9, color='steelblue', alpha=0.7)
ax1.set_xlabel('Radial distance from origin'); ax1.set_ylabel('Prime count')
ax1.set_title('Primes per Spherical Shell')
ax2.plot(1.0/freqs[pos][:50], ft[pos][:50], 'b-o', ms=3)
ax2.axvline(CUBIT, color='red', lw=2, label=f'cubit={CUBIT:.4f}')
ax2.set_xlabel('Period'); ax2.set_ylabel('FFT amplitude')
ax2.set_title('FFT of Shell Counts'); ax2.legend()
plt.tight_layout(); fig.savefig(f"{OUT}/7_volume_shells.png", dpi=150); plt.close()

results["7_shells"] = {"shell_width": float(shell_width), "dominant_period": float(peak_period),
                        "period_over_cubit": float(peak_period/CUBIT)}

# ============================================================
# BONUS: Comprehensive ratio scan
# ============================================================
print("\n" + "="*60)
print("BONUS: Scanning for cubit in various derived quantities")

# Collect all computed scalars and check ratios with cubit
quantities = {
    "1_sqrt_mean_angle": results["1_sqrt_linear"]["mean"],
    "1_sqrt_median_angle": results["1_sqrt_linear"]["median"],
    "1_cbrt_mean_angle": results["1_cbrt_log"]["mean"],
    "3_nn_mean": results["3_nn"]["mean"],
    "3_nn_median": float(median_nn),
    "7_dominant_period": results["7_shells"]["dominant_period"],
}

for name, val in quantities.items():
    ratio = val / CUBIT
    inv = CUBIT / val
    # Check if ratio is near a simple fraction
    for num in range(1, 13):
        for den in range(1, 13):
            frac = num / den
            if abs(ratio - frac) < 0.02:
                print(f"  {name} = {val:.6f}, val/cubit ≈ {num}/{den} = {frac:.4f} (actual {ratio:.4f})")

# ============================================================
# Save results
# ============================================================
with open(f"{OUT}/results.json", 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nAll results saved to {OUT}/")
print("Done!")
