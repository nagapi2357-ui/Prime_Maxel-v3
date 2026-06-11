# Unsorted Folder Review — Wheat from Chaff
*Reviewed by Nagaπ, 13 Feb 2026*

## 🌾 WHEAT — Directly Relevant to POC

### 1. Phased Experiment Plan for Breadboard Prototype (CRITICAL)
**Location:** `Unsorted/Adrian's Python Code/2026MaxelAlgebra/Breadboard Experiments/`
**Why it matters:** This is the Rosetta Stone for the POC. It documents:
- Breadboard observations: Layout B (centered) shows 95% revival efficiency vs Layout A (end-centered) at 85%
- **Hardware Koide fixed point: Q_ℓ ≈ 0.86** — this is the measurable target
- 3-phase plan: (1) 8-16 nodes symmetry optimization, (2) 50-100 nodes plaquette scale-up, (3) thermodynamic computation POC
- Key materials: SLG47004V, LM324 op-amps, 47pF coupling caps, rheostats for alpha tuning
- Metrics: revival efficiency, torsion ratio, Q_ℓ stability, diff to Koide 0.667
- **This plan is what our KiCad PCB should implement as Phase 2/3**

### 2. Extropic TSU Integration Scripts
**Location:** `Unsorted/Adrian's Python Code/2026MaxelAlgebra/Extropic TSU/`
**Key files:**
- `Refined_thrml_EBM_Export_Logic.py` — exports prime landscape as Energy-Based Model for thermodynamic hardware
- `prime_ebm_thrml_1000000.json` — pre-computed EBM for 1M primes
- `Statistical_Validation_Framework_τspread.py` — validates tau-spread convergence
- `Ulam-Spiral_τspread_Heatmap.py` — visualizes prime resonance on Ulam spiral
**Why:** Direct bridge from PWT math → Extropic hardware format. The POC circuit is a physical prototype of this EBM.

### 3. POC Design Files (Pre-KiCad Attempts)
**Location:** `Unsorted/Adrian's Python Code/2026MaxelAlgebra/POC/`
**Key files:**
- `trace_impedance_calculator.py` — earlier impedance calc (simpler than our z0_audit.py)
- `calibration_log.py`, `resonance_report_gen.py`, `tasp_sync_v1.py` — measurement/reporting tools
- `BOM.csv` — earlier bill of materials
- `KiCad/ulam_spiral_placement_logic.py` — Ulam spiral placement for KiCad (could be useful!)
- AutoCAD attempts (`.dwg` files) — abandoned in favor of KiCad
**Why:** Shows evolution of thinking. The Ulam spiral placement logic may feed our PCB layout.

### 4. Proof-of-Resonance (PoR) Whitepaper
**Location:** `Unsorted/Adrian's Python Code/PoR/Documents/Gemini/Whitepaper.odt`
**Why it matters:** Defines PoR as a consensus mechanism where:
- Prime Quadrance metrics replace hash difficulty
- "Spread Collapse" phenomenon = resonance in high-integer regimes
- Thermodynamic hardware finds low-energy solutions (resonance) vs brute-force
- **This is the ultimate application** — the POC circuit proves the physical substrate works

### 5. PoR Core Reference & Mining Sims
**Location:** `Unsorted/Adrian's Python Code/PoR/Gemini/`
**Key files:**
- `PoR_Core_Reference.py` — core PoR implementation
- `thermodynamic_emulator-v1.py` — emulates TSU behavior
- `tesla_swarm_miner-v1.py`, `hybrid_vortex_miner-v3.py` — mining algorithm experiments
- `symbiotic_governance-v2.py` — RL-based difficulty adjustment
**Why:** These are the software counterparts to our hardware POC.

### 6. LightTheory Scripts
**Location:** `Unsorted/Adrian's Python Code/LightTheory/`
**Key files:**
- `Modulo_24_Wheel.py` — visualizes the Mod-24 prime wheel
- `The_Prime_Torsion_Model.py` — the core torsion math
- `The_Resonance_Bridge.py` — bridge between prime gaps and resonance
- `The_Event_Horizon_Scanner.py` — tests stability across magnitudes
**Why:** These are the mathematical foundations our circuit embodies.

