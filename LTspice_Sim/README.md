# Prime_Maxel-v3 LTspice Simulation

## Purpose
Simulate the Golden Cell circuit to understand:
1. Single-cell oscillation behaviour
2. Multi-cell coupling through torsion traces
3. Sensitivity to TORSION_A/B length ratio (1.206 vs 1.182)
4. What signals are measurable at LM324 outputs

## Files
- `golden_cell_single.cir` — Single cell: GreenPAK model + LM324 + torsion stubs
- `golden_cell_3ring.cir` — 3-cell ring with torsion trace coupling
- `LM324.sub` — TI LM324 SPICE subcircuit
- `torsion_sweep.cir` — Parametric sweep of torsion ratio

## Component Models
- **SLG47004V:** Modelled as configurable pulse source (internal oscillator) 
  with op-amp output stages (simplified behavioural model)
- **LM324:** TI official SPICE model
- **Torsion traces:** Lossy transmission line (LTRA) — Z0=50Ω, εr=4.4, 
  loss tangent 0.02, copper conductivity for 0.229mm/2oz Cu

## Key Parameters
- TORSION_A length: 497.97mm → delay ~3.32ns (εeff≈3.2, v=167.7mm/ns)
- TORSION_B length: 600.56mm → delay ~3.58ns  
- Δ delay: ~0.68ns
- GreenPAK oscillator: swept 100kHz — 10MHz
- Supply: +12V (VCC_PWT), regulated to 5V/3.3V for ICs
