#!/usr/bin/env python3
"""
Reposition all 12 golden cells for optimal routing.

Layout per spoke (from center outward):
  SLG (QFN-24) at R=22mm — radial orientation (90° from tangent)
  Cap_SLG at R=20mm — SLG decoupling
  Cap_VCC at R=27mm — VCC decoupling, between SLG and LM324
  LM324 (SOIC-14) at R=30mm — tangential orientation (body parallel to ring)
  Cap_VREF at R=33mm — VREF filter cap
  Res1, Res2 at R=34.5mm — VREF divider resistors, offset tangentially
  TPs at R=38-39.5mm — test points, outermost

Board center: (150, 105)
12 spokes at 30° intervals
Torsion rings: A (outer) ~49mm on B.Cu, B (inner) ~27mm on B.Cu
"""

import re
import math
import sys
import shutil
from datetime import datetime

# ──────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────
CENTER_X = 150.0
CENTER_Y = 105.0

# Radial distances from center (mm)
# Original: LM324 ~39mm, SLG ~52mm, TPs ~56mm
# Torsion rings: B (inner) ~27mm, A (outer) ~49mm
R_LM324 = 39.0        # LM324 between torsion rings (original position)
R_SLG = 52.0           # SLG outside outer ring (original distance)
R_CAP_VCC = 36.0       # VCC decoupling just inside LM324
R_CAP_SLG = 49.0       # SLG decoupling between LM324 and SLG
R_CAP_VREF = 44.0      # VREF cap outside LM324
R_RES1 = 42.0          # VREF divider upper
R_RES2 = 42.0          # VREF divider lower
R_TP_TORSION_A = 57.0
R_TP_TORSION_B = 57.0
R_TP_VREF = 59.0
R_TP_PULSE = 59.0

# Tangential offsets from spoke centerline (mm)
# Positive = clockwise when looking from center outward
TANG_SLG = 0.0
TANG_CAP_SLG = 0.0
TANG_CAP_VCC = 0.0
TANG_LM324 = 0.0
TANG_CAP_VREF = 2.0
TANG_RES1 = -2.0
TANG_RES2 = 2.0
TANG_TP_TORSION_A = -3.0
TANG_TP_TORSION_B = 3.0
TANG_TP_VREF = -3.0
TANG_TP_PULSE = 3.0

# Rotation offsets relative to tangent direction
# tangent = spoke_angle + 90°
# 0 = tangential (body parallel to ring arc)
# -90 = radial (body along spoke, pointing toward center)
ROT_LM324 = 0
ROT_SLG = -90       # Radial: active pins face LM324 direction
ROT_CAP = 0         # Tangential
ROT_RES = 0         # Tangential
ROT_TP = 0          # Tangential

# ──────────────────────────────────────────
# Cell definitions — verified from PCB netlist
# ──────────────────────────────────────────
# Spoke angles in atan2 convention (KiCad: X right, Y down)
# Measured from actual U positions relative to center (150, 105)
CELLS = [
    # (cell, LM324, SLG, spoke_angle,
    #  cap_vcc, cap_slg, cap_vref, res1, res2,
    #  tp_torA, tp_torB, tp_vref, tp_pulse)
    ( 1, 'U2',  'U3',   105.0, 'C2', 'C3', 'C4',  'R3', 'R4',  'TP1','TP2','TP3','TP4'),
    ( 2, 'U4',  'U5',   135.0, 'C5', 'C6', 'C7',  'R5', 'R6',  'TP5','TP6','TP7','TP8'),
    ( 3, 'U6',  'U7',   165.0, 'C8', 'C9', 'C10', 'R7', 'R8',  'TP9','TP10','TP11','TP12'),
    ( 4, 'U8',  'U9',  -165.0, 'C11','C12','C13', 'R9', 'R10', 'TP13','TP14','TP15','TP16'),
    ( 5, 'U10','U11',  -135.0, 'C14','C15','C16', 'R11','R12', 'TP17','TP18','TP19','TP20'),
    ( 6, 'U12','U13',  -105.0, 'C17','C18','C19', 'R13','R14', 'TP21','TP22','TP23','TP24'),
    ( 7, 'U14','U15',   -75.0, 'C20','C21','C22', 'R15','R16', 'TP25','TP26','TP27','TP28'),
    ( 8, 'U16','U17',   -45.0, 'C23','C24','C25', 'R17','R18', 'TP29','TP30','TP31','TP32'),
    ( 9, 'U18','U19',   -15.0, 'C26','C27','C28', 'R19','R20', 'TP33','TP34','TP35','TP36'),
    (10, 'U20','U21',    15.0, 'C29','C30','C31', 'R21','R22', 'TP37','TP38','TP39','TP40'),
    (11, 'U22','U23',    45.0, 'C32','C33','C34', 'R23','R24', 'TP41','TP42','TP43','TP44'),
    (12, 'U24','U25',    75.0, 'C35','C36','C37', 'R25','R26', 'TP45','TP46','TP47','TP48'),
]

# ──────────────────────────────────────────
# Geometry helpers
# ──────────────────────────────────────────
def polar_to_xy(r, spoke_angle_deg, tang_offset=0.0):
    """Convert polar coords to KiCad XY. tang_offset shifts perpendicular to spoke."""
    rad = math.radians(spoke_angle_deg)
    # Tangential direction (perpendicular to radial, 90° CCW in standard math)
    tang_rad = rad + math.pi / 2
    x = CENTER_X + r * math.cos(rad) + tang_offset * math.cos(tang_rad)
    y = CENTER_Y + r * math.sin(rad) + tang_offset * math.sin(tang_rad)
    return round(x, 6), round(y, 6)

