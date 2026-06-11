#!/usr/bin/env python3
"""
Rigol DS1054Z Waveform Capture & Analysis Tool
================================================
Captures waveform data from the Rigol DS1054Z via USB, saves raw data,
and performs FFT analysis to identify frequency components.

Usage:
    python3 rigol_capture.py                  # Auto-detect scope, capture CH1
    python3 rigol_capture.py --channels 1 2   # Capture CH1 and CH2
    python3 rigol_capture.py --list           # List connected instruments
    python3 rigol_capture.py --label "TORSION_A"  # Add label to filenames

Requirements:
    pip3 install pyvisa pyvisa-py numpy matplotlib scipy
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    import pyvisa
except ImportError:
    print("ERROR: pyvisa not installed. Run: pip3 install pyvisa pyvisa-py")
    sys.exit(1)


# ── Configuration ──────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent.parent / "Adrian Docs" / "Scope Data"
PRIME_FREQS = {
    "f0/1":  1024.0,
    "f0/3":  341.3,
    "f0/5":  204.8,
    "f0/7":  146.3,
    "f0/11": 93.1,
    "f0/13": 78.8,
}
FREQ_TOLERANCE = 0.05  # 5% tolerance for matching


# ── Scope Communication ───────────────────────────────────────────────────

def find_scope():
    """Auto-detect Rigol scope on USB."""
    rm = pyvisa.ResourceManager("@py")
    resources = rm.list_resources()
    
    if not resources:
        print("No instruments found. Check USB connection.")
        print("Tip: Make sure the USB-B cable is connected to the REAR port of the Rigol.")
        return None, None
    
    print(f"Found {len(resources)} instrument(s):")
    for r in resources:
        print(f"  {r}")
    
    # Try to find a Rigol
    for r in resources:
        try:
            inst = rm.open_resource(r)
            inst.timeout = 5000
            idn = inst.query("*IDN?").strip()
            print(f"  → {idn}")
            if "RIGOL" in idn.upper() or "DS1" in idn.upper():
                print(f"  ✓ Rigol scope detected!")
                return rm, inst
        except Exception as e:
            print(f"  ✗ Could not query {r}: {e}")
    
    # Fall back to first instrument
    try:
        inst = rm.open_resource(resources[0])
        inst.timeout = 5000
        return rm, inst
    except Exception as e:
        print(f"Could not open instrument: {e}")
        return None, None


def capture_channel(scope, channel):
    """Capture waveform data from a single channel."""
    ch = f"CHAN{channel}"
    
    # Check if channel is displayed
    displayed = scope.query(f":{ch}:DISP?").strip()
    if displayed == "0":
        print(f"  Warning: {ch} is not displayed on scope. Enabling it...")
        scope.write(f":{ch}:DISP ON")
        time.sleep(0.5)
    
    # Stop the scope to capture stable data
    scope.write(":STOP")
    time.sleep(0.3)
    
    # Get waveform preamble (contains scale/offset/sample info)
    scope.write(f":WAV:SOUR {ch}")
    scope.write(":WAV:MODE NORMal")  # Screen data (faster, good enough)
    scope.write(":WAV:FORM ASCii")
    
    # Read preamble
    preamble_raw = scope.query(":WAV:PRE?").strip()
    preamble = preamble_raw.split(",")
    
    # Parse preamble fields
    # format, type, points, count, xincrement, xorigin, xreference, yincrement, yorigin, yreference
    info = {
        "format": int(preamble[0]),
        "type": int(preamble[1]),
        "points": int(preamble[2]),
        "count": int(preamble[3]),
        "x_increment": float(preamble[4]),   # Time between samples (seconds)
        "x_origin": float(preamble[5]),       # Time of first sample
        "x_reference": float(preamble[6]),
        "y_increment": float(preamble[7]),    # Voltage per bit
        "y_origin": float(preamble[8]),
        "y_reference": float(preamble[9]),
    }
    
    sample_rate = 1.0 / info["x_increment"]
    duration = info["points"] * info["x_increment"]
    
    print(f"  {ch}: {info['points']} points, {sample_rate/1e6:.2f} MSa/s, {duration*1e3:.2f} ms window")
    
    # Read waveform data
    raw = scope.query(":WAV:DATA?")
    
    # Parse ASCII data (comes as comma-separated values, may have header)
    # Strip TMC header if present
    if raw.startswith("#"):
        # Binary header: #NXXXXXXX where N is number of digits in length
        n_digits = int(raw[1])
        data_start = 2 + n_digits
        raw = raw[data_start:]
    
    voltages = []
    for val in raw.split(","):
        val = val.strip()
        if val:
            try:
                voltages.append(float(val))
            except ValueError:
                pass
    
    voltages = np.array(voltages)
    n_points = len(voltages)
    times = np.arange(n_points) * info["x_increment"] + info["x_origin"]
    
    print(f"  Got {n_points} samples, V range: [{voltages.min():.4f}, {voltages.max():.4f}] V")
    
    # Get scope measurements for reference
    measurements = {}
    for meas in ["FREQ", "VPP", "VRMS", "VAVG"]:
        try:
            val = scope.query(f":MEAS:ITEM? {meas},{ch}").strip()
            measurements[meas] = float(val) if val not in ["", "9.9E37"] else None
        except:
            measurements[meas] = None
    
    # Resume scope
    scope.write(":RUN")
    
    return {
        "channel": channel,
        "times": times,
        "voltages": voltages,
        "info": info,
        "sample_rate": sample_rate,
        "measurements": measurements,
    }


# ── Analysis ──────────────────────────────────────────────────────────────

def analyse_fft(data):
    """Perform FFT analysis and identify frequency components."""
    voltages = data["voltages"]
    sample_rate = data["sample_rate"]
    n = len(voltages)
    
    # Remove DC offset
    voltages_ac = voltages - np.mean(voltages)
    
    # Apply Hanning window to reduce spectral leakage
    window = np.hanning(n)
    voltages_windowed = voltages_ac * window
    
    # FFT
    fft_vals = np.fft.rfft(voltages_windowed)
    fft_freqs = np.fft.rfftfreq(n, d=1.0/sample_rate)
    fft_magnitude = 2.0 * np.abs(fft_vals) / n  # Normalize
    
    # Convert to dB (relative to max)
    fft_db = 20 * np.log10(fft_magnitude / (np.max(fft_magnitude) + 1e-12) + 1e-12)
    
    # Find peaks (simple peak detection)
    from scipy.signal import find_peaks
    
    # Only look at frequencies up to 50kHz (our signals are < 2kHz, but allow harmonics)
    freq_mask = fft_freqs < 50000
    peaks_idx, peak_props = find_peaks(
        fft_magnitude[freq_mask],
        height=np.max(fft_magnitude[freq_mask]) * 0.05,  # 5% of max
        distance=max(1, int(10 / (fft_freqs[1] - fft_freqs[0]))),  # Min 10 Hz apart
        prominence=np.max(fft_magnitude[freq_mask]) * 0.02,
    )
    
    # Identify peaks
    detected_peaks = []
    for idx in peaks_idx:
        freq = fft_freqs[idx]
        mag = fft_magnitude[idx]
        
        # Check if this matches a known prime frequency
        match = None
        for name, target_freq in PRIME_FREQS.items():
            if abs(freq - target_freq) / target_freq < FREQ_TOLERANCE:
                match = name
                break
            # Also check harmonics (2×, 3×)
            for harmonic in [2, 3, 4]:
                if abs(freq - target_freq * harmonic) / (target_freq * harmonic) < FREQ_TOLERANCE:
                    match = f"{name}×{harmonic}"
                    break
        
        detected_peaks.append({
            "frequency": freq,
            "magnitude": mag,
            "magnitude_db": 20 * np.log10(mag / (np.max(fft_magnitude) + 1e-12) + 1e-12),
            "match": match,
        })
    
    # Sort by magnitude (strongest first)
    detected_peaks.sort(key=lambda p: p["magnitude"], reverse=True)
    
    return {
        "fft_freqs": fft_freqs,
        "fft_magnitude": fft_magnitude,
        "fft_db": fft_db,
        "peaks": detected_peaks,
        "dc_offset": np.mean(voltages),
        "ac_rms": np.std(voltages_ac),
    }


# ── Output ────────────────────────────────────────────────────────────────

def save_data(data, analysis, label, output_dir):
    """Save raw data and analysis results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ch = data["channel"]
    prefix = f"{timestamp}_CH{ch}"
    if label:
        prefix += f"_{label}"
    
    # Save raw waveform as CSV
    csv_path = output_dir / f"{prefix}_raw.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_s", "voltage_V"])
        for t, v in zip(data["times"], data["voltages"]):
            writer.writerow([f"{t:.10e}", f"{v:.6e}"])
    print(f"  Saved raw data: {csv_path.name}")
    
    # Save FFT as CSV
    fft_path = output_dir / f"{prefix}_fft.csv"
    with open(fft_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["frequency_Hz", "magnitude_V", "magnitude_dB"])
        for freq, mag, db in zip(analysis["fft_freqs"], analysis["fft_magnitude"], analysis["fft_db"]):
            if freq < 100000:  # Only save up to 100kHz
                writer.writerow([f"{freq:.2f}", f"{mag:.8e}", f"{db:.2f}"])
    print(f"  Saved FFT data: {fft_path.name}")
    
    # Save analysis summary as JSON
    summary = {
        "timestamp": timestamp,
        "channel": ch,
        "label": label,
        "sample_rate": data["sample_rate"],
        "n_points": len(data["voltages"]),
        "window_duration_ms": len(data["voltages"]) / data["sample_rate"] * 1000,
        "dc_offset_V": analysis["dc_offset"],
        "ac_rms_V": analysis["ac_rms"],
        "scope_measurements": data["measurements"],
        "detected_peaks": [
            {
                "frequency_Hz": p["frequency"],
                "magnitude_V": p["magnitude"],
                "magnitude_dB": p["magnitude_db"],
                "match": p["match"],
            }
            for p in analysis["peaks"][:20]  # Top 20 peaks
        ],
        "prime_freq_matches": [
            p for p in analysis["peaks"] if p["match"] is not None
        ],
    }
    
    json_path = output_dir / f"{prefix}_analysis.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Saved analysis: {json_path.name}")
    
    return csv_path, fft_path, json_path


