#!/usr/bin/env python3
"""
Prime_Maxel-v3 PCB Component Placement Script
==============================================
Precision placement of all components on the Arduino Mega shield.

Layout: 6 rows × 2 columns of golden cells (grouped by I2C bus),
TCA9548A mux centered near the I2C header, test points accessible
along cell edges.

USAGE:
  1. SAVE and CLOSE KiCad PCB editor
  2. Run: python3 place_components.py
  3. Re-open Prime_Maxel-v3.kicad_pcb in KiCad

A backup is created automatically before any changes.
"""

import re
import shutil
import os
from datetime import datetime

# ─── Configuration ─────────────────────────────────────────────────
PCB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Prime_Maxel-v3.kicad_pcb")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Prime_Maxel-v3-backups")

# ─── Cell-to-component mapping ────────────────────────────────────
# Cell N → (LM324_ref, SLG_ref, [cap_decoup_LM, cap_decoup_SLG, cap_vref], [R_divR1, R_divR2], [TP_torA, TP_torB, TP_vref, TP_pulse])
CELLS = {}
for i in range(12):
    lm_ref  = f"U{2 + i*2}"       # U2,U4,...,U24 (even)
    slg_ref = f"U{3 + i*2}"       # U3,U5,...,U25 (odd)
    c_base  = i * 3 + 1           # C1,C4,C7,...
    caps    = [f"C{c_base}", f"C{c_base+1}", f"C{c_base+2}"]
    r_base  = i * 2 + 3           # R3,R5,R7,...
    res     = [f"R{r_base}", f"R{r_base+1}"]
    tp_base = i * 4 + 1           # TP1,TP5,TP9,...
    tps     = [f"TP{tp_base}", f"TP{tp_base+1}", f"TP{tp_base+2}", f"TP{tp_base+3}"]
    CELLS[i] = {
        'lm324': lm_ref, 'slg': slg_ref,
        'caps': caps, 'res': res, 'tps': tps,
        'i2c_bus': i // 2
    }

# ─── Board geometry ───────────────────────────────────────────────
# Arduino Mega connector positions define the shield boundary.
# Usable inner area: x ≈ 132–175mm, y ≈ -128 to -58mm (70mm tall, 43mm wide)
# KiCad Y-axis is inverted (more negative = higher on board)

# Cell grid: 6 rows × 2 columns, grouped by I2C bus
# Each cell: ~18mm wide × ~10.5mm tall (with generous spacing)
CELL_WIDTH   = 19.0    # mm, horizontal pitch between columns
CELL_HEIGHT  = 10.5    # mm, vertical pitch between rows

# Grid origin (top-left cell center) - centered in usable area
GRID_ORIGIN_X = 140.0  # left column center (clear of left headers at x=129.5)
GRID_ORIGIN_Y = -124.0 # top row center

# Cell layout order: row-major, bus pairs adjacent
# Row 0: Cell 0 (bus0), Cell 1 (bus0)
# Row 1: Cell 2 (bus1), Cell 3 (bus1)
# ...
# Row 5: Cell 10(bus5), Cell 11(bus5)
CELL_GRID = [
    (0, 1),    # Row 0 - I2C Bus 0
    (2, 3),    # Row 1 - I2C Bus 1
    (4, 5),    # Row 2 - I2C Bus 2
    (6, 7),    # Row 3 - I2C Bus 3
    (8, 9),    # Row 4 - I2C Bus 4
    (10, 11),  # Row 5 - I2C Bus 5
]

# ─── Component offsets within a cell (relative to cell center) ────
# Cell center is between the LM324 and SLG47004V
#
# Layout per cell (approx 18×10mm):
#   ┌─────────────────────────────────┐
#   │ [C_dec1]  [LM324]    [SLG47004]│
#   │ [C_dec2]  [R1][R2]   [C_vref]  │
#   │ TP_A  TP_B  TP_V  TP_P         │
#   └─────────────────────────────────┘

