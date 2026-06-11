#!/usr/bin/env python3
"""Route TORSION_A, TORSION_B, PULSE_IN - v3

Strategy:
- Ring buses on B.Cu (impedance ref: In2.Cu VCC plane)  
- SMD chip pad stubs: short F.Cu trace → via → B.Cu ring
- TPs (through-hole): direct B.Cu connection to ring
- J8 (through-hole): direct B.Cu from ring

Via placement: at ring radius, at each cell's angle. One via per cell per net.
Short F.Cu stubs from chip pads to via location, then B.Cu ring connects all vias.
"""
import pcbnew, math, shutil, os

BOARD_PATH = '/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/Prime_Maxel-v3.kicad_pcb'
BACKUP_PATH = BOARD_PATH + '.pre_torsion_routing.bak'

CX, CY = 150.0, 105.0
TRACE_W = 0.229  # mm, 50 ohm
VIA_SIZE = 0.6   # mm
VIA_DRILL = 0.3  # mm

# Ring radii - staggered, between chips (~35-44mm) and TPs (~56mm)
RING_R = {
    '/Golden Cell/PULSE_IN': 46.0,
    '/Golden Cell/TORSION_A': 48.0, 
    '/Golden Cell/TORSION_B': 50.0,
}

def nm(mm): return int(mm * 1e6)
def polar(r, a): 
    rad = math.radians(a)
    return (CX + r*math.cos(rad), CY + r*math.sin(rad))
def dist2(a, b): return (a[0]-b[0])**2 + (a[1]-b[1])**2
def ang(x, y): return math.degrees(math.atan2(y-CY, x-CX))

def add_track(board, s, e, w, layer, nc):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(nm(s[0]), nm(s[1])))
    t.SetEnd(pcbnew.VECTOR2I(nm(e[0]), nm(e[1])))
    t.SetWidth(nm(w))
    t.SetLayer(layer)
    t.SetNetCode(nc)
    board.Add(t)

def add_via(board, pos, nc):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(nm(pos[0]), nm(pos[1])))
    v.SetWidth(nm(VIA_SIZE))
    v.SetDrill(nm(VIA_DRILL))
    v.SetNetCode(nc)
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    board.Add(v)

def arc_tracks(board, r, a1, a2, w, layer, nc, step=3):
    """Arc from a1 to a2 (CW, increasing angle). Wraps if needed."""
    if a2 < a1: a2 += 360
    pts = []
    a = a1
    while a < a2 - 0.01:
        pts.append(polar(r, a % 360))
        a += step
    pts.append(polar(r, a2 % 360))
    for i in range(len(pts)-1):
        add_track(board, pts[i], pts[i+1], w, layer, nc)

def get_pads(board, net_name):
    pads = []
    for p in board.GetPads():
        if p.GetNetname() == net_name:
            pos = p.GetPosition()
            x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            ref = p.GetParentAsString()
            pads.append({
                'ref': ref, 'pin': p.GetNumber(),
                'x': x, 'y': y,
                'angle': ang(x, y),
                'r': math.sqrt((x-CX)**2 + (y-CY)**2)
            })
    return pads

def group_cells(pads):
    u, tp, other = {}, {}, []
    for p in pads:
        if p['ref'].startswith('U'): u.setdefault(p['ref'], []).append(p)
        elif p['ref'].startswith('TP'): tp[p['ref']] = p
        else: other.append(p)
    
    cells = []
    used = set()
    for ref, cps in u.items():
        ca = sum(p['angle'] for p in cps) / len(cps)
        best, bd = None, 999
        for tr, t in tp.items():
            if tr in used: continue
            d = abs(t['angle'] - ca)
            if d > 180: d = 360 - d
            if d < bd: bd, best = d, tr
        if best: used.add(best)
        cells.append({'ref': ref, 'angle': ca, 'pads': cps, 'tp': tp.get(best)})
    cells.sort(key=lambda c: c['angle'])
    return cells, other

def route_net(board, net_name, fcu, bcu, nc):
    ring_r = RING_R[net_name]
    cells, other = group_cells(get_pads(board, net_name))
    n = len(cells)
    print(f"  {net_name}: {n} cells, ring r={ring_r}mm")
    
    # 1. B.Cu ring bus (closed ring connecting all cells)
    for i in range(n):
        j = (i+1) % n
        a1, a2 = cells[i]['angle'], cells[j]['angle']
        if j == 0: a2 += 360
        arc_tracks(board, ring_r, a1, a2, TRACE_W, bcu, nc)
    
    # 2. Per-cell: F.Cu chip pad interconnect → via → B.Cu ring, B.Cu → TP
    for cell in cells:
        via_pt = polar(ring_r, cell['angle'])
        pads = sorted(cell['pads'], key=lambda p: p['pin'])
        
        # Interconnect chip pads on F.Cu
        for i in range(len(pads)-1):
            add_track(board, (pads[i]['x'], pads[i]['y']),
                      (pads[i+1]['x'], pads[i+1]['y']), TRACE_W, fcu, nc)
        
        # F.Cu stub: nearest chip pad → via location
        nearest = min(pads, key=lambda p: dist2((p['x'],p['y']), via_pt))
        add_track(board, (nearest['x'], nearest['y']), via_pt, TRACE_W, fcu, nc)
        
        # Via at ring point (F.Cu ↔ B.Cu)
        add_via(board, via_pt, nc)
        
        # B.Cu stub: via → TP (through-hole pad accessible on B.Cu)
        if cell['tp']:
            add_track(board, via_pt, (cell['tp']['x'], cell['tp']['y']),
                      TRACE_W, bcu, nc)
    
    return cells, other

def main():
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(BOARD_PATH, BACKUP_PATH)
    
    board = pcbnew.LoadBoard(BOARD_PATH)
    fcu = board.GetLayerID('F.Cu')
    bcu = board.GetLayerID('B.Cu')
    nets_map = board.GetNetsByName()
    
    print("Routing TORSION_A, TORSION_B, PULSE_IN (v3: B.Cu ring buses)...")
    
    for net_name in ['/Golden Cell/TORSION_A', '/Golden Cell/TORSION_B', '/Golden Cell/PULSE_IN']:
        nc = nets_map[net_name].GetNetCode()
        cells, other = route_net(board, net_name, fcu, bcu, nc)
        
        if net_name == '/Golden Cell/PULSE_IN' and other:
            j8 = other[0]
            j8_pos = (j8['x'], j8['y'])
            ring_r = RING_R[net_name]
            # Route J8 on B.Cu: connect to nearest ring point
            j8_ang = ang(j8['x'], j8['y'])
            # Find nearest cell on ring
            nearest_cell = min(cells, key=lambda c: min(abs(c['angle']-j8_ang), 360-abs(c['angle']-j8_ang)))
            ring_pt = polar(ring_r, nearest_cell['angle'])
            # J8 is through-hole, route on B.Cu
            add_track(board, j8_pos, ring_pt, TRACE_W, bcu, nc)
            print(f"  PULSE_IN→J8 routed on B.Cu")
    
    # Refill zones
    print("\nRefilling zones...")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("Zones refilled.")
    
    board.Save(BOARD_PATH)
    print(f"Saved: {BOARD_PATH}")

if __name__ == '__main__':
    main()
