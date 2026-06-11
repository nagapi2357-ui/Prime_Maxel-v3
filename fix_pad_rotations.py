#!/usr/bin/env python3
"""
Fix pad local rotations to match current footprint orientation.
In these custom Adrian footprints, pad_local_rot must equal footprint_orient
for correct visual alignment (matching reference cell U4/U5 pattern).
"""

import re
from pathlib import Path

PCB_PATH = Path("/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/"
                "Prime_Maxel-v3-2026-02-22_190839/Prime_Maxel-v3.kicad_pcb")

# All golden cell U refs (skip U1 = TCA9548A, skip U4/U5 = reference)
REFS_TO_FIX = [f'U{n}' for n in range(2, 26) if n not in (4, 5)]

def normalize_angle(a):
    while a > 180: a -= 360
    while a <= -180: a += 360
    return a

def main():
    print("Reading PCB file...")
    content = PCB_PATH.read_text()
    
    for ref_name in REFS_TO_FIX:
        ref_pos = content.find(f'"Reference" "{ref_name}"')
        if ref_pos < 0:
            print(f"  WARNING: {ref_name} not found")
            continue
        
        fp_start = content.rfind('(footprint ', 0, ref_pos)
        fp_end = content.find('\n\t(footprint ', fp_start + 1)
        if fp_end < 0:
            fp_end = content.find('\n\t(segment', fp_start)
        if fp_end < 0:
            fp_end = content.find('\n\t(arc', fp_start)
        if fp_end < 0:
            fp_end = content.find('\n\t(via', fp_start)
        if fp_end < 0:
            fp_end = len(content)
        
        block = content[fp_start:fp_end]
        
        # Get footprint orient
        fp_at = re.search(r'\(at\s+([\d.\-]+)\s+([\d.\-]+)(?:\s+([\d.\-]+))?\)', block)
        if not fp_at:
            continue
        fp_orient = float(fp_at.group(3)) if fp_at.group(3) else 0.0
        
        # Get current pad rotation (first pad)
        pad_rot_match = re.search(r'\(pad\s+"\d+"\s+\w+\s+\w+\s+\(at\s+[\d.\-]+\s+[\d.\-]+(?:\s+([\d.\-]+))?\)', block)
        old_pad_rot = float(pad_rot_match.group(1)) if pad_rot_match and pad_rot_match.group(1) else 0.0
        
        if abs(normalize_angle(old_pad_rot - fp_orient)) < 0.1:
            print(f"  {ref_name}: pad_rot={old_pad_rot:.1f}° = fp_orient={fp_orient:.1f}° → already correct")
            continue
        
        # Replace all pad rotations in this footprint block
        # Pattern: (pad "N" smd/thru_hole rect/... (at X Y ANGLE) ...)
        # We need to replace the ANGLE part in each pad's (at ...) within this block
        
        new_pad_rot = fp_orient
        # Normalize to match KiCad's format
        new_pad_rot_str = f"{new_pad_rot:.1f}" if new_pad_rot != int(new_pad_rot) else f"{int(new_pad_rot)}"
        
        # Count replacements
        count = 0
        
        def replace_pad_rot(match):
            nonlocal count
            count += 1
            prefix = match.group(1)
            # Replace the angle
            return f'{prefix}{new_pad_rot}'
        
        # Replace pad (at X Y OLD_ANGLE) with (at X Y NEW_ANGLE)
        # Only within this footprint block
        new_block = re.sub(
            r'(\(pad\s+"[^"]+"\s+\w+\s+\w+\s+\(at\s+[\d.\-]+\s+[\d.\-]+\s+)[\d.\-]+',
            replace_pad_rot,
            block
        )
        
        content = content[:fp_start] + new_block + content[fp_end:]
        
        # Adjust fp_end for content length changes
        delta = len(new_block) - len(block)
        
        print(f"  {ref_name}: pad_rot {old_pad_rot:.1f}° → {new_pad_rot:.1f}° ({count} pads updated)")
    
    # Validate
    depth = 0
    for ch in content:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
    
    if depth != 0:
        print(f"\nERROR: Unbalanced parentheses (depth={depth})")
        return
    
    print(f"\nParentheses balanced ✓")
    print(f"Writing modified PCB...")
    PCB_PATH.write_text(content)
    print(f"Done!")

if __name__ == "__main__":
    main()