def plot_results(data, analysis, label, output_dir):
    """Generate waveform + FFT plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available, skipping plot")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ch = data["channel"]
    prefix = f"{timestamp}_CH{ch}"
    if label:
        prefix += f"_{label}"
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(f"CH{ch} — {label or 'Capture'}", fontsize=14, fontweight="bold")
    
    # Waveform
    times_ms = data["times"] * 1000
    ax1.plot(times_ms, data["voltages"], linewidth=0.5, color="#FFD700")
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Voltage (V)")
    ax1.set_title(f"Waveform — DC={analysis['dc_offset']:.3f}V, AC RMS={analysis['ac_rms']*1000:.1f}mV")
    ax1.set_facecolor("#1a1a2e")
    ax1.grid(True, alpha=0.3)
    
    # FFT (up to 5kHz for our frequency range)
    freq_mask = analysis["fft_freqs"] < 5000
    ax2.plot(analysis["fft_freqs"][freq_mask], 
             analysis["fft_magnitude"][freq_mask] * 1000,  # mV
             linewidth=0.8, color="#00FF88")
    
    # Mark prime frequencies
    for name, freq in PRIME_FREQS.items():
        ax2.axvline(x=freq, color="red", alpha=0.4, linestyle="--", linewidth=0.8)
        ax2.text(freq, ax2.get_ylim()[1] * 0.9, name, rotation=90, 
                fontsize=7, color="red", alpha=0.7, ha="right")
    
    # Mark detected peaks
    for peak in analysis["peaks"][:10]:
        if peak["frequency"] < 5000:
            marker = "★" if peak["match"] else "●"
            color = "red" if peak["match"] else "yellow"
            ax2.annotate(
                f"{peak['frequency']:.0f}Hz",
                xy=(peak["frequency"], peak["magnitude"] * 1000),
                fontsize=7, color=color, fontweight="bold",
                textcoords="offset points", xytext=(5, 5),
            )
    
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Magnitude (mV)")
    ax2.set_title(f"FFT Spectrum — {len(analysis['peaks'])} peaks detected, "
                   f"{sum(1 for p in analysis['peaks'] if p['match'])} prime matches")
    ax2.set_facecolor("#1a1a2e")
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    plot_path = output_dir / f"{prefix}_plot.png"
    fig.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor="#0e0e1a")
    plt.close(fig)
    print(f"  Saved plot: {plot_path.name}")
    
    return plot_path


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rigol DS1054Z Waveform Capture & Analysis")
    parser.add_argument("--list", action="store_true", help="List connected instruments")
    parser.add_argument("--channels", "-c", nargs="+", type=int, default=[1],
                       help="Channels to capture (1-4). Default: 1")
    parser.add_argument("--label", "-l", type=str, default="",
                       help="Label for this capture (e.g. TORSION_A, U2_TP1)")
    parser.add_argument("--output", "-o", type=str, default=str(OUTPUT_DIR),
                       help=f"Output directory. Default: {OUTPUT_DIR}")
    parser.add_argument("--no-plot", action="store_true", help="Skip plot generation")
    parser.add_argument("--continuous", "-C", action="store_true",
                       help="Continuous capture mode (press Ctrl+C to stop)")
    parser.add_argument("--interval", type=float, default=2.0,
                       help="Seconds between captures in continuous mode")
    
    args = parser.parse_args()
    output_dir = Path(args.output)
    
    print("=" * 60)
    print("  Rigol DS1054Z Capture & Analysis Tool")
    print("  Prime Maxel v3 — Tusk Innovations")
    print("=" * 60)
    print()
    
    # List mode
    if args.list:
        rm = pyvisa.ResourceManager("@py")
        resources = rm.list_resources()
        if resources:
            for r in resources:
                try:
                    inst = rm.open_resource(r)
                    inst.timeout = 3000
                    idn = inst.query("*IDN?").strip()
                    print(f"  {r} → {idn}")
                    inst.close()
                except:
                    print(f"  {r} → (could not identify)")
        else:
            print("  No instruments found.")
        return
    
    # Find scope
    print("Searching for Rigol scope...")
    rm, scope = find_scope()
    if scope is None:
        print("\nTroubleshooting:")
        print("  1. USB-B cable connected to REAR port of Rigol?")
        print("  2. Scope powered on?")
        print("  3. Try: python3 -c \"import pyvisa; print(pyvisa.ResourceManager('@py').list_resources())\"")
        return
    
    idn = scope.query("*IDN?").strip()
    print(f"\nConnected: {idn}")
    print(f"Output dir: {output_dir}")
    print()
    
    def do_capture():
        """Run one capture cycle."""
        results = []
        for ch in args.channels:
            print(f"Capturing CH{ch}...")
            data = capture_channel(scope, ch)
            
            print(f"  Analysing FFT...")
            analysis = analyse_fft(data)
            
            # Print detected peaks
            if analysis["peaks"]:
                print(f"  Top frequency peaks:")
                for i, peak in enumerate(analysis["peaks"][:8]):
                    match_str = f" ← {peak['match']}" if peak["match"] else ""
                    print(f"    {i+1}. {peak['frequency']:8.1f} Hz  "
                          f"{peak['magnitude']*1000:6.2f} mV  "
                          f"({peak['magnitude_db']:+.1f} dB){match_str}")
            
            prime_matches = [p for p in analysis["peaks"] if p["match"]]
            if prime_matches:
                print(f"  🎯 PRIME FREQUENCY MATCHES: {len(prime_matches)}")
                for p in prime_matches:
                    print(f"     {p['match']}: {p['frequency']:.1f} Hz ({p['magnitude']*1000:.2f} mV)")
            
            # Save
            save_data(data, analysis, args.label, output_dir)
            if not args.no_plot:
                plot_results(data, analysis, args.label, output_dir)
            
            results.append((data, analysis))
            print()
        
        return results
    
    if args.continuous:
        print(f"Continuous capture mode (interval: {args.interval}s). Press Ctrl+C to stop.\n")
        capture_num = 0
        try:
            while True:
                capture_num += 1
                print(f"── Capture #{capture_num} ──")
                do_capture()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print(f"\nStopped after {capture_num} captures.")
    else:
        do_capture()
    
    # Cleanup
    scope.close()
    rm.close()
    print("Done! 🎯")


if __name__ == "__main__":
    main()
