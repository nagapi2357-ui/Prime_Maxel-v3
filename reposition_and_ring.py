#!/usr/bin/env python3
"""
Reposition 11 golden cell U pairs to match U4/U5 reference cell,
add torsion vias for all 12 cells, and create torsion ring arc traces.
"""

import re, math, uuid, sys, shutil
from pathlib import Path

PCB_PATH = Path("/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/"
                "Prime_Maxel-v3-2026-02-22_190839/Prime_Maxel-v3.kicad_pcb")

# Board geometry
CX, CY = 150.0, 105.0  # Board center

# Reference cell (U4/U5) at math angle 135°
REF_ANGLE = 135.0  # degrees, math convention (CCW from +X, Y-up in math = Y-down in KiCad)

# Radii computed from reference cell positions
R_SLG = 39.41935    # inner ring (SLG47004V) - computed from U5
R_LM324 = 46.41882  # outer ring (LM324DRE4) - computed from U4

# Torsion via geometry (from reference cell)
# TORSION_A via at (109.38, 133.53): r=49.64, angle=144.92° → offset +9.92° from cell
# TORSION_B via at (121.8, 145.96): r=49.73, angle=124.54° → offset -10.46° from cell
R_TORSION_A = 49.64
R_TORSION_B = 49.73
TORSION_A_OFFSET = 9.92   # degrees CCW from cell angle
TORSION_B_OFFSET = -10.46  # degrees CW from cell angle

# Cell definitions: (SLG_ref, LM324_ref, math_angle_degrees)
CELLS = [
    ("U5",  "U4",  135),
    ("U3",  "U2",  105),
    ("U25", "U24", 75),
    ("U23", "U22", 45),
    ("U21", "U20", 15),
    ("U19", "U18", 345),
    ("U17", "U16", 315),
    ("U15", "U14", 285),
    ("U13", "U12", 255),
    ("U11", "U10", 225),
    ("U9",  "U8",  195),
    ("U7",  "U6",  165),
]

REFERENCE_CELL = 0  # index into CELLS (U4/U5)

def polar_to_xy(r, angle_deg):
    """Convert polar (from board center) to KiCad coords. 
    Math convention: angle CCW from +X, but KiCad Y is down so sin is positive for 'down'."""
    rad = math.radians(angle_deg)
    return CX + r * math.cos(rad), CY + r * math.sin(rad)

def kicad_orientation(cell_angle_deg):
    """Compute KiCad footprint orientation for tangential alignment.
    From reference: cell at 135° → KiCad orientation 45° → offset = -90°"""
    return cell_angle_deg - 90.0

def normalize_angle(a):
    """Normalize angle to (-180, 180]"""
    while a > 180: a -= 360
    while a <= -180: a += 360
    return a

def gen_uuid():
    return str(uuid.uuid4())

def update_footprint_position(content, ref, new_x, new_y, new_angle):
    """Update the (at x y angle) of a footprint with given reference."""
    # Find the footprint block containing this reference
    # Strategy: find (property "Reference" "Uxx") and then find the (at ...) before it
    
    # Find all footprint starts
    pattern = re.compile(
        r'(\(footprint\s+"[^"]+"\s*\n\s*\(layer\s+"[^"]+"\)\s*\n\s*\(uuid\s+"[^"]+"\)\s*\n\s*)'
        r'\(at\s+[\d.\-]+\s+[\d.\-]+(?:\s+[\d.\-]+)?\)'
    )
    
    # We need to match the right footprint. Find position of reference property.
    ref_pattern = re.compile(r'\(property\s+"Reference"\s+"' + re.escape(ref) + r'"')
    ref_match = ref_pattern.search(content)
    if not ref_match:
        print(f"WARNING: Could not find reference {ref}")
        return content
    
    ref_pos = ref_match.start()
    
    # Find the footprint block start before this reference
    # Look backwards for "(footprint "
    fp_start = content.rfind('(footprint ', 0, ref_pos)
    if fp_start == -1:
        print(f"WARNING: Could not find footprint block for {ref}")
        return content
    
    # Find the (at ...) within this footprint block (should be near the start)
    fp_section = content[fp_start:ref_pos]
    at_match = re.search(r'\(at\s+[\d.\-]+\s+[\d.\-]+(?:\s+[\d.\-]+)?\)', fp_section)
    if not at_match:
        print(f"WARNING: Could not find (at ...) for {ref}")
        return content
    
    at_start = fp_start + at_match.start()
    at_end = fp_start + at_match.end()
    
    new_angle_norm = normalize_angle(new_angle)
    new_at = f"(at {new_x:.6f} {new_y:.6f} {new_angle_norm:.1f})"
    
    content = content[:at_start] + new_at + content[at_end:]
    return content

def make_via(x, y, net, size=0.6, drill=0.3):
    uid = gen_uuid()
    return f"""\t(via
\t\t(at {x:.6f} {y:.6f})
\t\t(size {size})
\t\t(drill {drill})
\t\t(layers "F.Cu" "B.Cu")
\t\t(net {net})
\t\t(uuid "{uid}")
\t)"""

def make_arc(sx, sy, mx, my, ex, ey, width, layer, net):
    uid = gen_uuid()
    return f"""\t(arc
\t\t(start {sx:.6f} {sy:.6f})
\t\t(mid {mx:.6f} {my:.6f})
\t\t(end {ex:.6f} {ey:.6f})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net {net})
\t\t(uuid "{uid}")
\t)"""

