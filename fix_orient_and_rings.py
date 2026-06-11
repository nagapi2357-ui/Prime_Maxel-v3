#!/usr/bin/env python3
"""
Fix #1: Correct tangential orientation for 8 'obtuse' cell pairs.
Fix #2: Move torsion rings to inner (29.7mm) / outer (58.0mm) radii with radial arms.
"""

import re, math, uuid
from pathlib import Path

PCB_PATH = Path("/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/"
                "Prime_Maxel-v3-2026-02-22_190839/Prime_Maxel-v3.kicad_pcb")

CX, CY = 150.0, 105.0
R_SLG = 39.41935
R_LM324 = 46.41882

# New ring radii from Adrian's reference points
# TORSION_A at (129.5, 126.5) → r = 29.71mm (INSIDE components)
# TORSION_B at (109, 146) → r = 57.98mm (OUTSIDE components)
R_RING_A = 29.71
R_RING_B = 57.98

# Via geometry (from reference cell at 135°)
R_VIA_A = 49.64
R_VIA_B = 49.73
VIA_A_OFFSET = 9.92   # degrees from cell angle
VIA_B_OFFSET = -10.46

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

def gen_uuid():
    return str(uuid.uuid4())

def normalize_angle(a):
    while a > 180: a -= 360
    while a <= -180: a += 360
    return a

def polar_to_xy(r, angle_deg):
    rad = math.radians(angle_deg)
    return CX + r * math.cos(rad), CY + r * math.sin(rad)

def compute_tangential_orient(cell_angle_deg):
    """
    For SOIC-14 (LM324) and QFN-24 (SLG47004V) footprints:
    - At orient=0°, SOIC long axis is VERTICAL (90° screen angle)
    - Global long axis angle = 90° - orient
    - For tangential: long axis = cell_angle ± 90°
    
    Two valid orientations (180° apart):
      A = 180° - cell_angle  (long axis = cell_angle - 90°)
      B = -cell_angle         (long axis = cell_angle + 90°)
    
    Pick the one closest to (cell_angle - 90°) for visual consistency
    with the reference cell U4/U5.
    """
    theta = cell_angle_deg
    ref = normalize_angle(theta - 90.0)  # what my old formula gave
    
    opt_a = normalize_angle(180.0 - theta)
    opt_b = normalize_angle(-theta)
    
    # Distance on the angle circle
    def angle_dist(a, b):
        d = abs(normalize_angle(a - b))
        return d
    
    if angle_dist(opt_a, ref) <= angle_dist(opt_b, ref):
        return opt_a
    else:
        return opt_b

def update_footprint_position(content, ref, new_x, new_y, new_angle):
    ref_pattern = re.compile(r'\(property\s+"Reference"\s+"' + re.escape(ref) + r'"')
    ref_match = ref_pattern.search(content)
    if not ref_match:
        print(f"  WARNING: Could not find reference {ref}")
        return content
    
    fp_start = content.rfind('(footprint ', 0, ref_match.start())
    if fp_start == -1:
        return content
    
    fp_section = content[fp_start:ref_match.start()]
    at_match = re.search(r'\(at\s+[\d.\-]+\s+[\d.\-]+(?:\s+[\d.\-]+)?\)', fp_section)
    if not at_match:
        return content
    
    at_start = fp_start + at_match.start()
    at_end = fp_start + at_match.end()
    
    new_at = f"(at {new_x:.6f} {new_y:.6f} {new_angle:.1f})"
    content = content[:at_start] + new_at + content[at_end:]
    return content

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

def make_segment(sx, sy, ex, ey, width, layer, net):
    uid = gen_uuid()
    return f"""\t(segment
\t\t(start {sx:.6f} {sy:.6f})
\t\t(end {ex:.6f} {ey:.6f})
\t\t(width {width})
\t\t(layer "{layer}")
\t\t(net {net})
\t\t(uuid "{uid}")
\t)"""

