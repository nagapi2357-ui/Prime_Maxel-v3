# Prime Mirror Ring - PCB Component Placement Script (v2)
# Only places golden cells + TCA9548A mux + mounting holes
# Leaves Arduino shield headers (J1-J7) untouched for manual placement
#
# Run via KiCad scripting console:
# exec(open("/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/Nagaπ Python Scripts/place_ring.py").read())

import pcbnew
import math

board = pcbnew.GetBoard()

# Layout parameters
RING_RADIUS = 45.0       # mm - radius for cell centres (increased from 38)
BOARD_CENTRE_X = 150.0   # mm
BOARD_CENTRE_Y = 105.0   # mm
MM = pcbnew.FromMM

# Each golden cell: (name, angle_deg, LM324_ref, SLG_ref, [caps], [resistors], [test_points])
# 3 caps per cell, 2 resistors, 4 test points
cells = [
    ("N1",  255, "U2",  "U3",  ["C1","C2","C3"],     ["R3","R4"],   ["TP1","TP2","TP3","TP4"]),
    ("N2",  225, "U4",  "U5",  ["C4","C5","C6"],     ["R5","R6"],   ["TP5","TP6","TP7","TP8"]),
    ("N3",  195, "U6",  "U7",  ["C7","C8","C9"],     ["R7","R8"],   ["TP9","TP10","TP11","TP12"]),
    ("N4",  165, "U8",  "U9",  ["C10","C11","C12"],  ["R9","R10"],  ["TP13","TP14","TP15","TP16"]),
    ("N5",  135, "U10", "U11", ["C13","C14","C15"],  ["R11","R12"], ["TP17","TP18","TP19","TP20"]),
    ("N6",  105, "U12", "U13", ["C16","C17","C18"],  ["R13","R14"], ["TP21","TP22","TP23","TP24"]),
    ("N7",   75, "U14", "U15", ["C19","C20","C21"],  ["R15","R16"], ["TP25","TP26","TP27","TP28"]),
    ("N8",   45, "U16", "U17", ["C22","C23","C24"],  ["R17","R18"], ["TP29","TP30","TP31","TP32"]),
    ("N9",   15, "U18", "U19", ["C25","C26","C27"],  ["R19","R20"], ["TP33","TP34","TP35","TP36"]),
    ("N10", -15, "U20", "U21", ["C28","C29","C30"],  ["R21","R22"], ["TP37","TP38","TP39","TP40"]),
    ("N11", -45, "U22", "U23", ["C31","C32","C33"],  ["R23","R24"], ["TP41","TP42","TP43","TP44"]),
    ("N12", -75, "U24", "U25", ["C34","C35","C36"],  ["R25","R26"], ["TP45","TP46","TP47","TP48"]),
]

def find_fp(ref):
    for fp in board.GetFootprints():
        if fp.GetReference() == ref:
            return fp
    print("WARNING: " + ref + " not found!")
    return None

def place(ref, x_mm, y_mm, angle_deg=0):
    fp = find_fp(ref)
    if fp:
        fp.SetPosition(pcbnew.VECTOR2I(MM(x_mm), MM(y_mm)))
        fp.SetOrientationDegrees(angle_deg)

print("=" * 50)
print("Prime Mirror Ring Placement v2")
print("=" * 50)
print("Skipping Arduino shield headers (J1-J7) — place manually")
print("")

# --- Place 12 golden cells around the ring ---
# Component sizes (mm):
#   LM324 SOIC-14:  ~8.6 x 6.0  (body+pads ~10 x 7)
#   SLG47004V QFN:  ~3.0 x 3.0  (body+pads ~4.5 x 4.5)
#   Cap 0603:       ~1.6 x 0.8
#   Res 0402:       ~1.0 x 0.5
#   TestPoint:      ~1.5 x 1.5

for node, angle_deg, lm324, slg, caps, res, tps in cells:
    angle_rad = math.radians(angle_deg)
    # Unit vectors: radial (outward) and tangential (perpendicular, CCW)
    rad_x = math.cos(angle_rad)
    rad_y = -math.sin(angle_rad)
    tan_x = -math.sin(angle_rad)  # tangential = perpendicular to radial
    tan_y = -math.cos(angle_rad)

    # Cell centre on ring
    cx = BOARD_CENTRE_X + RING_RADIUS * rad_x
    cy = BOARD_CENTRE_Y + RING_RADIUS * rad_y

    # Rotation: orient components so their "top" points outward
    rot = -(angle_deg - 90)

    # LM324 (inward, closer to centre) - offset 6mm inward from cell centre
    lm_offset = -6.0
    place(lm324, cx + lm_offset * rad_x, cy + lm_offset * rad_y, rot)

    # SLG47004V (outward, further from centre) - offset 7mm outward
    slg_offset = 7.0
    place(slg, cx + slg_offset * rad_x, cy + slg_offset * rad_y, rot)

    # Caps: placed between LM324 and SLG, spread along tangent
    for i, cap in enumerate(caps):
        t_off = (i - 1) * 2.2  # tangential spacing
        r_off = 0.5             # slight radial offset (between the two ICs)
        cap_x = cx + r_off * rad_x + t_off * tan_x
        cap_y = cy + r_off * rad_y + t_off * tan_y
        place(cap, cap_x, cap_y, rot)

    # Resistors: next to LM324, inward side, spread along tangent
    for i, r in enumerate(res):
        t_off = (i - 0.5) * 2.5
        r_off = -9.5  # further inward than LM324
        r_x = cx + r_off * rad_x + t_off * tan_x
        r_y = cy + r_off * rad_y + t_off * tan_y
        place(r, r_x, r_y, rot)

    # Test points: outside the SLG, spread along tangent
    for i, tp in enumerate(tps):
        t_off = (i - 1.5) * 2.5
        r_off = 11.0  # outside SLG
        tp_x = cx + r_off * rad_x + t_off * tan_x
        tp_y = cy + r_off * rad_y + t_off * tan_y
        place(tp, tp_x, tp_y, rot)

    print("  " + node + " placed: " + lm324 + " (inward) / " + slg + " (outward) at " + str(angle_deg) + " deg")

# --- Centre: TCA9548A I2C mux + pull-up resistors ---
print("\nPlacing TCA9548A (U1) at centre...")
place("U1", BOARD_CENTRE_X, BOARD_CENTRE_Y, 0)
place("R1", BOARD_CENTRE_X - 4.0, BOARD_CENTRE_Y - 6.0, 0)
place("R2", BOARD_CENTRE_X + 4.0, BOARD_CENTRE_Y - 6.0, 0)

# --- Mounting holes: 6 holes evenly spaced outside the ring ---
print("Placing 6 mounting holes...")
mh_radius = RING_RADIUS + 22.0
for i, mh in enumerate(["MH1", "MH2", "MH3", "MH4", "MH5", "MH6"]):
    a = math.radians(i * 60 + 30)  # offset 30 deg so they fall between cells
    place(mh, BOARD_CENTRE_X + mh_radius * math.cos(a),
              BOARD_CENTRE_Y - mh_radius * math.sin(a), 0)

pcbnew.Refresh()
print("\n" + "=" * 50)
print("Done! Golden cells + mux + mounting holes placed.")
print("Arduino headers (J1-J7) left untouched.")
print("=" * 50)