def tangent_rotation(spoke_angle_deg, offset_deg=0):
    """KiCad rotation for tangential orientation at a given spoke angle."""
    rot = spoke_angle_deg + 90.0 + offset_deg
    while rot > 180: rot -= 360
    while rot <= -180: rot += 360
    return round(rot, 6)

# ──────────────────────────────────────────
# PCB file manipulation
# ──────────────────────────────────────────
def update_footprint_position(pcb_lines, ref, new_x, new_y, new_rot):
    """Update a footprint's (at x y rot) by reference. Returns modified lines."""
    # Find property Reference line for this ref
    ref_indices = []
    for i, line in enumerate(pcb_lines):
        if f'"Reference" "{ref}"' in line and '(property' in line:
            ref_indices.append(i)

    if not ref_indices:
        print(f"  ⚠ {ref} NOT FOUND")
        return False

    for ref_idx in ref_indices:
        # Search backward for the footprint block start
        fp_start = None
        for j in range(ref_idx, max(ref_idx - 40, 0), -1):
            if '(footprint "' in pcb_lines[j]:
                fp_start = j
                break

        if fp_start is None:
            continue

        # Find the footprint-level (at ...) line (within first few lines of block)
        for j in range(fp_start, min(fp_start + 5, len(pcb_lines))):
            at_match = re.match(r'^(\s+)\(at [\d.eE+-]+ [\d.eE+-]+', pcb_lines[j])
            if at_match:
                indent = at_match.group(1)
                if new_rot == 0:
                    pcb_lines[j] = f'{indent}(at {new_x} {new_y})'
                else:
                    pcb_lines[j] = f'{indent}(at {new_x} {new_y} {new_rot})'
                return True

    print(f"  ⚠ Could not find (at) for {ref}")
    return False

# ──────────────────────────────────────────
# Main
# ──────────────────────────────────────────
def main():
    pcb_path = sys.argv[1] if len(sys.argv) > 1 else 'Prime_Maxel-v3.kicad_pcb'

    print(f"Reading: {pcb_path}")
    with open(pcb_path, 'r') as f:
        lines = f.read().split('\n')

    # Create backup
    backup_path = pcb_path + f'.backup-{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2(pcb_path, backup_path)
    print(f"Backup: {backup_path}")

    total_moves = 0
    total_warnings = 0

    print(f"\n{'='*60}")
    print(f"Repositioning 12 golden cells")
    print(f"Center: ({CENTER_X}, {CENTER_Y})")
    print(f"LM324: R={R_LM324}mm tangential | SLG: R={R_SLG}mm radial")
    print(f"{'='*60}\n")

    for cell in CELLS:
        (cell_num, lm_ref, slg_ref, spoke,
         cap_vcc, cap_slg, cap_vref, res1, res2,
         tp_ta, tp_tb, tp_vr, tp_pu) = cell

        print(f"── Cell {cell_num:2d} ({lm_ref}/{slg_ref}) spoke={spoke:+.0f}° ──")

        placements = [
            (lm_ref,   R_LM324,       TANG_LM324,       ROT_LM324,  "LM324 tangential"),
            (slg_ref,  R_SLG,         TANG_SLG,         ROT_SLG,    "SLG radial"),
            (cap_vcc,  R_CAP_VCC,     TANG_CAP_VCC,     ROT_CAP,    "Cap VCC"),
            (cap_slg,  R_CAP_SLG,     TANG_CAP_SLG,     ROT_CAP,    "Cap SLG"),
            (cap_vref, R_CAP_VREF,    TANG_CAP_VREF,    ROT_CAP,    "Cap VREF"),
            (res1,     R_RES1,        TANG_RES1,        ROT_RES,    "Res upper"),
            (res2,     R_RES2,        TANG_RES2,        ROT_RES,    "Res lower"),
            (tp_ta,    R_TP_TORSION_A,TANG_TP_TORSION_A,ROT_TP,    "TP TORSION_A"),
            (tp_tb,    R_TP_TORSION_B,TANG_TP_TORSION_B,ROT_TP,    "TP TORSION_B"),
            (tp_vr,    R_TP_VREF,     TANG_TP_VREF,     ROT_TP,    "TP VREF"),
            (tp_pu,    R_TP_PULSE,    TANG_TP_PULSE,    ROT_TP,    "TP PULSE"),
        ]

        for ref, radius, tang, rot_offset, desc in placements:
            x, y = polar_to_xy(radius, spoke, tang)
            rot = tangent_rotation(spoke, rot_offset)
            ok = update_footprint_position(lines, ref, x, y, rot)
            if ok:
                print(f"  ✓ {ref:5s} → ({x:8.3f}, {y:8.3f}) rot={rot:+7.1f}°  [{desc}]")
                total_moves += 1
            else:
                total_warnings += 1
        print()

    # Write output
    print(f"{'='*60}")
    print(f"Moves: {total_moves} | Warnings: {total_warnings}")
    print(f"Writing: {pcb_path}")

    with open(pcb_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\n✅ Done! Open in KiCad v9 and:")
    print(f"   1. File → Revert (or re-open the file)")
    print(f"   2. View → Zoom to Fit")
    print(f"   3. Check one spoke visually")
    print(f"   4. Run DRC (Inspect → Design Rules Check)")
    print(f"   5. If courtyard overlaps → we'll adjust radii")

if __name__ == '__main__':
    main()
