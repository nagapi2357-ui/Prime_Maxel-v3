#!/usr/bin/env python3
"""Add board outline (Edge.Cuts): circle + rectangular Arduino tab.

Main circle: center (150, 105), R=75mm — contains cell ring + mounting holes
Arduino tab: rectangle extending left to x=20mm, from y=75 to y=170
             (covers J1-J7 headers with margin)
Smooth blend between circle and rectangle with small arcs at junctions.
"""

import pcbnew
import math
import os

BOARD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Prime_Maxel-v3.kicad_pcb')

# Board geometry
CX, CY = 150.0, 105.0  # Circle center
RADIUS = 75.0           # Circle radius
TAB_LEFT = 20.0         # Left edge of Arduino tab
TAB_TOP = 75.0          # Top of tab (y-min in KiCad coords)
TAB_BOTTOM = 170.0      # Bottom of tab (y-max)
CORNER_R = 3.0          # Corner radius for tab corners

def mm(val):
    return pcbnew.FromMM(val)

def add_line(board, x1, y1, x2, y2, layer, width=0.1):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    seg.SetLayer(layer)
    seg.SetWidth(mm(width))
    board.Add(seg)

def add_arc(board, cx, cy, start_x, start_y, angle_deg, layer, width=0.1):
    """Add arc given center, start point, and angle (degrees, positive=CCW)."""
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetCenter(pcbnew.VECTOR2I(mm(cx), mm(cy)))
    arc.SetStart(pcbnew.VECTOR2I(mm(start_x), mm(start_y)))
    # KiCad 8 uses SetArcAngleAndEnd
    arc.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(angle_deg, pcbnew.DEGREES_T), True)
    arc.SetLayer(layer)
    arc.SetWidth(mm(width))
    board.Add(arc)

def circle_point(cx, cy, r, angle_deg):
    """Get point on circle at given angle (0=right, 90=down in KiCad coords)."""
    rad = math.radians(angle_deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)

