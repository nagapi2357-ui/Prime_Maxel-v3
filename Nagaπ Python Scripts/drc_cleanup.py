#!/usr/bin/env python3
"""DRC Cleanup: Remove torsion rings and PULSE_IN star traces on F.Cu."""

import pcbnew
import os
import shutil

BOARD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Prime_Maxel-v3.kicad_pcb')
BACKUP_PATH = BOARD_PATH + '.bak_pre_cleanup'

def main():
    # Backup
    shutil.copy2(BOARD_PATH, BACKUP_PATH)
    print(f"Backup saved to {BACKUP_PATH}")
    
    board = pcbnew.LoadBoard(BOARD_PATH)
    
    total_before = len(board.GetTracks())
    print(f"Tracks before: {total_before}")
    
    to_remove = []
    counts = {'TORSION_A': 0, 'TORSION_B': 0, 'PULSE_F': 0}
    
    for t in board.GetTracks():
        net = t.GetNetname()
        layer = t.GetLayerName()
        
        # Remove ALL torsion traces (rings + stubs) on F.Cu
        if 'TORSION_A' in net and layer == 'F.Cu':
            to_remove.append(t)
            counts['TORSION_A'] += 1
        elif 'TORSION_B' in net and layer == 'F.Cu':
            to_remove.append(t)
            counts['TORSION_B'] += 1
        # Remove torsion vias too
        elif 'TORSION_A' in net and isinstance(t, pcbnew.PCB_VIA):
            to_remove.append(t)
            counts['TORSION_A'] += 1
        elif 'TORSION_B' in net and isinstance(t, pcbnew.PCB_VIA):
            to_remove.append(t)
            counts['TORSION_B'] += 1
        # Remove PULSE_IN star traces on F.Cu only (keep B.Cu J7 route)
        elif 'PULSE_IN' in net and layer == 'F.Cu':
            to_remove.append(t)
            counts['PULSE_F'] += 1
    
    print(f"\nRemoving:")
    print(f"  TORSION_A (F.Cu + vias): {counts['TORSION_A']}")
    print(f"  TORSION_B (F.Cu + vias): {counts['TORSION_B']}")
    print(f"  PULSE_IN (F.Cu only): {counts['PULSE_F']}")
    print(f"  Total: {len(to_remove)}")
    
    for t in to_remove:
        board.Remove(t)
    
    total_after = len(board.GetTracks())
    print(f"\nTracks after: {total_after}")
    
    board.Save(BOARD_PATH)
    print(f"Saved to {BOARD_PATH}")

if __name__ == '__main__':
    main()
