#!/usr/bin/env python3
"""Fix remaining unrouted connections:
1. U1 COL_SCL0-5 pads: via stubs are offset - need short F.Cu segments to actual pads
2. U1 COL_SDA4/5, COL_SCL4/5: right-side pads need connecting to left-side track endpoints
3. PULSE_IN: J7 pin 22 → star center at (150, 108)
"""

import pcbnew
import os

BOARD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Prime_Maxel-v3.kicad_pcb')

def mm(val):
    return pcbnew.FromMM(val)

def add_track(board, x1, y1, x2, y2, net, layer, width=0.25):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    t.SetNet(net)
    t.SetLayer(layer)
    t.SetWidth(mm(width))
    board.Add(t)

def add_via(board, x, y, net, drill=0.3, size=0.6):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetNet(net)
    v.SetDrill(mm(drill))
    v.SetWidth(mm(size))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    board.Add(v)

def get_net(board, name):
    net = board.GetNetInfo().GetNetItem(name)
    if net is None or net.GetNetCode() == 0:
        raise ValueError(f"Net '{name}' not found")
    return net

def main():
    board = pcbnew.LoadBoard(BOARD_PATH)
    F_Cu = board.GetLayerID('F.Cu')
    B_Cu = board.GetLayerID('B.Cu')
    
    # ═══════════════════════════════════════════════
    # 1. Fix U1 left-side COL_SCL pads (0-3)
    #    SCL vias landed at SDA pad positions (one pin above)
    #    Need short vertical F.Cu stubs from via to actual SCL pad
    # ═══════════════════════════════════════════════
    print("=== Fixing U1 left-side COL_SCL connections ===")
    
    # COL_SCL0: via at (147.14, 102.72) → pad at (147.14, 104.03)
    # But wait — 102.72 is actually the Net-(U1-SCL) pad position!
    # The COL_SCL0 track endpoint is at y that's 1.3mm off from the pad.
    # Looking at the data: nearest track for SCL0 is at (147.14, 102.72) but pad is at (147.14, 104.03)
    # That 102.72 point is U1 pin 22 (Net-U1-SCL) — different net!
    # The actual COL_SCL0 track must start from the via that came from the cell.
    
    # Let me re-examine: the route_intracell script placed vias at U1 pad positions.
    # But the left-side pins alternate SDA/SCL:
    #   pin 4 = COL_SDA0 (103.38) ✓ connected
    #   pin 5 = COL_SCL0 (104.03) ✗ nearest track at 102.72
    #   pin 6 = COL_SDA1 (104.67) ✓ connected
    #   pin 7 = COL_SCL1 (105.33) ✗ nearest track at 104.03
    # Pattern: SCL tracks are landing 1.3mm above (at the previous pin position)
    # This means the via/track for SCL0 is at y=102.72 which is NOT on U1 at all
    # It seems the route script used wrong coordinates.
    
    # Fix: add short F.Cu segments from existing track endpoints to actual U1 pads
    scl_fixes_left = [
        # (net_name, existing_track_y, actual_pad_y, x=147.14)
        ('/COL_SCL0', 102.72, 104.03),  # 102.72 is pin 22 area, pad is pin 5
        ('/COL_SCL1', 104.03, 105.33),  # was at pin 5 pos, should be pin 7
        ('/COL_SCL2', 105.33, 106.62),  # was at pin 7 pos, should be pin 9
        ('/COL_SCL3', 106.62, 107.92),  # was at pin 9 pos, should be pin 11
    ]
    
    x_left = 147.14
    for net_name, from_y, to_y in scl_fixes_left:
        net = get_net(board, net_name)
        add_track(board, x_left, from_y, x_left, to_y, net, F_Cu)
        print(f"  {net_name}: stub ({x_left},{from_y:.2f}) → ({x_left},{to_y:.2f})")
    
    # ═══════════════════════════════════════════════
    # 2. Fix U1 right-side pins (13-16): COL_SDA4/5, COL_SCL4/5
    #    Tracks currently end on LEFT side (x=147.14) but pads are on RIGHT (x=152.86)
    #    Need to route across the chip (under it on B.Cu or around)
    # ═══════════════════════════════════════════════
    print("\n=== Fixing U1 right-side COL connections ===")
    
    # Right-side pads:
    #   pin 13 = COL_SDA4 (152.86, 108.58) — track at (147.14, 108.58)
    #   pin 14 = COL_SCL4 (152.86, 107.92) — track at (147.14, 107.92) 
    #   pin 15 = COL_SDA5 (152.86, 107.28) — track at (152.86, 107.92) dist=0.65mm
    #   pin 16 = COL_SCL5 (152.86, 106.62) — track at (152.86, 108.58) dist=1.95mm
    
    # For SDA4 and SCL4: route horizontal across under chip on B.Cu
    right_side_cross = [
        ('/COL_SDA4', 147.14, 108.58, 152.86, 108.58),  # pin 13
        ('/COL_SCL4', 147.14, 107.92, 152.86, 107.92),  # pin 14
    ]
    
    for net_name, x1, y1, x2, y2 in right_side_cross:
        net = get_net(board, net_name)
        # Via down to B.Cu, cross, via back up
        add_via(board, x1, y1, net)
        add_track(board, x1, y1, x2, y2, net, B_Cu)
        add_via(board, x2, y2, net)
        print(f"  {net_name}: cross via ({x1},{y1}) → B.Cu → via ({x2},{y2})")
    
    # For SDA5: track endpoint at (152.86, 107.92) needs to reach pad at (152.86, 107.28)
    net_sda5 = get_net(board, '/COL_SDA5')
    add_track(board, 152.86, 107.92, 152.86, 107.28, net_sda5, F_Cu)
    print(f"  /COL_SDA5: stub (152.86,107.92) → (152.86,107.28)")
    
    # For SCL5: track endpoint at (152.86, 108.58) needs to reach pad at (152.86, 106.62)
    net_scl5 = get_net(board, '/COL_SCL5')
    add_track(board, 152.86, 108.58, 152.86, 106.62, net_scl5, F_Cu)
    print(f"  /COL_SCL5: stub (152.86,108.58) → (152.86,106.62)")
    
    # ═══════════════════════════════════════════════
    # 3. PULSE_IN: J7 pin 22 (47.23, 82.34) → star center (150.0, 108.0)
    #    Route on B.Cu with L-shape to avoid crossing cell ring
    # ═══════════════════════════════════════════════
    print("\n=== Routing PULSE_IN: J7 → star center ===")
    
    net_pulse = get_net(board, '/Golden Cell/PULSE_IN')
    j7_x, j7_y = 47.23, 82.34
    star_x, star_y = 150.0, 108.0
    
    # L-path on B.Cu: go right at y=82.34 to x=150, then down to y=108
    add_via(board, j7_x, j7_y, net_pulse)
    add_track(board, j7_x, j7_y, star_x, j7_y, net_pulse, B_Cu)
    add_track(board, star_x, j7_y, star_x, star_y, net_pulse, B_Cu)
    add_via(board, star_x, star_y, net_pulse)
    print(f"  PULSE_IN: J7 ({j7_x},{j7_y}) → B.Cu L-path → star ({star_x},{star_y})")
    
    board.Save(BOARD_PATH)
    print(f"\nSaved! All fixes applied to {BOARD_PATH}")

if __name__ == '__main__':
    main()