def main():
    board = pcbnew.LoadBoard(BOARD_PATH)
    edge_cuts = board.GetLayerID('Edge.Cuts')
    
    # Remove existing Edge.Cuts shapes
    to_remove = []
    for dwg in board.GetDrawings():
        if dwg.GetLayer() == edge_cuts:
            to_remove.append(dwg)
    for d in to_remove:
        board.Remove(d)
    print(f"Removed {len(to_remove)} existing Edge.Cuts shapes")
    
    # Calculate where the tab meets the circle
    # Tab top edge at y=TAB_TOP intersects circle: solve for x
    # (x - CX)^2 + (TAB_TOP - CY)^2 = R^2
    dy_top = TAB_TOP - CY  # negative (above center)
    dx_top = math.sqrt(RADIUS**2 - dy_top**2)
    circle_x_top = CX - dx_top  # left intersection
    
    dy_bot = TAB_BOTTOM - CY  # positive (below center)  
    dx_bot = math.sqrt(RADIUS**2 - dy_bot**2)
    circle_x_bot = CX - dx_bot  # left intersection
    
    print(f"Circle-tab junction top: ({circle_x_top:.1f}, {TAB_TOP})")
    print(f"Circle-tab junction bottom: ({circle_x_bot:.1f}, {TAB_BOTTOM})")
    
    # The outline consists of:
    # 1. Main circle arc (right portion, from bottom junction CW to top junction)
    # 2. Top tab line: from circle junction → left (with rounded corners)
    # 3. Left tab line: down
    # 4. Bottom tab line: right back to circle junction (with rounded corners)
    
    # Angles for circle junctions (measured from center, 0=right, positive=CW in screen)
    angle_top = math.degrees(math.atan2(dy_top, -dx_top))  # top-left
    angle_bot = math.degrees(math.atan2(dy_bot, -dx_bot))  # bottom-left
    
    print(f"Circle arc from {angle_bot:.1f}° to {angle_top:.1f}° (going CW through right side)")
    
    # Draw the main circle arc (the right ~270° portion)
    # From bottom junction, going clockwise (right, top, then to top junction)
    # In KiCad, positive angle = CCW
    # We want: from bottom junction CCW to top junction (the long way around right side)
    
    # Arc angle: go from bottom junction CCW (through right side) to top junction
    # bottom angle is positive (below), top angle is negative (above)
    # Going CCW from bottom: angle increases through 0 (right), -90 (top), to top junction
    arc_sweep = angle_top - angle_bot
    if arc_sweep > 0:
        arc_sweep -= 360  # We want the long way around (negative = CW)
    # Actually let's think again. angle_top ~ -160°, angle_bot ~ 160°
    # Going from bot (160°) CCW means increasing angle: 160 → 180 → -180 → -160 = top
    # That's the SHORT way (through the left/tab side) — we don't want that
    # We want the LONG way: bot (160°) → 90° → 0° → -90° → -160° = CW
    # CW = negative angle in KiCad
    
    # Total CW sweep from bottom to top going right:
    # From 160° CW to -160° = -(360 - 320) = no...
    # 160° to -160° CW = -(160 - (-160)) = -320°
    cw_sweep = -(360 - (angle_bot - angle_top))
    # Actually: going CW from angle_bot to angle_top
    # If angle_bot=160, angle_top=-160: CW means 160→0→-160 = -320°
    cw_sweep = angle_top - angle_bot  # -160 - 160 = -320
    if cw_sweep > 0:
        cw_sweep -= 360
        
    print(f"Arc sweep: {cw_sweep:.1f}° (negative=CW)")
    
    # Start point of arc is at the bottom junction
    start_x, start_y = circle_point(CX, CY, RADIUS, angle_bot)
    
    add_arc(board, CX, CY, start_x, start_y, cw_sweep, edge_cuts)
    print("  Main circle arc ✓")
    
    # Now the tab portion:
    # Top line: from circle top junction to tab top-left corner (with rounded corners)
    # Left line: tab left side
    # Bottom line: from tab bottom-left to circle bottom junction
    
    top_junc_x, top_junc_y = circle_point(CX, CY, RADIUS, angle_top)
    bot_junc_x, bot_junc_y = circle_point(CX, CY, RADIUS, angle_bot)
    
    # Tab corners (with rounding)
    # Top-left corner: (TAB_LEFT + CORNER_R, TAB_TOP + CORNER_R) center
    # Top line: from top_junc → (TAB_LEFT + CORNER_R, TAB_TOP) 
    add_line(board, top_junc_x, top_junc_y, TAB_LEFT + CORNER_R, TAB_TOP, edge_cuts)
    print("  Top tab line ✓")
    
    # Top-left corner arc
    add_arc(board, TAB_LEFT + CORNER_R, TAB_TOP + CORNER_R, 
            TAB_LEFT + CORNER_R, TAB_TOP, -90, edge_cuts)
    print("  Top-left corner ✓")
    
    # Left side
    add_line(board, TAB_LEFT, TAB_TOP + CORNER_R, TAB_LEFT, TAB_BOTTOM - CORNER_R, edge_cuts)
    print("  Left tab line ✓")
    
    # Bottom-left corner arc
    add_arc(board, TAB_LEFT + CORNER_R, TAB_BOTTOM - CORNER_R,
            TAB_LEFT, TAB_BOTTOM - CORNER_R, -90, edge_cuts)
    print("  Bottom-left corner ✓")
    
    # Bottom line: from corner to circle bottom junction
    add_line(board, TAB_LEFT + CORNER_R, TAB_BOTTOM, bot_junc_x, bot_junc_y, edge_cuts)
    print("  Bottom tab line ✓")
    
    board.Save(BOARD_PATH)
    print(f"\nSaved! Board outline added to {BOARD_PATH}")

if __name__ == '__main__':
    main()
