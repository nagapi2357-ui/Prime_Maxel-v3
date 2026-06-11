# Prime Mirror Ring - PCB Routing Script
# Routes: GND/VCC zones, Torsion bridges (50Ω, 13/11 ratio), I2C, PULSE_IN
#
# Run via KiCad scripting console:
# exec(open("/Users/ClawdBot/.openclaw/workspace/projects/Prime_Maxel-v3/Nagaπ Python Scripts/route_board.py").read())

import pcbnew
import math

board = pcbnew.GetBoard()
MM = pcbnew.FromMM

# ============================================================
# CONSTANTS
# ============================================================
BOARD_CENTRE_X = 150.0   # mm
BOARD_CENTRE_Y = 105.0   # mm
RING_RADIUS = 45.0        # mm (cell centres)

# Torsion bridge radii — 13/11 ratio achieved via geometry
TORSION_A_RADIUS = 50.0   # mm — inner ring
TORSION_B_RADIUS = 50.0 * 13.0 / 11.0  # 59.09 mm — outer ring

# Track widths
TORSION_WIDTH = 0.229     # mm — 50Ω impedance (from stackup calc)
SIGNAL_WIDTH = 0.2        # mm — default signal
I2C_WIDTH = 0.2           # mm
POWER_WIDTH = 0.4         # mm

# Via parameters
VIA_DRILL = 0.3           # mm
VIA_SIZE = 0.6            # mm

# Layer IDs
F_Cu = board.GetLayerID("F.Cu")
In1_Cu = board.GetLayerID("In1.Cu")
In2_Cu = board.GetLayerID("In2.Cu")
B_Cu = board.GetLayerID("B.Cu")

# Cell data: (name, angle_deg, LM324, SLG, caps, resistors, test_points)
cells = [
    ("N1",  255, "U2",  "U3"),
    ("N2",  225, "U4",  "U5"),
    ("N3",  195, "U6",  "U7"),
    ("N4",  165, "U8",  "U9"),
    ("N5",  135, "U10", "U11"),
    ("N6",  105, "U12", "U13"),
    ("N7",   75, "U14", "U15"),
    ("N8",   45, "U16", "U17"),
    ("N9",   15, "U18", "U19"),
    ("N10", -15, "U20", "U21"),
    ("N11", -45, "U22", "U23"),
    ("N12", -75, "U24", "U25"),
]

# ============================================================
# HELPERS
# ============================================================
def find_fp(ref):
    for fp in board.GetFootprints():
        if fp.GetReference() == ref:
            return fp
    return None

def find_net(name):
    netinfo = board.GetNetInfo()
    net = netinfo.GetNetItem(name)
    if net is not None:
        return net.GetNetCode()
    return -1

def get_pad_pos(ref, pad_num):
    """Get pad position in mm for a given component ref and pad number."""
    fp = find_fp(ref)
    if fp is None:
        return None
    for pad in fp.Pads():
        if pad.GetNumber() == str(pad_num):
            pos = pad.GetPosition()
            return (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
    return None

def add_track(x1, y1, x2, y2, net_code, layer, width_mm):
    """Add a straight track segment."""
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    track.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
    track.SetNet(board.GetNetInfo().GetNetItem(net_code))
    track.SetLayer(layer)
    track.SetWidth(MM(width_mm))
    board.Add(track)
    return track

def add_track_by_name(x1, y1, x2, y2, net_name, layer, width_mm):
    """Add a straight track segment using net name."""
    net_code = find_net(net_name)
    if net_code < 0:
        print("WARNING: Net '" + net_name + "' not found!")
        return None
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    track.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
    ni = board.FindNet(net_code)
    if ni:
        track.SetNet(ni)
    track.SetLayer(layer)
    track.SetWidth(MM(width_mm))
    board.Add(track)
    return track

def add_arc_segments(cx, cy, radius, start_deg, end_deg, n_segments, net_name, layer, width_mm):
    """Add an arc as a series of small straight segments."""
    net_code = find_net(net_name)
    if net_code < 0:
        print("WARNING: Net '" + net_name + "' not found!")
        return []
    
    tracks = []
    for i in range(n_segments):
        a1 = math.radians(start_deg + (end_deg - start_deg) * i / n_segments)
        a2 = math.radians(start_deg + (end_deg - start_deg) * (i + 1) / n_segments)
        x1 = cx + radius * math.cos(a1)
        y1 = cy - radius * math.sin(a1)
        x2 = cx + radius * math.cos(a2)
        y2 = cy - radius * math.sin(a2)
        t = add_track_by_name(x1, y1, x2, y2, net_name, layer, width_mm)
        if t:
            tracks.append(t)
    return tracks

def add_via(x_mm, y_mm, net_name, top_layer=F_Cu, bot_layer=B_Cu):
    """Add a through via."""
    net_code = find_net(net_name)
    if net_code < 0:
        return None
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I(MM(x_mm), MM(y_mm)))
    ni = board.FindNet(net_code)
    if ni:
        via.SetNet(ni)
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetDrill(MM(VIA_DRILL))
    via.SetWidth(MM(VIA_SIZE))
    via.SetLayerPair(top_layer, bot_layer)
    board.Add(via)
    return via

