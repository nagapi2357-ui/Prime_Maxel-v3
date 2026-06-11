#!/usr/bin/env python3
"""Route TORSION_A, TORSION_B, PULSE_IN with ring buses on F.Cu,
TP stubs on B.Cu via vias at ring connection points.

Strategy:
- Ring buses: F.Cu (best impedance ref to In1.Cu GND plane)
- Chip pad stubs: F.Cu (SMD pads on F.Cu only)
- TP stubs: B.Cu (TPs are through-hole, via at ring point)
- PULSE_IN to J8: B.Cu (long trace, avoids F.Cu congestion)

Ring radii staggered to avoid inter-net crossings:
  PULSE_IN: r=46mm (innermost)
  TORSION_A: r=48mm
  TORSION_B: r=50mm (outermost)
"""
import pcbnew, math, shutil, os

BOARD_PATH = '/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/Prime_Maxel-v3.kicad_pcb'
BACKUP_PATH = BOARD_PATH + '.pre_torsion_routing.bak'

CX, CY = 150.0, 105.0
TORSION_WIDTH = 0.229  # mm, 50 ohm
VIA_DRILL = 0.3        # mm
VIA_SIZE = 0.6         # mm

RING_R = {
    'PULSE_IN': 46.0,
    'TORSION_A': 48.0,
    'TORSION_B': 50.0,
}

def to_nm(mm):
    return int(mm * 1e6)

def polar(r, angle_deg):
    rad = math.radians(angle_deg)
    return (CX + r * math.cos(rad), CY + r * math.sin(rad))

def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def angle_of(x, y):
    return math.degrees(math.atan2(y - CY, x - CX))

def add_track(board, start, end, width, layer, netcode):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(to_nm(start[0]), to_nm(start[1])))
    t.SetEnd(pcbnew.VECTOR2I(to_nm(end[0]), to_nm(end[1])))
    t.SetWidth(to_nm(width))
    t.SetLayer(layer)
    t.SetNetCode(netcode)
    board.Add(t)

def add_via(board, pos, netcode, size_mm=VIA_SIZE, drill_mm=VIA_DRILL):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(to_nm(pos[0]), to_nm(pos[1])))
    v.SetWidth(to_nm(size_mm))
    v.SetDrill(to_nm(drill_mm))
    v.SetNetCode(netcode)
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    board.Add(v)

def add_arc_tracks(board, r, a_start, a_end, width, layer, netcode, step_deg=3):
    """Add arc segments. Always goes CW (increasing angle)."""
    if a_end < a_start:
        a_end += 360
    points = []
    a = a_start
    while a < a_end - 0.1:
        points.append(polar(r, a % 360))
        a += step_deg
    points.append(polar(r, a_end % 360))
    for i in range(len(points) - 1):
        add_track(board, points[i], points[i+1], width, layer, netcode)

def collect_net_pads(board, net_name):
    pads = []
    for pad in board.GetPads():
        if pad.GetNetname() == net_name:
            pos = pad.GetPosition()
            x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            ref = pad.GetParentAsString()
            pin = pad.GetNumber()
            a = angle_of(x, y)
            r = math.sqrt((x-CX)**2 + (y-CY)**2)
            pads.append({'ref': ref, 'pin': pin, 'x': x, 'y': y, 'angle': a, 'r': r})
    return pads

def group_into_cells(pads):
    u_pads = {}
    tp_pads = {}
    other_pads = []
    for p in pads:
        if p['ref'].startswith('U'):
            u_pads.setdefault(p['ref'], []).append(p)
        elif p['ref'].startswith('TP'):
            tp_pads[p['ref']] = p
        else:
            other_pads.append(p)

    cells = []
    used_tps = set()
    for ref, chip_pads in u_pads.items():
        cell_angle = sum(p['angle'] for p in chip_pads) / len(chip_pads)
        # Find nearest TP
        best_tp = None
        best_diff = 999
        for tp_ref, tp in tp_pads.items():
            if tp_ref in used_tps:
                continue
            diff = abs(tp['angle'] - cell_angle)
            if diff > 180:
                diff = 360 - diff
            if diff < best_diff:
                best_diff = diff
                best_tp = tp_ref
        tp = tp_pads.get(best_tp)
        if best_tp:
            used_tps.add(best_tp)
        cells.append({'ref': ref, 'angle': cell_angle, 'chip_pads': chip_pads, 'tp': tp})

    cells.sort(key=lambda c: c['angle'])
    return cells, other_pads