### 7. Prime NAND Gate & Breadboard Experiment Docs
**Location:** `Background for Nagaπ/LTspice Bread Board Experiment/Documentation/`
**Why:** Documents the first physical experiment — maps to our POC progression.

---

## 🌾 WHEAT — Valuable Context / Future Use

### 8. EMFGenie Chats (Selected)
**Location:** `Unsorted/01 WRITING and AI Chats/AI Chat/01 Gemini/`
- EMFGenie 14 "The Genesis Set" — foundational set theory thinking
- EMFGenie 15 "Agency over information" — primes as agents of structure
- EMFGenie 16 "Cell division/Morphogenesis" — biological prime emergence

### 9. SET Theory Files
**Location:** `Unsorted/01 WRITING and AI Chats/Set Theory/`
- `GSET.odt` — "The Set is Greater than the Sum of Its Elements" — Adrian's axioms for prime-based set theory
- `THE SET.odt` — Philosophical foundation connecting Satoshi/BTC to prime structure

### 10. Buckminster Fuller Notes
**Location:** `Unsorted/01 WRITING and AI Chats/Buckminster Fuller/`
- Tensegrity concepts may inform PCB structural layout thinking

### 11. SOLSATS (Solar Data)
**Location:** `Unsorted/01 WRITING and AI Chats/SOLSATS/`
- Sunspot data, solar flux, magnetic data — potential future PWT correlation study
- Not relevant to current POC

### 12. Dusty's Road — Full Creative Archive
**Location:** `Unsorted/01 WRITING and AI Chats/AI Chat/01 Gemini/Dusty/`
- Complete chapter drafts, character development (AquaSol, BeeMan, Marama)
- Tensegrity artwork (.xcf/.png)
- **Future YouTube channel content**

### 13. AI Chat History (Gemini/Claude/Grok/ChatGPT/Deepseek)
**Location:** `Unsorted/01 WRITING and AI Chats/AI Chat/`
- PWT thesis versions V8 through V15 development history across all major LLMs
- Cross-AI validation (Grok reviewing Claude's results, etc.)
- LaTeX outputs available in some folders
- **Archive value** — shows the collaborative AI journey

---

## 🟡 CHAFF — Low Priority / Superseded

### Superseded Code
- `PwodeV9/`, `PwodeV9-4/`, `PwodeV10/`, `PwodeV11/` — older PWODE versions, superseded by V15 and the Multipolar Engine
- `Rational Software V13/`, `TCM V12/` — older thesis code, superseded
- `Superformula/` — exploratory, not connected to current POC
- `mp Data Downloads/` — raw data files

### Duplicate Content
- `ONCE IN A BLUE MOON.odt` exists in both Background and Unsorted/01 WRITING
- Multiple copies of prime_maxel_v2 data files across PoR and Extropic TSU folders

### AutoCAD Files
- `POC/AutoCad - not used/` — explicitly marked as abandoned

---

## 📋 Summary Priorities for POC

| Priority | Item | Action |
|----------|------|--------|
| 🔴 P0 | Phased Experiment Plan | Use as POC specification |
| 🔴 P0 | Breadboard observations (Q_ℓ ≈ 0.86, revival 95%) | Define measurable success criteria |
| 🟠 P1 | Extropic TSU scripts | Adapt EBM export for SLG47004V config |
| 🟠 P1 | PoR Whitepaper | Reference for what we're ultimately proving |
| 🟡 P2 | Ulam spiral placement | Consider for PCB layout |
| 🟡 P2 | LightTheory scripts | Verify torsion math matches circuit geometry |
| ⚪ P3 | AI chat archives | Historical reference |
| ⚪ P3 | SOLSATS/Creative | Future projects |