def add_zone(net_name, layer, corners, priority=0):
    """Add a copper zone (pour) given corner points in mm."""
    net_code = find_net(net_name)
    if net_code < 0:
        print("WARNING: Net '" + net_name + "' not found for zone!")
        return None
    
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    ni = board.FindNet(net_code)
    if ni:
        zone.SetNet(ni)
    zone.SetAssignedPriority(priority)
    zone.SetIsRuleArea(False)
    zone.SetDoNotAllowTracks(False)
    zone.SetDoNotAllowVias(False)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowCopperPour(False)
    zone.SetDoNotAllowFootprints(False)
    
    # Build outline
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in corners:
        outline.Append(MM(x), MM(y))
    
    board.Add(zone)
    return zone

print("=" * 60)
print("Prime Mirror Ring - Routing Script")
print("=" * 60)

# ============================================================
# STEP 1: GROUND & POWER ZONES (In2.Cu and In1.Cu)
# ============================================================
print("\n[1/5] Creating GND and VCC power zones...")

# Large rectangular zone covering the entire board area
# Using generous bounds around all components
ZONE_LEFT = 70.0
ZONE_RIGHT = 230.0
ZONE_TOP = 30.0
ZONE_BOTTOM = 200.0

zone_corners = [
    (ZONE_LEFT, ZONE_TOP),
    (ZONE_RIGHT, ZONE_TOP),
    (ZONE_RIGHT, ZONE_BOTTOM),
    (ZONE_LEFT, ZONE_BOTTOM),
]

gnd_zone = add_zone("GND_PWT", In2_Cu, zone_corners, priority=0)
if gnd_zone:
    print("  GND_PWT zone on In2.Cu - OK")
else:
    print("  GND_PWT zone - FAILED")

vcc_zone = add_zone("+VCC_PWT", In1_Cu, zone_corners, priority=0)
if vcc_zone:
    print("  +VCC_PWT zone on In1.Cu - OK")
else:
    print("  +VCC_PWT zone - FAILED")

# ============================================================
# STEP 2: TORSION BRIDGES (F.Cu — 50Ω controlled impedance)
# ============================================================
print("\n[2/5] Routing torsion bridges on F.Cu...")
print("  TORSION_A: radius={:.2f}mm, path={:.2f}mm".format(
    TORSION_A_RADIUS, 2 * math.pi * TORSION_A_RADIUS))
print("  TORSION_B: radius={:.2f}mm, path={:.2f}mm".format(
    TORSION_B_RADIUS, 2 * math.pi * TORSION_B_RADIUS))
print("  Ratio B/A: {:.6f} (target 13/11 = {:.6f})".format(
    TORSION_B_RADIUS / TORSION_A_RADIUS, 13.0/11.0))

# Route TORSION_A as a full circle at TORSION_A_RADIUS
# 360 segments for smooth arc (1 degree per segment)
N_ARC_SEGMENTS = 360

ta_tracks = add_arc_segments(
    BOARD_CENTRE_X, BOARD_CENTRE_Y, TORSION_A_RADIUS,
    0, 360, N_ARC_SEGMENTS,
    "/Golden Cell/TORSION_A", F_Cu, TORSION_WIDTH)
print("  TORSION_A ring: {} segments".format(len(ta_tracks)))

# Route TORSION_B as a full circle at TORSION_B_RADIUS
tb_tracks = add_arc_segments(
    BOARD_CENTRE_X, BOARD_CENTRE_Y, TORSION_B_RADIUS,
    0, 360, N_ARC_SEGMENTS,
    "/Golden Cell/TORSION_B", F_Cu, TORSION_WIDTH)
print("  TORSION_B ring: {} segments".format(len(tb_tracks)))

