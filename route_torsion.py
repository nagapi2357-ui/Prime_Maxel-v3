#!/usr/bin/env python3
"""Route TORSION_A, TORSION_B, and PULSE_IN ring buses for Prime_Maxel-v3."""
import pcbnew, math, shutil, os

BOARD_PATH = '/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/Prime_Maxel-v3.kicad_pcb'
BACKUP_PATH = BOARD_PATH + '.pre_torsion_routing.bak'

CX, CY = 150.0, 105.0
TORSION_WIDTH = 0.229  # mm (50 ohm controlled impedance)
PULSE_WIDTH = 0.229    # same netclass? using same for now

# Ring radii (between chips at r~35-44 and TPs at r~56)
RING_R_PULSE = 46.0
RING_R_TORSION_A = 48.0
RING_R_TORSION_B = 50.0

def to_nm(mm):
    return int(mm * 1e6)

def polar(r, angle_deg):
    """Return (x, y) at radius r and angle (degrees) from center."""
    rad = math.radians(angle_deg)
    return (CX + r * math.cos(rad), CY + r * math.sin(rad))

def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def add_track(board, start, end, width, layer, netcode):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(to_nm(start[0]), to_nm(start[1])))
    t.SetEnd(pcbnew.VECTOR2I(to_nm(end[0]), to_nm(end[1])))
    t.SetWidth(to_nm(width))
    t.SetLayer(layer)
    t.SetNetCode(netcode)
    board.Add(t)

def add_arc_tracks(board, cx, cy, r, a_start_deg, a_end_deg, width, layer, netcode, step_deg=3):
    """Add arc as series of short straight segments."""
    points = []
    # Ensure we go in the right direction
    if a_end_deg < a_start_deg:
        a_end_deg += 360
    a = a_start_deg
    while a < a_end_deg:
        points.append(polar(r, a))
        a += step_deg
    points.append(polar(r, a_end_deg % 360 if a_end_deg >= 360 else a_end_deg))
    
    for i in range(len(points) - 1):
        add_track(board, points[i], points[i+1], width, layer, netcode)
    return points

def collect_net_pads(board, net_name):
    """Collect pads for a net, organized by component."""
    pads = []
    for pad in board.GetPads():
        if pad.GetNetname() == net_name:
            pos = pad.GetPosition()
            x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            ref = pad.GetParentAsString()
            pin = pad.GetNumber()
            angle = math.degrees(math.atan2(y - CY, x - CX))
            r = math.sqrt((x-CX)**2 + (y-CY)**2)
            pads.append({'ref': ref, 'pin': pin, 'x': x, 'y': y, 'angle': angle, 'r': r})
    return pads

def group_into_cells(pads):
    """Group pads into cells by angular proximity. Returns list of cell dicts sorted by angle."""
    # Separate U-pads and TP-pads
    u_pads = {}  # ref -> [pad_dict, ...]
    tp_pads = {}  # ref -> pad_dict
    other_pads = []
    
    for p in pads:
        if p['ref'].startswith('U'):
            u_pads.setdefault(p['ref'], []).append(p)
        elif p['ref'].startswith('TP'):
            tp_pads[p['ref']] = p
        else:
            other_pads.append(p)
    
    # Build cells: each U-ref is a cell, match nearest TP by angle
    cells = []
    used_tps = set()
    
    for ref, chip_pads in u_pads.items():
        cell_angle = sum(p['angle'] for p in chip_pads) / len(chip_pads)
        
        # Find nearest TP by angle
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
        
        cells.append({
            'ref': ref,
            'angle': cell_angle,
            'chip_pads': chip_pads,
            'tp': tp,
        })
    
    cells.sort(key=lambda c: c['angle'])
    return cells, other_pads

def route_ring_bus(board, cells, ring_r, width, layer, netcode, net_label=""):
    """Route a ring bus connecting all cells, plus stubs to chip pads and TPs."""
    n = len(cells)
    track_count = 0
    
    # 1. Route ring arc segments between adjacent cells
    for i in range(n - 1):
        a_start = cells[i]['angle']
        a_end = cells[i+1]['angle']
        add_arc_tracks(board, CX, CY, ring_r, a_start, a_end, width, layer, netcode)
        track_count += 1
    
    # Close the ring (last cell to first cell)
    a_start = cells[-1]['angle']
    a_end = cells[0]['angle'] + 360  # wrap around
    add_arc_tracks(board, CX, CY, ring_r, a_start, a_end, width, layer, netcode)
    track_count += 1
    
    # 2. For each cell, route stubs from ring point to chip pads and TP
    for cell in cells:
        ring_point = polar(ring_r, cell['angle'])
        
        # Connect chip pads to each other first (short intra-cell traces)
        chip_pads = sorted(cell['chip_pads'], key=lambda p: p['pin'])
        if len(chip_pads) >= 2:
            for i in range(len(chip_pads) - 1):
                p1 = (chip_pads[i]['x'], chip_pads[i]['y'])
                p2 = (chip_pads[i+1]['x'], chip_pads[i+1]['y'])
                add_track(board, p1, p2, width, layer, netcode)
                track_count += 1
        
        # Connect nearest chip pad to ring point
        nearest_pad = min(chip_pads, key=lambda p: dist((p['x'], p['y']), ring_point))
        pad_pos = (nearest_pad['x'], nearest_pad['y'])
        add_track(board, pad_pos, ring_point, width, layer, netcode)
        track_count += 1
        
        # Connect TP to ring point
        if cell['tp']:
            tp_pos = (cell['tp']['x'], cell['tp']['y'])
            add_track(board, ring_point, tp_pos, width, layer, netcode)
            track_count += 1
    
    print(f"  {net_label}: Routed ring bus + stubs ({track_count} operations)")

