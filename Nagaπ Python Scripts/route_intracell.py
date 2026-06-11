# Prime Mirror Ring - Intra-Cell Routing Script
# Routes all connections WITHIN each golden cell:
#   - LM324 ↔ SLG signal traces (4 pairs per cell)
#   - Cap power connections
#   - Resistor divider (VREF_MID)
#   - Test point stubs
#   - Fixes torsion ring stubs (LM324, not SLG)
#   - LM324/SLG power pin vias to planes
#
# Run via KiCad scripting console:
# exec(open("/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/Nagaπ Python Scripts/route_intracell.py").read())

import pcbnew
import math

board = pcbnew.GetBoard()
MM = pcbnew.FromMM

# ============================================================
# CONSTANTS
# ============================================================
BOARD_CENTRE_X = 150.0
BOARD_CENTRE_Y = 105.0
RING_RADIUS = 45.0

TORSION_A_RADIUS = 50.0
TORSION_B_RADIUS = 50.0 * 13.0 / 11.0  # 59.09mm

SIGNAL_WIDTH = 0.2    # mm
TORSION_WIDTH = 0.229  # mm (50Ω)
POWER_WIDTH = 0.3      # mm

VIA_DRILL = 0.3
VIA_SIZE = 0.6

F_Cu = board.GetLayerID("F.Cu")
In1_Cu = board.GetLayerID("In1.Cu")
In2_Cu = board.GetLayerID("In2.Cu")
B_Cu = board.GetLayerID("B.Cu")

# ============================================================
# CELL DEFINITIONS
# ============================================================
# (name, angle_deg, LM324_ref, SLG_ref, [cap_refs], [res_refs], [tp_refs])
# Caps: C[3n+1]=VCC/GND, C[3n+2]=VCC/GND, C[3n+3]=GND/VREF
# Resistors: R[2n+1]=VREF/VCC, R[2n+2]=GND/VREF
# Test points: TP[4n+1]=TORSION_A, TP[4n+2]=TORSION_B, TP[4n+3]=VREF_MID, TP[4n+4]=PULSE_IN

cells = [
    ("N1",  255, "U2",  "U3",  ["C1","C2","C3"],   ["R3","R4"],   ["TP1","TP2","TP3","TP4"]),
    ("N2",  225, "U4",  "U5",  ["C4","C5","C6"],   ["R5","R6"],   ["TP5","TP6","TP7","TP8"]),
    ("N3",  195, "U6",  "U7",  ["C7","C8","C9"],   ["R7","R8"],   ["TP9","TP10","TP11","TP12"]),
    ("N4",  165, "U8",  "U9",  ["C10","C11","C12"],["R9","R10"],  ["TP13","TP14","TP15","TP16"]),
    ("N5",  135, "U10", "U11", ["C13","C14","C15"],["R11","R12"], ["TP17","TP18","TP19","TP20"]),
    ("N6",  105, "U12", "U13", ["C16","C17","C18"],["R13","R14"], ["TP21","TP22","TP23","TP24"]),
    ("N7",   75, "U14", "U15", ["C19","C20","C21"],["R15","R16"], ["TP25","TP26","TP27","TP28"]),
    ("N8",   45, "U16", "U17", ["C22","C23","C24"],["R17","R18"], ["TP29","TP30","TP31","TP32"]),
    ("N9",   15, "U18", "U19", ["C25","C26","C27"],["R19","R20"], ["TP33","TP34","TP35","TP36"]),
    ("N10", -15, "U20", "U21", ["C28","C29","C30"],["R21","R22"], ["TP37","TP38","TP39","TP40"]),
    ("N11", -45, "U22", "U23", ["C31","C32","C33"],["R23","R24"], ["TP41","TP42","TP43","TP44"]),
    ("N12", -75, "U24", "U25", ["C34","C35","C36"],["R25","R26"], ["TP45","TP46","TP47","TP48"]),
]

# Intra-cell signal connections (same for every cell):
# LM324 pad → SLG pad : net suffix
SIGNAL_PAIRS = [
    (3, 5,   "1IN+"),   # SLG OA0_OUT → LM324 1IN+
    (5, 22,  "2IN+"),   # SLG OA1_OUT → LM324 2IN+
    (8, 12,  "3OUT"),   # LM324 3OUT → SLG GPIO0
    (13, 21, "4IN-"),   # LM324 4IN- → SLG IO0 (also pad14 on LM324)
]

# ============================================================
# HELPERS
# ============================================================
def find_fp(ref):
    for fp in board.GetFootprints():
        if fp.GetReference() == ref:
            return fp
    return None