def main():
    print("Reading PCB file...")
    content = PCB_PATH.read_text()
    
    # --- Step 1: Reposition 11 U pairs ---
    print("\n=== Step 1: Repositioning footprints ===")
    for i, (slg_ref, lm_ref, angle) in enumerate(CELLS):
        if i == REFERENCE_CELL:
            print(f"  Cell {i+1} ({slg_ref}/{lm_ref}) at {angle}° — REFERENCE, skipping")
            continue
        
        # SLG (inner)
        sx, sy = polar_to_xy(R_SLG, angle)
        s_orient = normalize_angle(kicad_orientation(angle))
        content = update_footprint_position(content, slg_ref, sx, sy, s_orient)
        print(f"  {slg_ref} → ({sx:.2f}, {sy:.2f}) orient={s_orient:.1f}°")
        
        # LM324 (outer)
        lx, ly = polar_to_xy(R_LM324, angle)
        l_orient = normalize_angle(kicad_orientation(angle))
        content = update_footprint_position(content, lm_ref, lx, ly, l_orient)
        print(f"  {lm_ref} → ({lx:.2f}, {ly:.2f}) orient={l_orient:.1f}°")
    
    # --- Step 2: Add torsion vias for cells 2-12 ---
    print("\n=== Step 2: Adding torsion vias ===")
    new_vias = []
    via_positions_a = []  # (x, y, cell_angle) for ring routing
    via_positions_b = []
    
    for i, (slg_ref, lm_ref, angle) in enumerate(CELLS):
        # Compute via positions
        ax, ay = polar_to_xy(R_TORSION_A, angle + TORSION_A_OFFSET)
        bx, by = polar_to_xy(R_TORSION_B, angle + TORSION_B_OFFSET)
        
        via_positions_a.append((ax, ay, angle))
        via_positions_b.append((bx, by, angle))
        
        if i == REFERENCE_CELL:
            print(f"  Cell {i+1} at {angle}° — REFERENCE vias already exist")
            print(f"    TORSION_A: ({ax:.2f}, {ay:.2f}) [existing: (109.38, 133.53)]")
            print(f"    TORSION_B: ({bx:.2f}, {by:.2f}) [existing: (121.80, 145.96)]")
            continue
        
        new_vias.append(make_via(ax, ay, 95))  # net 95 = TORSION_A
        new_vias.append(make_via(bx, by, 96))  # net 96 = TORSION_B
        print(f"  Cell {i+1} at {angle}°: A=({ax:.2f},{ay:.2f}) B=({bx:.2f},{by:.2f})")
    
    # --- Step 3: Create ring arcs ---
    print("\n=== Step 3: Creating torsion ring arcs ===")
    new_arcs = []
    
    # Sort via positions by angle for proper ring ordering
    # TORSION_A ring
    va_sorted = sorted(via_positions_a, key=lambda v: v[2])  # sort by cell angle
    for i in range(len(va_sorted)):
        j = (i + 1) % len(va_sorted)
        sx, sy, a1 = va_sorted[i]
        ex, ey, a2 = va_sorted[j]
        
        # Midpoint angle on the TORSION_A ring
        ang1 = a1 + TORSION_A_OFFSET
        ang2 = a2 + TORSION_A_OFFSET
        if ang2 < ang1:
            ang2 += 360
        mid_ang = (ang1 + ang2) / 2.0
        mx, my = polar_to_xy(R_TORSION_A, mid_ang)
        
        arc = make_arc(sx, sy, mx, my, ex, ey, 0.229, "F.Cu", 95)
        new_arcs.append(arc)
    
    # TORSION_B ring
    vb_sorted = sorted(via_positions_b, key=lambda v: v[2])
    for i in range(len(vb_sorted)):
        j = (i + 1) % len(vb_sorted)
        sx, sy, a1 = vb_sorted[i]
        ex, ey, a2 = vb_sorted[j]
        
        ang1 = a1 + TORSION_B_OFFSET
        ang2 = a2 + TORSION_B_OFFSET
        if ang2 < ang1:
            ang2 += 360
        mid_ang = (ang1 + ang2) / 2.0
        mx, my = polar_to_xy(R_TORSION_B, mid_ang)
        
        arc = make_arc(sx, sy, mx, my, ex, ey, 0.229, "F.Cu", 96)
        new_arcs.append(arc)
    
    print(f"  Created {len(new_arcs)} arc segments (12 TORSION_A + 12 TORSION_B)")
    
    # --- Insert new elements into PCB ---
    # Find position to insert (before the closing parenthesis of the PCB)
    # Insert vias and arcs before the last ')' 
    insert_text = "\n".join(new_vias + new_arcs) + "\n"
    
    # Find last ')' in file
    last_paren = content.rstrip().rfind(')')
    content = content[:last_paren] + insert_text + content[last_paren:]
    
    # --- Write output ---
    print(f"\nWriting modified PCB...")
    PCB_PATH.write_text(content)
    print(f"Done! Modified: {PCB_PATH}")
    
    # Print summary
    print(f"\n=== Summary ===")
    print(f"  Repositioned: 22 footprints (11 SLG + 11 LM324)")
    print(f"  Added: {len(new_vias)} vias (11 TORSION_A + 11 TORSION_B)")
    print(f"  Added: {len(new_arcs)} ring arc segments")
    print(f"  Ring radii: TORSION_A={R_TORSION_A:.2f}mm, TORSION_B={R_TORSION_B:.2f}mm")
    print(f"  Track width: 0.229mm (Torsion_Bridge net class)")
    print(f"\n  NOTE: Spoke traces from components to vias are only done for")
    print(f"  the reference cell (U4/U5). Adrian will replicate for others.")

if __name__ == "__main__":
    main()