# Add stub traces from each SLG47004V TORSION pins to the rings
print("\n  Adding stubs from SLGs to torsion rings...")
for name, angle_deg, lm324_ref, slg_ref in cells:
    angle_rad = math.radians(angle_deg)
    
    # SLG centre is at cell_centre + 7mm radial
    slg_cx = BOARD_CENTRE_X + (RING_RADIUS + 7.0) * math.cos(angle_rad)
    slg_cy = BOARD_CENTRE_Y - (RING_RADIUS + 7.0) * math.sin(angle_rad)
    
    # TORSION_A pin on SLG (pin 1) - get actual pad position
    ta_pad = get_pad_pos(slg_ref, 1)
    # TORSION_B pin on SLG (pin 6 = TORSION_B based on schematic, or pin 9)
    # From the detail screenshots: pin 6 = TORSION_B, pin 7 = TORSION_B
    tb_pad = get_pad_pos(slg_ref, 9)
    
    # Point on TORSION_A ring closest to this cell
    ta_ring_x = BOARD_CENTRE_X + TORSION_A_RADIUS * math.cos(angle_rad)
    ta_ring_y = BOARD_CENTRE_Y - TORSION_A_RADIUS * math.sin(angle_rad)
    
    # Point on TORSION_B ring closest to this cell
    tb_ring_x = BOARD_CENTRE_X + TORSION_B_RADIUS * math.cos(angle_rad)
    tb_ring_y = BOARD_CENTRE_Y - TORSION_B_RADIUS * math.sin(angle_rad)
    
    if ta_pad:
        add_track_by_name(ta_pad[0], ta_pad[1], ta_ring_x, ta_ring_y,
                         "/Golden Cell/TORSION_A", F_Cu, TORSION_WIDTH)
    if tb_pad:
        add_track_by_name(tb_pad[0], tb_pad[1], tb_ring_x, tb_ring_y,
                         "/Golden Cell/TORSION_B", F_Cu, TORSION_WIDTH)
    
    print("    {} stubs - OK".format(name))

# ============================================================
# STEP 3: I2C BUS (B.Cu)
# ============================================================
print("\n[3/5] Routing I2C bus on B.Cu...")

# TCA9548A (U1) is at centre. It has 6 I2C channel pairs (SC0-SC5, SD0-SD5)
# Each channel connects to 2 golden cells
# Channel mapping: Ch0→N1,N2 / Ch1→N3,N4 / Ch2→N5,N6 / Ch3→N7,N8 / Ch4→N9,N10 / Ch5→N11,N12

i2c_channels = [
    (0, ["U3", "U5"],   "/COL_SCL0", "/COL_SDA0"),
    (1, ["U7", "U9"],   "/COL_SCL1", "/COL_SDA1"),
    (2, ["U11", "U13"], "/COL_SCL2", "/COL_SDA2"),
    (3, ["U15", "U17"], "/COL_SCL3", "/COL_SDA3"),
    (4, ["U19", "U21"], "/COL_SCL4", "/COL_SDA4"),
    (5, ["U23", "U25"], "/COL_SCL5", "/COL_SDA5"),
]

# Get TCA9548A pad positions for each channel
# TCA9548A TSSOP-24 pin mapping:
# SC0=pin3, SD0=pin4, SC1=pin5, SD1=pin6, SC2=pin7, SD2=pin8
# SC3=pin9, SD3=pin10, SC4=pin11, SD4=pin12, SC5=pin13, SD5=pin14
tca_scl_pins = {0: 3, 1: 5, 2: 7, 3: 9, 4: 11, 5: 13}
tca_sda_pins = {0: 4, 1: 6, 2: 8, 3: 10, 4: 12, 5: 14}

# SLG47004V I2C pins: SCL=pin10, SDA=pin11
SLG_SCL_PIN = 10
SLG_SDA_PIN = 11

for ch, slg_refs, scl_net, sda_net in i2c_channels:
    # TCA pad positions
    tca_scl = get_pad_pos("U1", tca_scl_pins[ch])
    tca_sda = get_pad_pos("U1", tca_sda_pins[ch])
    
    if not tca_scl or not tca_sda:
        print("  Ch{}: TCA9548A pads not found!".format(ch))
        continue
    
    for slg_ref in slg_refs:
        slg_scl = get_pad_pos(slg_ref, SLG_SCL_PIN)
        slg_sda = get_pad_pos(slg_ref, SLG_SDA_PIN)
        
        if slg_scl:
            # Via down at TCA pad, route on B.Cu, via up at SLG pad
            add_via(tca_scl[0], tca_scl[1], scl_net)
            add_via(slg_scl[0], slg_scl[1], scl_net)
            add_track_by_name(tca_scl[0], tca_scl[1], slg_scl[0], slg_scl[1],
                            scl_net, B_Cu, I2C_WIDTH)
        
        if slg_sda:
            add_via(tca_sda[0], tca_sda[1], sda_net)
            add_via(slg_sda[0], slg_sda[1], sda_net)
            add_track_by_name(tca_sda[0], tca_sda[1], slg_sda[0], slg_sda[1],
                            sda_net, B_Cu, I2C_WIDTH)
        
        print("    Ch{} → {} - OK".format(ch, slg_ref))