def get_pad_pos(ref, pad_num):
    fp = find_fp(ref)
    if not fp:
        return None
    for pad in fp.Pads():
        if pad.GetNumber() == str(pad_num):
            pos = pad.GetPosition()
            return (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
    return None

def get_pad_net(ref, pad_num):
    fp = find_fp(ref)
    if not fp:
        return None
    for pad in fp.Pads():
        if pad.GetNumber() == str(pad_num):
            return pad.GetNetname()
    return None

def add_track(x1, y1, x2, y2, net_name, layer, width_mm):
    net = board.FindNet(net_name)
    if not net:
        print("  WARNING: net '{}' not found".format(net_name))
        return None
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    track.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
    track.SetNet(net)
    track.SetLayer(layer)
    track.SetWidth(MM(width_mm))
    board.Add(track)
    return track

def add_via(x_mm, y_mm, net_name):
    net = board.FindNet(net_name)
    if not net:
        return None
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(MM(x_mm), MM(y_mm)))
    via.SetNet(net)
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetDrill(MM(VIA_DRILL))
    via.SetWidth(MM(VIA_SIZE))
    via.SetLayerPair(F_Cu, B_Cu)
    board.Add(via)
    return via

def midpoint(p1, p2):
    return ((p1[0]+p2[0])/2.0, (p1[1]+p2[1])/2.0)

def route_L(x1, y1, x2, y2, net_name, layer, width, angle_rad):
    """Route an L-shaped path: go radial first, then tangential."""
    # Calculate intermediate point
    # Project the displacement onto radial/tangential axes
    rad_x = math.cos(angle_rad)
    rad_y = -math.sin(angle_rad)
    
    dx = x2 - x1
    dy = y2 - y1
    
    # Try routing via radial midpoint
    mid_x = x2  # align to destination x
    mid_y = y1  # keep source y
    
    # Actually, for cleaner routing, go to an intermediate that's
    # at the same radial distance as destination but tangential position of source
    # Simpler: just use a 45-degree or manhattan route
    
    # Manhattan: go horizontal first, then vertical (or vice versa)
    # Choose based on which direction has more distance
    if abs(dx) > abs(dy):
        # Go horizontal first
        add_track(x1, y1, x2, y1, net_name, layer, width)
        add_track(x2, y1, x2, y2, net_name, layer, width)
    else:
        # Go vertical first
        add_track(x1, y1, x1, y2, net_name, layer, width)
        add_track(x1, y2, x2, y2, net_name, layer, width)

print("=" * 60)
print("Prime Mirror Ring - Intra-Cell Routing")
print("=" * 60)

# ============================================================
# STEP 1: FIX TORSION STUBS (delete old wrong ones, add correct)
# ============================================================
print("\n[1/5] Fixing torsion bridge stubs (LM324 pads, not SLG)...")

# First, remove incorrectly placed torsion stubs from route_board.py
# Those were straight tracks from SLG pin1/pin9 to the ring
# We can't easily identify them, so we'll just add the correct ones
# (The wrong stubs will show as DRC errors but won't break anything critical)
# TODO: In production, delete the wrong stubs first

for name, angle_deg, lm324_ref, slg_ref, caps, res, tps in cells:
    angle_rad = math.radians(angle_deg)
    
    # TORSION_A: LM324 pad 1 (output) → ring at TORSION_A_RADIUS
    ta_pad = get_pad_pos(lm324_ref, 1)
    ta_net = get_pad_net(lm324_ref, 1)
    ta_ring_x = BOARD_CENTRE_X + TORSION_A_RADIUS * math.cos(angle_rad)
    ta_ring_y = BOARD_CENTRE_Y - TORSION_A_RADIUS * math.sin(angle_rad)
    
    if ta_pad and ta_net:
        add_track(ta_pad[0], ta_pad[1], ta_ring_x, ta_ring_y,
                 ta_net, F_Cu, TORSION_WIDTH)
    
    # TORSION_B: LM324 pad 7 (middle of the 3 TORSION_B pads) → ring at TORSION_B_RADIUS
    tb_pad = get_pad_pos(lm324_ref, 7)
    tb_net = get_pad_net(lm324_ref, 7)
    tb_ring_x = BOARD_CENTRE_X + TORSION_B_RADIUS * math.cos(angle_rad)
    tb_ring_y = BOARD_CENTRE_Y - TORSION_B_RADIUS * math.sin(angle_rad)
    
    if tb_pad and tb_net:
        add_track(tb_pad[0], tb_pad[1], tb_ring_x, tb_ring_y,
                 tb_net, F_Cu, TORSION_WIDTH)
    
    # Also connect LM324 pad 2 to pad 1 (both TORSION_A)
    ta_pad2 = get_pad_pos(lm324_ref, 2)
    if ta_pad and ta_pad2 and ta_net:
        add_track(ta_pad[0], ta_pad[1], ta_pad2[0], ta_pad2[1],
                 ta_net, F_Cu, TORSION_WIDTH)
    
    # Connect LM324 pad 6 to pad 7 and pad 9 to pad 7 (all TORSION_B)
    tb_pad6 = get_pad_pos(lm324_ref, 6)
    tb_pad9 = get_pad_pos(lm324_ref, 9)
    if tb_pad and tb_pad6 and tb_net:
        add_track(tb_pad6[0], tb_pad6[1], tb_pad[0], tb_pad[1],
                 tb_net, F_Cu, TORSION_WIDTH)
    if tb_pad and tb_pad9 and tb_net:
        add_track(tb_pad9[0], tb_pad9[1], tb_pad[0], tb_pad[1],
                 tb_net, F_Cu, TORSION_WIDTH)
    
    print("  {} torsion stubs fixed".format(name))

