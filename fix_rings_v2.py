#!/usr/bin/env python3
"""
Fix v2: 
1. Remove old torsion ring arcs (at ~49.6mm radius)
2. Create new TORSION_A ring at ~29.7mm (inside components)  
3. Create new TORSION_B ring at ~58.0mm (outside components)
4. Add radial arm traces from each ring to each cell's torsion via
"""

import re, math, uuid
from pathlib import Path

PCB_PATH = Path("/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/"
                "Prime_Maxel-v3-2026-02-22_190839/Prime_Maxel-v3.kicad_pcb")

CX, CY = 150.0, 105.0

# New ring radii from Adrian's reference points
R_RING_A = 29.71   # TORSION_A inner ring (from point 129.5, 126.5)
R_RING_B = 57.98   # TORSION_B outer ring (from point 109, 146)

# Existing via geometry (from reference cell at 135°)
R_VIA_A = 49.64     # TORSION_A vias at this radius
R_VIA_B = 49.73     # TORSION_B vias at this radius
VIA_A_OFFSET = 9.92  # degrees from cell angle
VIA_B_OFFSET = -10.46

# Cell angles
CELL_ANGLES = [135, 105, 75, 45, 15, 345, 315, 285, 255, 225, 195, 165]

def polar_to_xy(r, angle_deg):
    rad = math.radians(angle_deg)
    return CX + r * math.cos(rad), CY + r * math.sin(rad)

def gen_uuid():
    return str(uuid.uuid4())

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
    
    # --- Step 1: Remove old arc segments (my previous ring arcs) ---
    # These are all (arc ...) blocks — the original PCB had 0 arcs, I added 24
    old_arc_count = len(re.findall(r'\t\(arc\n', content))
    print(f"Removing {old_arc_count} old arc segments...")
    content = re.sub(r'\t\(arc\n\t\t\(start .*?\n\t\t\(mid .*?\n\t\t\(end .*?\n\t\t\(width .*?\n\t\t\(layer .*?\n\t\t\(net .*?\n\t\t\(uuid .*?\n\t\)\n?', '', content, flags=re.DOTALL)
    
    # Verify removal
    remaining_arcs = len(re.findall(r'\(arc\s', content))
    print(f"  Arcs remaining: {remaining_arcs}")
    
    # --- Step 2: Create new ring arcs ---
    print("\n=== Creating new torsion rings ===")
    new_elements = []
    
    # Sort cell angles for ring connectivity
    sorted_angles = sorted(CELL_ANGLES)  # 15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345
    
    # TORSION_A inner ring (radius ~29.7mm)
    # The ring connects points at the intersection of each radial arm with the ring
    # Radial arm direction = same as via angle from center
    ring_a_points = []
    for cell_ang in sorted_angles:
        via_ang = cell_ang + VIA_A_OFFSET
        # Ring point is where the radial arm from the via hits the ring
        rx, ry = polar_to_xy(R_RING_A, via_ang)
        ring_a_points.append((rx, ry, via_ang))
    
    for i in range(len(ring_a_points)):
        j = (i + 1) % len(ring_a_points)
        sx, sy, a1 = ring_a_points[i]
        ex, ey, a2 = ring_a_points[j]
        if a2 < a1:
            a2 += 360
        mid_ang = (a1 + a2) / 2.0
        mx, my = polar_to_xy(R_RING_A, mid_ang)
        new_elements.append(make_arc(sx, sy, mx, my, ex, ey, 0.229, "F.Cu", 95))
    
    print(f"  TORSION_A ring: 12 arcs at r={R_RING_A:.1f}mm")
    
    # TORSION_B outer ring (radius ~58mm)
    ring_b_points = []
    for cell_ang in sorted_angles:
        via_ang = cell_ang + VIA_B_OFFSET
        rx, ry = polar_to_xy(R_RING_B, via_ang)
        ring_b_points.append((rx, ry, via_ang))
    
    for i in range(len(ring_b_points)):
        j = (i + 1) % len(ring_b_points)
        sx, sy, a1 = ring_b_points[i]
        ex, ey, a2 = ring_b_points[j]
        if a2 < a1:
            a2 += 360
        mid_ang = (a1 + a2) / 2.0
        mx, my = polar_to_xy(R_RING_B, mid_ang)
        new_elements.append(make_arc(sx, sy, mx, my, ex, ey, 0.229, "F.Cu", 96))
    
    print(f"  TORSION_B ring: 12 arcs at r={R_RING_B:.1f}mm")
    
    # --- Step 3: Create radial arm traces ---
    print("\n=== Creating radial arm traces ===")
    
    for cell_ang in CELL_ANGLES:
        # TORSION_A: arm from inner ring outward to via
        via_ang_a = cell_ang + VIA_A_OFFSET
        vx_a, vy_a = polar_to_xy(R_VIA_A, via_ang_a)  # via position
        rx_a, ry_a = polar_to_xy(R_RING_A, via_ang_a)  # ring point
        new_elements.append(make_segment(rx_a, ry_a, vx_a, vy_a, 0.229, "F.Cu", 95))
        
        # TORSION_B: arm from outer ring inward to via
        via_ang_b = cell_ang + VIA_B_OFFSET
        vx_b, vy_b = polar_to_xy(R_VIA_B, via_ang_b)  # via position
        rx_b, ry_b = polar_to_xy(R_RING_B, via_ang_b)  # ring point
        new_elements.append(make_segment(rx_b, ry_b, vx_b, vy_b, 0.229, "F.Cu", 96))
    
    print(f"  Created {len(CELL_ANGLES) * 2} radial arm traces (12 TORSION_A + 12 TORSION_B)")
    
    # --- Insert new elements ---
    insert_text = "\n".join(new_elements) + "\n"
    last_paren = content.rstrip().rfind(')')
    content = content[:last_paren] + insert_text + content[last_paren:]
    
    # --- Write ---
    print(f"\nWriting modified PCB...")
    PCB_PATH.write_text(content)
    print(f"Done!")
    
    print(f"\n=== Summary ===")
    print(f"  Removed: {old_arc_count} old ring arcs")
    print(f"  Added: 24 new ring arcs (12 inner + 12 outer)")
    print(f"  Added: 24 radial arm traces")
    print(f"  TORSION_A inner ring: r={R_RING_A:.1f}mm")
    print(f"  TORSION_B outer ring: r={R_RING_B:.1f}mm")
    print(f"  Existing torsion vias unchanged (at ~{R_VIA_A:.0f}mm radius)")

if __name__ == "__main__":
    main()