def main():
    print("Reading PCB file...")
    content = PCB_PATH.read_text()
    
    # ============================================================
    # FIX 1: Correct tangential orientations for all 12 cells
    # ============================================================
    print("\n=== Fix 1: Correcting component orientations ===")
    
    reference_idx = 0  # U4/U5 at 135° — don't touch
    
    for i, (slg_ref, lm_ref, angle) in enumerate(CELLS):
        new_orient = compute_tangential_orient(angle)
        
        if i == reference_idx:
            print(f"  Cell {i+1} ({slg_ref}/{lm_ref}) at {angle}°: orient={new_orient:.1f}° — REFERENCE, skipping")
            continue
        
        # Check if orientation needs updating
        # Get current orient from file
        sx, sy = polar_to_xy(R_SLG, angle)
        lx, ly = polar_to_xy(R_LM324, angle)
        
        content = update_footprint_position(content, slg_ref, sx, sy, new_orient)
        content = update_footprint_position(content, lm_ref, lx, ly, new_orient)
        print(f"  Cell {i+1} ({slg_ref}/{lm_ref}) at {angle}°: orient={new_orient:.1f}°")
    
    # ============================================================
    # FIX 2: Remove old torsion ring arcs, create new rings + arms
    # ============================================================
    print("\n=== Fix 2: Rebuilding torsion rings ===")
    
    # Remove ALL arc segments (they were all torsion ring arcs we added)
    old_arc_count = len(re.findall(r'\t\(arc\n', content))
    content = re.sub(r'\t\(arc\n\t\t.*?\n\t\t.*?\n\t\t.*?\n\t\t.*?\n\t\t.*?\n\t\t.*?\n\t\t.*?\n\t\)', '', content, flags=re.DOTALL)
    print(f"  Removed {old_arc_count} old ring arcs")
    
    # Remove the 22 torsion vias we added (keep the 2 original ones for cell 1)
    # Original vias: (109.38, 133.53) net 95 and (121.8, 145.96) net 96
    # Strategy: remove vias on net 95/96 that are NOT the originals
    via_pattern = re.compile(
        r'\t\(via\n\t\t\(at\s+([\d.\-]+)\s+([\d.\-]+)\)\n\t\t\(size\s+[\d.]+\)\n\t\t\(drill\s+[\d.]+\)\n'
        r'\t\t\(layers\s+"F\.Cu"\s+"B\.Cu"\)\n\t\t\(net\s+(95|96)\)\n\t\t\(uuid\s+"[^"]+"\)\n\t\)'
    )
    
    def via_replacer(match):
        x, y = float(match.group(1)), float(match.group(2))
        # Keep original cell 1 vias
        if abs(x - 109.38) < 0.01 and abs(y - 133.53) < 0.01:
            return match.group(0)  # keep
        if abs(x - 121.8) < 0.01 and abs(y - 145.96) < 0.01:
            return match.group(0)  # keep
        return ''  # remove
    
    content = via_pattern.sub(via_replacer, content)
    print("  Removed non-reference torsion vias")
    
    # Compute via positions for all 12 cells
    new_elements = []
    ring_a_points = []  # (x, y, angle) for TORSION_A ring
    ring_b_points = []
    
    for i, (slg_ref, lm_ref, angle) in enumerate(CELLS):
        via_a_angle = angle + VIA_A_OFFSET
        via_b_angle = angle + VIA_B_OFFSET
        
        va_x, va_y = polar_to_xy(R_VIA_A, via_a_angle)
        vb_x, vb_y = polar_to_xy(R_VIA_B, via_b_angle)
        
        ring_a_points.append((va_x, va_y, via_a_angle))
        ring_b_points.append((vb_x, vb_y, via_b_angle))
        
        # Add vias for cells 2-12 (cell 1 already has them)
        if i != reference_idx:
            uid_a = gen_uuid()
            new_elements.append(f"""\t(via
\t\t(at {va_x:.6f} {va_y:.6f})
\t\t(size 0.6)
\t\t(drill 0.3)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net 95)
\t\t(uuid "{uid_a}")
\t)""")
            uid_b = gen_uuid()
            new_elements.append(f"""\t(via
\t\t(at {vb_x:.6f} {vb_y:.6f})
\t\t(size 0.6)
\t\t(drill 0.3)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net 96)
\t\t(uuid "{uid_b}")
\t)""")
    
    print(f"  Added 22 torsion vias")
    
    # Create TORSION_A ring arcs at R_RING_A = 29.71mm
    ra_sorted = sorted(ring_a_points, key=lambda p: p[2] % 360)
    for i in range(len(ra_sorted)):
        j = (i + 1) % len(ra_sorted)
        # Arc on the INNER ring connecting consecutive radial arm landing points
        # The arc goes between the angles where the radial arms meet the ring
        ang1 = ra_sorted[i][2]
        ang2 = ra_sorted[j][2]
        if ang2 < ang1:
            ang2 += 360
        mid_ang = (ang1 + ang2) / 2.0
        
        sx, sy = polar_to_xy(R_RING_A, ang1)
        ex, ey = polar_to_xy(R_RING_A, ang2)
        mx, my = polar_to_xy(R_RING_A, mid_ang)
        
        new_elements.append(make_arc(sx, sy, mx, my, ex, ey, 0.229, "F.Cu", 95))
    
    print(f"  Created 12 TORSION_A ring arcs at r={R_RING_A}mm")
    
    # Create TORSION_B ring arcs at R_RING_B = 57.98mm
    rb_sorted = sorted(ring_b_points, key=lambda p: p[2] % 360)
    for i in range(len(rb_sorted)):
        j = (i + 1) % len(rb_sorted)
        ang1 = rb_sorted[i][2]
        ang2 = rb_sorted[j][2]
        if ang2 < ang1:
            ang2 += 360
        mid_ang = (ang1 + ang2) / 2.0
        
        sx, sy = polar_to_xy(R_RING_B, ang1)
        ex, ey = polar_to_xy(R_RING_B, ang2)
        mx, my = polar_to_xy(R_RING_B, mid_ang)
        
        new_elements.append(make_arc(sx, sy, mx, my, ex, ey, 0.229, "F.Cu", 96))
    
    print(f"  Created 12 TORSION_B ring arcs at r={R_RING_B}mm")
    
    # Create radial arm traces (straight segments from via to ring)
    for i, (slg_ref, lm_ref, angle) in enumerate(CELLS):
        va_x, va_y, va_ang = ring_a_points[i]
        vb_x, vb_y, vb_ang = ring_b_points[i]
        
        # TORSION_A arm: from via (outer) radially inward to ring
        ring_a_x, ring_a_y = polar_to_xy(R_RING_A, va_ang)
        new_elements.append(make_segment(va_x, va_y, ring_a_x, ring_a_y, 0.229, "F.Cu", 95))
        
        # TORSION_B arm: from via (inner) radially outward to ring
        ring_b_x, ring_b_y = polar_to_xy(R_RING_B, vb_ang)
        new_elements.append(make_segment(vb_x, vb_y, ring_b_x, ring_b_y, 0.229, "F.Cu", 96))
    
    print(f"  Created 24 radial arm traces (12 TORSION_A + 12 TORSION_B)")
    
    # Insert new elements before closing paren
    insert_text = "\n".join(new_elements) + "\n"
    last_paren = content.rstrip().rfind(')')
    content = content[:last_paren] + insert_text + content[last_paren:]
    
    # Clean up any double blank lines from removals
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Write output
    print(f"\nWriting modified PCB...")
    PCB_PATH.write_text(content)
    print(f"Done! Modified: {PCB_PATH}")
    
    # Print orientation summary
    print(f"\n=== Orientation Summary ===")
    for i, (slg_ref, lm_ref, angle) in enumerate(CELLS):
        orient = compute_tangential_orient(angle)
        old = normalize_angle(angle - 90)
        changed = "✓ fixed" if abs(orient - old) > 0.1 else "  (unchanged)"
        ref_mark = " ← REFERENCE" if i == 0 else ""
        print(f"  {angle:>3}° → orient {orient:>7.1f}°  (was {old:>7.1f}°)  {changed}{ref_mark}")
    
    print(f"\n=== Ring Summary ===")
    print(f"  TORSION_A ring: r={R_RING_A}mm (INSIDE components)")
    print(f"  TORSION_B ring: r={R_RING_B}mm (OUTSIDE components)")
    print(f"  Component zone: SLG at {R_SLG:.1f}mm, LM324 at {R_LM324:.1f}mm")
    print(f"  Radial arms: 0.229mm width on F.Cu")

if __name__ == "__main__":
    main()