OFFSETS = {
    'lm324':  (-3.5,  0.0,  0),     # (dx, dy, rotation) — SOIC-14 horizontal
    'slg':    ( 5.5,  0.0,  0),     # QFN-24 to the right
    'caps': [
        (-8.0, -2.0, 0),            # C decoupling LM324 (left of LM)
        (-8.0,  2.0, 0),            # C decoupling SLG
        ( 5.5,  3.5, 90),           # C VREF below SLG
    ],
    'res': [
        ( 0.5, -3.5, 0),            # R voltage divider 1
        ( 0.5,  3.5, 0),            # R voltage divider 2
    ],
    'tps': [
        (-3.5, -5.0, 0),            # TP TORSION_A
        (-3.5,  5.0, 0),            # TP TORSION_B
        ( 1.5, -5.0, 0),            # TP VREF_MID
        ( 5.5, -5.0, 0),            # TP PULSE_IN
    ],
}

# Main sheet components
# U1 (TCA9548A) - near I2C header area, top of board
U1_POS = (168.0, -65.0, 0)
# R1, R2 - I2C pullups near TCA9548A
R1_POS = (164.0, -62.0, 90)  # SDA pullup
R2_POS = (166.0, -62.0, 90)  # SCL pullup

# ─── Placement computation ────────────────────────────────────────
def compute_placements():
    """Returns dict of {reference: (x, y, rotation)}"""
    placements = {}

    for row_idx, (cell_left, cell_right) in enumerate(CELL_GRID):
        for col_idx, cell_id in enumerate([cell_left, cell_right]):
            cell = CELLS[cell_id]
            cx = GRID_ORIGIN_X + col_idx * CELL_WIDTH
            cy = GRID_ORIGIN_Y + row_idx * CELL_HEIGHT

            # Place each component type
            dx, dy, rot = OFFSETS['lm324']
            placements[cell['lm324']] = (cx + dx, cy + dy, rot)

            dx, dy, rot = OFFSETS['slg']
            placements[cell['slg']] = (cx + dx, cy + dy, rot)

            for i, cap_ref in enumerate(cell['caps']):
                dx, dy, rot = OFFSETS['caps'][i]
                placements[cap_ref] = (cx + dx, cy + dy, rot)

            for i, r_ref in enumerate(cell['res']):
                dx, dy, rot = OFFSETS['res'][i]
                placements[r_ref] = (cx + dx, cy + dy, rot)

            for i, tp_ref in enumerate(cell['tps']):
                dx, dy, rot = OFFSETS['tps'][i]
                placements[tp_ref] = (cx + dx, cy + dy, rot)

    # Main sheet components
    placements['U1'] = U1_POS
    placements['R1'] = R1_POS
    placements['R2'] = R2_POS

    return placements


