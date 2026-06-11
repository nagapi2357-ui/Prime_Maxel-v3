#!/usr/bin/env python3
"""
Ring Survey FFT Analysis — 22 May 2026 (5ms/div, 60ms window)
Runs FFT on all 12 cells, detects prime frequency peaks, generates heatmap.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import os, glob

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'Adrian Docs', 'Pics', 'Test Point Readings', '22 May Results - Board 3')

# Expected prime frequencies
PRIME_FREQS = {'f₀/1': 1024, 'f₀/3': 341, 'f₀/5': 205, 'f₀/7': 146, 'f₀/11': 93, 'f₀/13': 79}

# Cell order around the ring
CELLS = ['U2','U4','U6','U8','U10','U12','U14','U16','U18','U20','U22','U24']
DRIVEN = {'U2': 'f₀/1', 'U4': 'f₀/3', 'U6': 'f₀/5', 'U8': 'f₀/7', 'U10': 'f₀/11', 'U12': 'f₀/13'}

def find_file(cell):
    """Find the best capture file for a cell (prefer r2 for U10)."""
    pattern = os.path.join(DATA_DIR, f'torsion_{cell}_TP1_TP2*.npz')
    files = sorted(glob.glob(pattern))
    if not files:
        return None
    # For U10, prefer r2 (first capture had dead CH2)
    if cell == 'U10':
        r2 = [f for f in files if '_r2_' in f]
        if r2:
            return r2[0]
    # Otherwise use first (primary) capture
    return files[0]

def fft_peaks(voltage, sr, fmax=1200, n_top=10, threshold=0.05):
    """Compute FFT and return top peaks."""
    v_ac = voltage - voltage.mean()
    N = len(v_ac)
    # Apply Hann window
    window = np.hanning(N)
    v_win = v_ac * window
    
    Y = np.abs(fft(v_win))[:N//2] * 2.0 / (N * 0.5)  # Hann correction
    freqs = fftfreq(N, 1.0/sr)[:N//2]
    
    # Convert to mV
    amp_mv = Y * 1000
    
    mask = freqs <= fmax
    f_m = freqs[mask]
    a_m = amp_mv[mask]
    
    # Find peaks
    peaks, props = find_peaks(a_m, height=a_m.max() * threshold, distance=2)
    if len(peaks) == 0:
        return f_m, a_m, [], []
    
    top_idx = np.argsort(a_m[peaks])[-n_top:][::-1]
    return f_m, a_m, f_m[peaks[top_idx]], a_m[peaks[top_idx]]

def match_prime(freq, tolerance=25):
    """Match a detected frequency to nearest prime frequency."""
    for name, f in PRIME_FREQS.items():
        if abs(freq - f) <= tolerance:
            return name, f
    return None, None

def main():
    print("=" * 70)
    print("RING SURVEY FFT ANALYSIS — 22 May 2026 — Board 3 — 5ms/div (60ms)")
    print("=" * 70)
    
    # Collect results: cell → {prime_name: amplitude_mV}
    all_results = {}
    all_spectra = {}
    
    for cell in CELLS:
        fpath = find_file(cell)
        if fpath is None:
            print(f"\n⚠️  {cell}: NO DATA FILE FOUND")
            continue
        
        data = np.load(fpath, allow_pickle=True)
        t1, v1 = data['t1'], data['v1']
        t2, v2 = data['t2'], data['v2']
        sr = 1.0 / (t1[1] - t1[0])
        df = sr / len(t1)
        
        driven_str = f" ← DRIVEN {DRIVEN[cell]} ({PRIME_FREQS[DRIVEN[cell]]}Hz)" if cell in DRIVEN else " (undriven)"
        print(f"\n{'='*50}")
        print(f"{cell}{driven_str}")
        print(f"File: {os.path.basename(fpath)}")
        print(f"SR: {sr:.0f} Sa/s, N: {len(v1)}, Δf: {df:.1f} Hz")
        
        cell_result = {}
        
        for ch_idx, (v, ch_name) in enumerate([(v1, 'CH1/A'), (v2, 'CH2/B')]):
            freqs, amps, peak_f, peak_a = fft_peaks(v, sr)
            all_spectra[(cell, ch_name)] = (freqs, amps)
            
            print(f"\n  {ch_name} peaks:")
            for pf, pa in zip(peak_f, peak_a):
                name, exact_f = match_prime(pf)
                tag = f" ★ {name}" if name else ""
                print(f"    {pf:7.1f} Hz  {pa:6.2f} mV{tag}")
                if name and ch_idx == 0:  # Use CH1 for heatmap
                    if name not in cell_result or pa > cell_result[name]:
                        cell_result[name] = pa
        
        all_results[cell] = cell_result
    
    # ===== HEATMAP =====
    print("\n" + "=" * 70)
    print("PRIME FREQUENCY HEATMAP (CH1 amplitudes, mV)")
    print("=" * 70)
    
    prime_names = list(PRIME_FREQS.keys())
    header = f"{'Cell':>6} | " + " | ".join(f"{n:>7}" for n in prime_names) + " | Total"
    print(header)
    print("-" * len(header))
    
    heatmap = np.zeros((len(CELLS), len(prime_names)))
    for i, cell in enumerate(CELLS):
        row_vals = []
        for j, pn in enumerate(prime_names):
            val = all_results.get(cell, {}).get(pn, 0)
            heatmap[i, j] = val
            row_vals.append(val)
        driven_mark = " *" if cell in DRIVEN else ""
        total = sum(row_vals)
        print(f"{cell:>6} | " + " | ".join(f"{v:7.2f}" for v in row_vals) + f" | {total:5.1f}{driven_mark}")
    
    print("\n* = driven cell")
    
    # ===== PLOT =====
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Board 3 Ring Survey — 22 May 2026 — 5ms/div (Δf≈17Hz)', fontsize=14, fontweight='bold')
    
    # Panel 1: Heatmap
    ax = axes[0, 0]
    im = ax.imshow(heatmap.T, aspect='auto', cmap='hot', interpolation='nearest')
    ax.set_xticks(range(len(CELLS)))
    ax.set_xticklabels(CELLS, rotation=45)
    ax.set_yticks(range(len(prime_names)))
    ax.set_yticklabels([f"{n} ({PRIME_FREQS[n]}Hz)" for n in prime_names])
    ax.set_title('Prime Frequency Amplitude by Cell (CH1, mV)')
    plt.colorbar(im, ax=ax, label='mV')
    # Mark driven cells
    for i, cell in enumerate(CELLS):
        if cell in DRIVEN:
            j = prime_names.index(DRIVEN[cell])
            ax.plot(i, j, 'ws', markersize=8, markeredgewidth=2)
    
    # Panel 2: All CH1 spectra overlaid
    ax = axes[0, 1]
    colors = plt.cm.tab20(np.linspace(0, 1, 12))
    for i, cell in enumerate(CELLS):
        key = (cell, 'CH1/A')
        if key in all_spectra:
            f, a = all_spectra[key]
            ax.plot(f, a, color=colors[i], alpha=0.7, linewidth=0.8, label=cell)
    for name, freq in PRIME_FREQS.items():
        ax.axvline(freq, color='red', alpha=0.3, linestyle='--', linewidth=0.8)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude (mV)')
    ax.set_title('CH1 FFT Spectra — All Cells')
    ax.set_xlim(0, 1200)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    
    # Panel 3: Vpp bar chart
    ax = axes[1, 0]
    ch1_vpp = []
    ch2_vpp = []
    for cell in CELLS:
        fpath = find_file(cell)
        if fpath:
            d = np.load(fpath, allow_pickle=True)
            ch1_vpp.append((d['v1'].max() - d['v1'].min()) * 1000)
            ch2_vpp.append((d['v2'].max() - d['v2'].min()) * 1000)
        else:
            ch1_vpp.append(0)
            ch2_vpp.append(0)
    
    x = np.arange(len(CELLS))
    ax.bar(x - 0.2, ch1_vpp, 0.4, color='gold', label='CH1 (TORSION_A)', edgecolor='black')
    ax.bar(x + 0.2, ch2_vpp, 0.4, color='cyan', label='CH2 (TORSION_B)', edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels(CELLS, rotation=45)
    ax.set_ylabel('Vpp (mV)')
    ax.set_title('Peak-to-Peak Voltage by Cell')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    # Mark driven/undriven boundary
    ax.axvline(5.5, color='red', alpha=0.5, linestyle=':', linewidth=2)
    ax.text(2.5, max(ch1_vpp)*0.95, 'DRIVEN', ha='center', color='red', fontweight='bold')
    ax.text(8.5, max(ch1_vpp)*0.95, 'UNDRIVEN', ha='center', color='red', fontweight='bold')
    
    # Panel 4: Total prime energy per cell (polar plot for ring topology)
    ax = axes[1, 1]
    ax.remove()
    ax = fig.add_subplot(2, 2, 4, projection='polar')
    angles = np.linspace(0, 2*np.pi, len(CELLS), endpoint=False)
    totals = [sum(all_results.get(c, {}).values()) for c in CELLS]
    # Close the loop
    angles_c = np.append(angles, angles[0])
    totals_c = np.append(totals, totals[0])
    ax.plot(angles_c, totals_c, 'gold', linewidth=2)
    ax.fill(angles_c, totals_c, 'gold', alpha=0.3)
    ax.set_thetagrids(np.degrees(angles), CELLS)
    ax.set_title('Total Prime Energy by Cell (Ring)', pad=20)
    # Mark driven cells
    for i, cell in enumerate(CELLS):
        if cell in DRIVEN:
            ax.plot(angles[i], totals[i], 'r*', markersize=12)
    
    plt.tight_layout()
    out_path = os.path.join(DATA_DIR, 'ring_survey_fft_22may.png')
    plt.savefig(out_path, dpi=150)
    print(f"\n📊 Ring survey plot saved: {out_path}")

if __name__ == '__main__':
    main()