def route_pulse_in_to_arduino(board, cells, ring_r, width, layer, netcode, j8_pad):
    """Route PULSE_IN from ring bus to J8 connector on Arduino shield."""
    # Find the cell nearest to J8 (which is at angle ~-168°, roughly where U8 is)
    j8_angle = math.degrees(math.atan2(j8_pad['y'] - CY, j8_pad['x'] - CX))
    
    # Ring point at J8's angle
    ring_entry = polar(ring_r, j8_angle)
    
    # Route from J8 pad to ring entry point
    # This is a longer trace from Arduino area to the circular arena
    # Route in two segments: J8 -> intermediate point -> ring entry
    j8_pos = (j8_pad['x'], j8_pad['y'])
    
    # Route directly (may need waypoints to avoid components, but start simple)
    add_track(board, j8_pos, ring_entry, width, layer, netcode)
    print(f"  PULSE_IN→J8: Routed from ring to J8 @ ({j8_pad['x']:.1f}, {j8_pad['y']:.1f})")


def main():
    # Backup
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(BOARD_PATH, BACKUP_PATH)
        print(f"Backup saved: {BACKUP_PATH}")
    else:
        print(f"Backup already exists: {BACKUP_PATH}")
    
    board = pcbnew.LoadBoard(BOARD_PATH)
    
    # Get layer IDs
    fcu = board.GetLayerID('F.Cu')
    
    # Get net codes
    nets = board.GetNetsByName()
    
    net_a_name = '/Golden Cell/TORSION_A'
    net_b_name = '/Golden Cell/TORSION_B'
    net_p_name = '/Golden Cell/PULSE_IN'
    
    nc_a = nets[net_a_name].GetNetCode()
    nc_b = nets[net_b_name].GetNetCode()
    nc_p = nets[net_p_name].GetNetCode()
    
    print(f"Net codes: TORSION_A={nc_a}, TORSION_B={nc_b}, PULSE_IN={nc_p}")
    
    # Collect and group pads
    pads_a = collect_net_pads(board, net_a_name)
    pads_b = collect_net_pads(board, net_b_name)
    pads_p = collect_net_pads(board, net_p_name)
    
    cells_a, other_a = group_into_cells(pads_a)
    cells_b, other_b = group_into_cells(pads_b)
    cells_p, other_p = group_into_cells(pads_p)
    
    print(f"\nTORSION_A: {len(cells_a)} cells, {len(other_a)} other pads")
    print(f"TORSION_B: {len(cells_b)} cells, {len(other_b)} other pads")
    print(f"PULSE_IN: {len(cells_p)} cells, {len(other_p)} other pads")
    
    # Route TORSION_A ring bus
    print("\nRouting TORSION_A...")
    route_ring_bus(board, cells_a, RING_R_TORSION_A, TORSION_WIDTH, fcu, nc_a, "TORSION_A")
    
    # Route TORSION_B ring bus
    print("\nRouting TORSION_B...")
    route_ring_bus(board, cells_b, RING_R_TORSION_B, TORSION_WIDTH, fcu, nc_b, "TORSION_B")
    
    # Route PULSE_IN ring bus
    print("\nRouting PULSE_IN...")
    route_ring_bus(board, cells_p, RING_R_PULSE, PULSE_WIDTH, fcu, nc_p, "PULSE_IN")
    
    # Route PULSE_IN to Arduino connector
    if other_p:
        j8 = other_p[0]  # J8 pin 22
        route_pulse_in_to_arduino(board, cells_p, RING_R_PULSE, PULSE_WIDTH, fcu, nc_p, j8)
    
    # Save
    board.Save(BOARD_PATH)
    print(f"\nBoard saved to {BOARD_PATH}")
    
    # Run DRC summary
    print("\nDone! Open in KiCad to verify. Run DRC to check for violations.")

if __name__ == '__main__':
    main()