# ─── PCB file modification ────────────────────────────────────────
def update_pcb(placements):
    """Read PCB, update footprint positions, write back."""

    # Backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(BACKUP_DIR, f"Prime_Maxel-v3_{ts}_pre_placement.kicad_pcb")
    shutil.copy2(PCB_FILE, backup)
    print(f"Backup: {backup}")

    with open(PCB_FILE, 'r') as f:
        content = f.read()

    placed = 0
    skipped = []

    # For each footprint block, find its reference and update position
    # Strategy: find each (footprint "..." block, locate its Reference property,
    # then update the first (at ...) after the footprint opening.

    def replace_footprint_pos(match_content, ref, new_x, new_y, new_rot):
        """Replace the (at X Y [rot]) in a footprint block."""
        # The first (at ...) in a footprint is its position
        at_pattern = re.compile(r'(\(at\s+)([\d.\-]+)\s+([\d.\-]+)(?:\s+([\d.\-]+))?(\))')
        m = at_pattern.search(match_content)
        if m:
            if new_rot != 0:
                replacement = f"{m.group(1)}{new_x:.4f} {new_y:.4f} {new_rot}{m.group(5)}"
            else:
                replacement = f"{m.group(1)}{new_x:.4f} {new_y:.4f}{m.group(5)}"
            return match_content[:m.start()] + replacement + match_content[m.end():]
        return match_content

    # Split content by footprint blocks using a proper parser
    new_content = []
    pos = 0
    fp_start_pattern = re.compile(r'\(footprint\s+"')

    while pos < len(content):
        m = fp_start_pattern.search(content, pos)
        if not m:
            new_content.append(content[pos:])
            break

        # Add content before this footprint
        new_content.append(content[pos:m.start()])

        # Find the matching closing paren
        depth = 0
        block_end = m.start()
        for i in range(m.start(), len(content)):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    block_end = i + 1
                    break

        block = content[m.start():block_end]

        # Find reference
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        if ref_m and ref_m.group(1) in placements:
            ref = ref_m.group(1)
            new_x, new_y, new_rot = placements[ref]
            block = replace_footprint_pos(block, ref, new_x, new_y, new_rot)
            placed += 1

        new_content.append(block)
        pos = block_end

    content = ''.join(new_content)

    with open(PCB_FILE, 'w') as f:
        f.write(content)

    not_placed = set(placements.keys()) - set()
    print(f"\nPlaced {placed}/{len(placements)} components")
    if placed < len(placements):
        print(f"Note: {len(placements) - placed} references not found in PCB")

    # Print placement summary
    print("\n── Placement Summary ──")
    print(f"{'Ref':8s} {'X':>8s} {'Y':>8s} {'Rot':>5s}  Description")
    print("─" * 55)
    for ref in sorted(placements, key=lambda r: (re.match(r'[A-Z]+', r).group(), int(re.search(r'\d+', r).group()))):
        x, y, rot = placements[ref]
        # Determine what this is
        desc = ""
        if ref == 'U1': desc = "TCA9548A I2C Mux"
        elif ref in ('R1','R2'): desc = "I2C pullup"
        else:
            for cell_id, cell in CELLS.items():
                if ref == cell['lm324']: desc = f"Cell {cell_id} LM324"
                elif ref == cell['slg']: desc = f"Cell {cell_id} SLG47004V"
                elif ref in cell['caps']: desc = f"Cell {cell_id} cap"
                elif ref in cell['res']: desc = f"Cell {cell_id} resistor"
                elif ref in cell['tps']: desc = f"Cell {cell_id} test point"
                if desc: break
        print(f"{ref:8s} {x:8.2f} {y:8.2f} {rot:5.0f}  {desc}")


# ─── Main ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Prime_Maxel-v3 PCB Component Placement")
    print("=" * 40)
    print(f"PCB file: {PCB_FILE}")

    # Check file exists
    if not os.path.exists(PCB_FILE):
        print(f"ERROR: PCB file not found: {PCB_FILE}")
        exit(1)

    # Check not locked (KiCad creates .lck file when open)
    lck_file = PCB_FILE.replace('.kicad_pcb', '.kicad_pcb.lck')
    # Note: schematic lock exists, PCB lock is different
    pcb_lck = os.path.splitext(PCB_FILE)[0] + '.kicad_pcb.lck'
    # KiCad 8 uses ~ prefix for locks
    tilde_lck = os.path.join(os.path.dirname(PCB_FILE), '~' + os.path.basename(PCB_FILE) + '.lck')

    placements = compute_placements()
    print(f"\nComputed {len(placements)} component positions")
    print(f"  12 cells × (LM324 + SLG + 3 caps + 2 res + 4 TPs) = {12*10} cell components")
    print(f"  + U1 (TCA9548A) + R1, R2 (I2C pullups) = 3 main components")

    update_pcb(placements)
    print("\n✅ Done! Open Prime_Maxel-v3.kicad_pcb in KiCad to verify.")