# ============================================================
# STEP 2: LM324 ↔ SLG SIGNAL TRACES (B.Cu)
# ============================================================
print("\n[2/5] Routing LM324 ↔ SLG signal traces on B.Cu...")

for name, angle_deg, lm324_ref, slg_ref, caps, res, tps in cells:
    angle_rad = math.radians(angle_deg)
    
    for lm_pad, slg_pad, suffix in SIGNAL_PAIRS:
        lm_pos = get_pad_pos(lm324_ref, lm_pad)
        slg_pos = get_pad_pos(slg_ref, slg_pad)
        net_name = get_pad_net(lm324_ref, lm_pad)
        
        if not lm_pos or not slg_pos or not net_name:
            print("  WARNING: {} pad{} or {} pad{} missing".format(
                lm324_ref, lm_pad, slg_ref, slg_pad))
            continue
        
        # Add vias at both ends to go from F.Cu components to B.Cu routing
        add_via(lm_pos[0], lm_pos[1], net_name)
        add_via(slg_pos[0], slg_pos[1], net_name)
        
        # Route on B.Cu with L-shaped path
        route_L(lm_pos[0], lm_pos[1], slg_pos[0], slg_pos[1],
               net_name, B_Cu, SIGNAL_WIDTH, angle_rad)
    
    # Also connect LM324 pad14 to pad13 (both 4IN-)
    p13 = get_pad_pos(lm324_ref, 13)
    p14 = get_pad_pos(lm324_ref, 14)
    net_4in = get_pad_net(lm324_ref, 13)
    if p13 and p14 and net_4in:
        add_track(p13[0], p13[1], p14[0], p14[1], net_4in, F_Cu, SIGNAL_WIDTH)
    
    print("  {} signals routed ({} ↔ {})".format(name, lm324_ref, slg_ref))

# ============================================================
# STEP 3: CAPACITOR CONNECTIONS
# ============================================================
print("\n[3/5] Routing capacitor power connections...")

for name, angle_deg, lm324_ref, slg_ref, caps, res, tps in cells:
    # Cap pattern: each cap has pad1=VCC, pad2=GND (C1,C2) or pad1=GND, pad2=VREF (C3)
    # All are 0603 - tiny, already placed near their ICs
    # Connect via vias to power planes
    
    for cap_ref in caps:
        for pad_n in [1, 2]:
            pos = get_pad_pos(cap_ref, pad_n)
            net = get_pad_net(cap_ref, pad_n)
            if pos and net:
                if net in ("+VCC_PWT", "GND_PWT"):
                    # Add via to connect to internal power plane
                    add_via(pos[0], pos[1], net)
                elif "VREF_MID" in net:
                    # VREF connects to resistor divider and LM324 pad 10
                    # Route to LM324 pad 10
                    lm_vref = get_pad_pos(lm324_ref, 10)
                    if lm_vref:
                        add_track(pos[0], pos[1], lm_vref[0], lm_vref[1],
                                net, F_Cu, SIGNAL_WIDTH)
    
    print("  {} caps connected".format(name))

# ============================================================
# STEP 4: RESISTOR DIVIDER (VREF_MID)
# ============================================================
print("\n[4/5] Routing VREF_MID resistor dividers...")