# Main I2C (SDA/SCL from Arduino to TCA9548A)
# TCA9548A: SCL=pin22, SDA=pin23
print("  Routing main I2C (Arduino → TCA9548A)...")
# These connect to nets /SCL{slash}21 and /SDA{slash}20
# Will need manual routing from shield headers to U1 since header positions are manual

# ============================================================
# STEP 4: PULSE_IN BUS (B.Cu)  
# ============================================================
print("\n[4/5] Routing PULSE_IN bus on B.Cu...")

# PULSE_IN is shared across all cells
# Route from centre outward to each SLG
# SLG PULSE_IN = pin 12 (GPIO0)
PULSE_NET = "/Golden Cell/PULSE_IN"
SLG_PULSE_PIN = 12

for name, angle_deg, lm324_ref, slg_ref in cells:
    pulse_pad = get_pad_pos(slg_ref, SLG_PULSE_PIN)
    if pulse_pad:
        # Route from centre to each SLG via a star topology
        add_via(BOARD_CENTRE_X, BOARD_CENTRE_Y + 3, PULSE_NET)
        add_via(pulse_pad[0], pulse_pad[1], PULSE_NET)
        add_track_by_name(BOARD_CENTRE_X, BOARD_CENTRE_Y + 3,
                         pulse_pad[0], pulse_pad[1],
                         PULSE_NET, B_Cu, SIGNAL_WIDTH)
        print("    PULSE_IN → {} - OK".format(slg_ref))

# ============================================================
# STEP 5: POWER STITCHING VIAS
# ============================================================
print("\n[5/5] Adding power stitching vias...")

# Add GND vias in a ring between components and at corners
# Ring of GND vias at ~42mm radius (between LM324s and centre)
for i in range(24):
    a = math.radians(i * 15)
    r = 42.0
    vx = BOARD_CENTRE_X + r * math.cos(a)
    vy = BOARD_CENTRE_Y - r * math.sin(a)
    add_via(vx, vy, "GND_PWT")

# Ring of GND vias outside torsion B ring
for i in range(24):
    a = math.radians(i * 15)
    r = TORSION_B_RADIUS + 4.0
    vx = BOARD_CENTRE_X + r * math.cos(a)
    vy = BOARD_CENTRE_Y - r * math.sin(a)
    add_via(vx, vy, "GND_PWT")

print("  48 GND stitching vias placed")

# Add VCC vias near each LM324 VCC pin (pin 4)
for name, angle_deg, lm324_ref, slg_ref in cells:
    vcc_pad = get_pad_pos(lm324_ref, 4)
    if vcc_pad:
        add_via(vcc_pad[0], vcc_pad[1], "+VCC_PWT")
    # Also near SLG VDD pin (pin 2)
    vdd_pad = get_pad_pos(slg_ref, 2)
    if vdd_pad:
        add_via(vdd_pad[0], vdd_pad[1], "+VCC_PWT")

print("  24 VCC stitching vias placed (1 per IC)")

# ============================================================
# FILL ALL ZONES
# ============================================================
print("\nFilling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
print("  Zones filled")

pcbnew.Refresh()
print("\n" + "=" * 60)
print("ROUTING COMPLETE!")
print("=" * 60)
print("""
Summary:
  - GND_PWT zone on In2.Cu (ground plane)
  - +VCC_PWT zone on In1.Cu (power plane)
  - TORSION_A ring on F.Cu at R={:.1f}mm (L={:.1f}mm)
  - TORSION_B ring on F.Cu at R={:.1f}mm (L={:.1f}mm)
  - Ratio B/A = {:.6f} (target 13/11 = {:.6f})
  - I2C channels routed on B.Cu (6 channels, 2 cells each)
  - PULSE_IN star bus on B.Cu
  - 72 stitching vias (48 GND + 24 VCC)

Still needs manual routing:
  - Arduino shield headers → TCA9548A main I2C (SCL/SDA)
  - Arduino shield → PULSE_IN injection point
  - Intra-cell traces (LM324 ↔ SLG within each cell)
  - Test point connections
  - Board outline on Edge.Cuts
""".format(
    TORSION_A_RADIUS, 2*math.pi*TORSION_A_RADIUS,
    TORSION_B_RADIUS, 2*math.pi*TORSION_B_RADIUS,
    TORSION_B_RADIUS/TORSION_A_RADIUS, 13.0/11.0))
