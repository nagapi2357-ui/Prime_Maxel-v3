#!/usr/bin/env python3
"""Route the main I2C bus: Arduino J1 → R1/R2 → TCA9548A U1.

Nets:
  /SDA{slash}20  : J1.2 (29.45,157.52) → R1.1 (145.49,99.00)
  /SCL{slash}21  : J1.1 (29.45,160.06) → R2.1 (153.49,99.00)
  Net-(U1-SDA)   : R1.2 (146.51,99.00) → U1.23 (152.86,102.08)
  Net-(U1-SCL)   : R2.2 (154.51,99.00) → U1.22 (152.86,102.72)

Strategy:
  - Long runs on B.Cu with vias at each end (L-shaped)
  - Short R→U1 hops on F.Cu
  - Track width: 0.25mm (standard signal)
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
    
    net_sda20 = get_net(board, '/SDA{slash}20')
    net_scl21 = get_net(board, '/SCL{slash}21')
    net_u1_sda = get_net(board, 'Net-(U1-SDA)')
    net_u1_scl = get_net(board, 'Net-(U1-SCL)')
    
    print("Routing main I2C bus...")
    
    # ──────────────────────────────────────────────
    # SDA: J1.2 (29.45, 157.52) → R1.1 (145.49, 99.00)
    # L-path on B.Cu: right at y=157.52, then up
    # ──────────────────────────────────────────────
    add_via(board, 29.45, 157.52, net_sda20)
    add_track(board, 29.45, 157.52, 145.49, 157.52, net_sda20, B_Cu)
    add_track(board, 145.49, 157.52, 145.49, 99.00, net_sda20, B_Cu)
    add_via(board, 145.49, 99.00, net_sda20)
    print("  SDA: J1 → R1 ✓")
    
    # ──────────────────────────────────────────────
    # SCL: J1.1 (29.45, 160.06) → R2.1 (153.49, 99.00)
    # L-path on B.Cu: right at y=160.06, then up
    # ──────────────────────────────────────────────
    add_via(board, 29.45, 160.06, net_scl21)
    add_track(board, 29.45, 160.06, 153.49, 160.06, net_scl21, B_Cu)
    add_track(board, 153.49, 160.06, 153.49, 99.00, net_scl21, B_Cu)
    add_via(board, 153.49, 99.00, net_scl21)
    print("  SCL: J1 → R2 ✓")
    
    # ──────────────────────────────────────────────
    # R1.2 (146.51, 99.00) → U1.23 (152.86, 102.08) — SDA
    # F.Cu: right to x=149.5, then down to 102.08, then right to 152.86
    # (avoid collision with SCL at x=152.86)
    # ──────────────────────────────────────────────
    add_track(board, 146.51, 99.00, 146.51, 102.08, net_u1_sda, F_Cu)
    add_track(board, 146.51, 102.08, 152.86, 102.08, net_u1_sda, F_Cu)
    print("  SDA: R1 → U1 ✓")
    
    # ──────────────────────────────────────────────
    # R2.2 (154.51, 99.00) → U1.22 (152.86, 102.72) — SCL
    # F.Cu: down at x=154.51 to y=102.72, then left to 152.86
    # ──────────────────────────────────────────────
    add_track(board, 154.51, 99.00, 154.51, 102.72, net_u1_scl, F_Cu)
    add_track(board, 154.51, 102.72, 152.86, 102.72, net_u1_scl, F_Cu)
    print("  SCL: R2 → U1 ✓")
    
    print("\nSaving...")
    board.Save(BOARD_PATH)
    print(f"Saved: {BOARD_PATH}")
    print("\nMain I2C routing complete! 4 routes added.")

if __name__ == '__main__':
    main()