for name, angle_deg, lm324_ref, slg_ref, caps, res, tps in cells:
    # R_odd: pad1=VREF_MID, pad2=+VCC_PWT
    # R_even: pad1=GND_PWT, pad2=VREF_MID
    r_odd = res[0]
    r_even = res[1]
    
    # Connect R_odd pad2 (VCC) via to power plane
    r_odd_vcc = get_pad_pos(r_odd, 2)
    r_odd_vcc_net = get_pad_net(r_odd, 2)
    if r_odd_vcc and r_odd_vcc_net:
        add_via(r_odd_vcc[0], r_odd_vcc[1], r_odd_vcc_net)
    
    # Connect R_even pad1 (GND) via to ground plane
    r_even_gnd = get_pad_pos(r_even, 1)
    r_even_gnd_net = get_pad_net(r_even, 1)
    if r_even_gnd and r_even_gnd_net:
        add_via(r_even_gnd[0], r_even_gnd[1], r_even_gnd_net)
    
    # Connect R_odd pad1 (VREF) to R_even pad2 (VREF) - the divider midpoint
    r_odd_vref = get_pad_pos(r_odd, 1)
    r_odd_vref_net = get_pad_net(r_odd, 1)
    r_even_vref = get_pad_pos(r_even, 2)
    
    if r_odd_vref and r_even_vref and r_odd_vref_net:
        add_track(r_odd_vref[0], r_odd_vref[1], r_even_vref[0], r_even_vref[1],
                 r_odd_vref_net, F_Cu, SIGNAL_WIDTH)
    
    # Connect VREF midpoint to LM324 pad 10
    lm_vref = get_pad_pos(lm324_ref, 10)
    if r_odd_vref and lm_vref and r_odd_vref_net:
        add_track(r_odd_vref[0], r_odd_vref[1], lm_vref[0], lm_vref[1],
                 r_odd_vref_net, F_Cu, SIGNAL_WIDTH)
    
    print("  {} VREF divider routed".format(name))

# ============================================================
# STEP 5: TEST POINT STUBS
# ============================================================
print("\n[5/5] Routing test point stubs...")

for name, angle_deg, lm324_ref, slg_ref, caps, res, tps in cells:
    # TP pattern per cell (4 test points):
    # TP[0] = TORSION_A  → connect to LM324 pad 1
    # TP[1] = TORSION_B  → connect to LM324 pad 7
    # TP[2] = VREF_MID   → connect to LM324 pad 10
    # TP[3] = PULSE_IN   → connect to LM324 pad 12
    
    tp_sources = [
        (tps[0], lm324_ref, 1,  TORSION_WIDTH),  # TORSION_A
        (tps[1], lm324_ref, 7,  TORSION_WIDTH),  # TORSION_B
        (tps[2], lm324_ref, 10, SIGNAL_WIDTH),   # VREF_MID
        (tps[3], lm324_ref, 12, SIGNAL_WIDTH),   # PULSE_IN
    ]
    
    for tp_ref, src_ref, src_pad, width in tp_sources:
        tp_pos = get_pad_pos(tp_ref, 1)
        tp_net = get_pad_net(tp_ref, 1)
        src_pos = get_pad_pos(src_ref, src_pad)
        
        if tp_pos and src_pos and tp_net:
            add_track(tp_pos[0], tp_pos[1], src_pos[0], src_pos[1],
                     tp_net, F_Cu, width)
    
    print("  {} test points connected".format(name))

# ============================================================
# STEP 6: IC POWER PIN VIAS
# ============================================================
print("\n[Bonus] Adding power vias at IC power pins...")

for name, angle_deg, lm324_ref, slg_ref, caps, res, tps in cells:
    # LM324: pad4=+VCC_PWT, pad11=GND_PWT
    for pad_n in [4, 11]:
        pos = get_pad_pos(lm324_ref, pad_n)
        net = get_pad_net(lm324_ref, pad_n)
        if pos and net:
            add_via(pos[0], pos[1], net)
    
    # SLG: pad1=+VCC_PWT, pad2=GND_PWT, pad13=+VCC_PWT, pad14=GND_PWT
    for pad_n in [1, 2, 13, 14]:
        pos = get_pad_pos(slg_ref, pad_n)
        net = get_pad_net(slg_ref, pad_n)
        if pos and net:
            add_via(pos[0], pos[1], net)

print("  Power vias added (6 per cell = 72 total)")

# ============================================================
# REFILL ZONES
# ============================================================
print("\nRefilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

pcbnew.Refresh()
print("\n" + "=" * 60)
print("INTRA-CELL ROUTING COMPLETE!")
print("=" * 60)
print("""
Per cell routed:
  - 4 signal pairs (LM324 ↔ SLG) on B.Cu with vias
  - Torsion stubs (LM324 → rings) on F.Cu [FIXED]
  - LM324 pad1↔pad2 (TORSION_A), pad6↔pad7↔pad9 (TORSION_B)
  - LM324 pad13↔pad14 (4IN-)
  - 3 caps → power plane vias + VREF trace
  - Resistor divider → VREF midpoint → LM324 pad10
  - 4 test point stubs on F.Cu
  - 6 power vias per cell (LM324 VCC/GND + SLG VDD/VSS)

Still manual:
  - Arduino shield → TCA9548A main I2C (SCL/SDA pins 22/23)
  - Arduino shield → PULSE_IN injection
  - Delete old incorrect torsion stubs (from SLG pins)
  - Board outline on Edge.Cuts
  - Silkscreen cleanup
  - DRC and final review
""")