def route_net(board, net_name, ring_r, fcu, bcu, netcode):
    """Route a complete ring bus with stubs."""
    pads = collect_net_pads(board, net_name)
    cells, other = group_into_cells(pads)
    n = len(cells)
    
    print(f"\n  {net_name}: {n} cells, ring r={ring_r}mm")
    
    # 1. Ring bus on F.Cu (arc between each adjacent cell pair)
    for i in range(n):
        j = (i + 1) % n
        a_start = cells[i]['angle']
        a_end = cells[j]['angle']
        if j == 0:  # wrap around
            a_end += 360
        add_arc_tracks(board, ring_r, a_start, a_end, TORSION_WIDTH, fcu, netcode)
    
    # 2. Per-cell stubs
    for cell in cells:
        ring_pt = polar(ring_r, cell['angle'])
        chip_pads = sorted(cell['chip_pads'], key=lambda p: p['pin'])
        
        # Connect chip pads to each other on F.Cu
        for i in range(len(chip_pads) - 1):
            p1 = (chip_pads[i]['x'], chip_pads[i]['y'])
            p2 = (chip_pads[i+1]['x'], chip_pads[i+1]['y'])
            add_track(board, p1, p2, TORSION_WIDTH, fcu, netcode)
        
        # Connect nearest chip pad to ring point on F.Cu
        nearest = min(chip_pads, key=lambda p: dist((p['x'], p['y']), ring_pt))
        add_track(board, (nearest['x'], nearest['y']), ring_pt, TORSION_WIDTH, fcu, netcode)
        
        # Via at ring point, then route to TP on B.Cu
        if cell['tp']:
            add_via(board, ring_pt, netcode)
            tp_pos = (cell['tp']['x'], cell['tp']['y'])
            add_track(board, ring_pt, tp_pos, TORSION_WIDTH, bcu, netcode)
    
    return cells, other

def main():
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(BOARD_PATH, BACKUP_PATH)
        print(f"Backup: {BACKUP_PATH}")

    board = pcbnew.LoadBoard(BOARD_PATH)
    fcu = board.GetLayerID('F.Cu')
    bcu = board.GetLayerID('B.Cu')
    nets = board.GetNetsByName()

    net_map = {
        '/Golden Cell/TORSION_A': ('TORSION_A', RING_R['TORSION_A']),
        '/Golden Cell/TORSION_B': ('TORSION_B', RING_R['TORSION_B']),
        '/Golden Cell/PULSE_IN': ('PULSE_IN', RING_R['PULSE_IN']),
    }

    print("Routing critical analog signals...")
    for net_name, (label, ring_r) in net_map.items():
        nc = nets[net_name].GetNetCode()
        cells, other = route_net(board, net_name, ring_r, fcu, bcu, nc)
        
        # PULSE_IN: route from ring to J8 on B.Cu
        if label == 'PULSE_IN' and other:
            j8 = other[0]
            j8_pos = (j8['x'], j8['y'])
            # Find ring entry angle for J8
            j8_angle = angle_of(j8['x'], j8['y'])
            ring_entry = polar(ring_r, j8_angle)
            # Via at ring entry, then B.Cu to J8
            add_via(board, ring_entry, nc)
            # Route on B.Cu: ring_entry -> waypoint to avoid center -> J8
            # J8 is far left at (47.2, 82.3), ring is at r=46 from (150,105)
            # Route along bottom of Arduino area
            add_track(board, ring_entry, j8_pos, TORSION_WIDTH, bcu, nc)
            # Also add arc segment on F.Cu ring to the entry point
            nearest_cell = min(cells, key=lambda c: abs(c['angle'] - j8_angle) if abs(c['angle'] - j8_angle) < 180 else 360 - abs(c['angle'] - j8_angle))
            a1 = nearest_cell['angle']
            a2 = j8_angle
            if abs(a2 - a1) > 180:
                if a2 > a1:
                    a1 += 360
                else:
                    a2 += 360
            add_arc_tracks(board, ring_r, min(a1,a2), max(a1,a2), TORSION_WIDTH, fcu, nc)
            print(f"  PULSE_IN→J8: routed via B.Cu")

    board.Save(BOARD_PATH)
    print(f"\nSaved: {BOARD_PATH}")

if __name__ == '__main__':
    main()
