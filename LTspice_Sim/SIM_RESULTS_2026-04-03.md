# LTspice Simulation Results — 3 April 2026

## Models Tested
1. **golden_cell_3ring.cir (v1)** — Original model, RC-filtered injection, ideal transmission lines
2. **golden_cell_3ring_v2.cir** — Cross-coupled model, lossy LTRA lines, no RC filter

## Key Findings

### 1. Self-Sustaining Ring Oscillator ✅
A single 1µs pulse at 50µs creates a **permanently self-sustaining oscillation** on the torsion ring. Tested to 1ms with zero decay. The ring acts as a latent resonator — it needs excitation to activate, but once started, the LM324 feedback loop sustains it indefinitely.

### 2. Minimum 3 Nodes Required ✅
The 2-cell model produces no oscillation (flat line at −691.5mV). The closed ring topology with ≥3 nodes is essential for the feedback loop to sustain.

### 3. Pulse Required for B-Ring Activation ✅
With V_PULSE = 0, TORSION_B stays dead flat at −345.4mV. The GreenPAK oscillators alone (at prime-ratio frequencies) do not couple into the torsion ring. External excitation is required.

### 4. Torsion Ratio Effect — Subtle but Real ✅
**v1 model (RC-filtered):** No visible difference between TB=497.97mm and TB=600.56mm — the 1µs RC time constant (Rinj × Cinj = 10kΩ × 100pF) completely masks the sub-nanosecond transmission line delay.

**v2 model (cross-coupled, lossy):** Clear differences visible:
- **Period changes:** Equal ratio → ~1.25µs period; Original ratio (1.206) → ~1.05µs period (~20% faster)
- **Start time shifts:** Original ratio triggers ~300ns earlier due to cross-coupling feedback path timing
- **Amplitude:** Essentially identical (~63mV p-p on TORSION_A)

### 5. TORSION_A Decay (v1)
The comparator outputs driving TORSION_A decay from ~1.25V to 0V over ~140-200µs regardless of pulse injection. This is an LM324 DC offset accumulation artefact — the single-supply op-amp slowly saturates. Not a physics issue.

## What This Means for the Physical Board

### What WILL work:
- The ring topology will sustain oscillation once excited — this is real circuit behaviour
- The Arduino can fire the centre pulse and measure the ring response
- Different cells at different prime-ratio frequencies will create interference patterns

### What needs attention:
- **The torsion ratio effect is subtle** — the line delay (~0.3ns per segment) is dwarfed by the LM324 response time (~1µs). On the real board, the ratio may only be measurable with high-speed instrumentation or by looking at phase differences between cells.
- **The LM324 dominates** the oscillation frequency. The op-amp slew rate and gain-bandwidth product (~1MHz) set the fundamental timing, not the transmission line properties. To see true torsion effects, the circuit would need faster comparators or direct measurement of the trace signals.
- **Real GreenPAK behaviour** will differ from ideal pulse sources. The SLG47004V's actual output impedance, rise time, and programmable functions will affect coupling.

### Recommended Next Steps:
1. **Build and test** — the sim confirms the basic topology works. Real-world measurements may reveal effects the sim can't capture (EMI coupling, ground plane currents, etc.)
2. **Use the Arduino ADC** to sample TORSION_A/B at multiple cells simultaneously and look for phase relationships
3. **Try different GreenPAK frequencies** and look for resonance peaks where the torsion length matches a harmonic
4. **Consider faster comparators** (e.g., LM339 or TLV3501) if more sensitivity to trace properties is needed

## File Index
- `golden_cell_3ring.cir` — v1 original model
- `golden_cell_3ring_v2.cir` — v2 cross-coupled lossy model  
- `torsion_ratio_sweep.cir` — 2-cell model (dead — needs ring topology)
- `Files for Nagaπ from me/` — All screenshots from today's session
