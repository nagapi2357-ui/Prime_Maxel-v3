#!/usr/bin/env python3
"""
Great Pyramid of Giza — Comprehensive Dimensional Analysis in Royal Cubits
===========================================================================

Sources:
  - W.M.F. Petrie, "The Pyramids and Temples of Gizeh" (1883)
  - J.H. Cole, "Determination of the Exact Size and Orientation of the
    Great Pyramid of Giza" (Survey of Egypt, Paper No. 39, 1925)
  - Glen Dash Foundation surveys (2015)
  - Rudolf Gantenbrink, robotic surveys of shafts (1993)
  - I.E.S. Edwards, "The Pyramids of Egypt" (1993 rev.)
  - Mark Lehner, "The Complete Pyramids" (1997)
  - Wikipedia (compiled modern consensus)

Royal Cubit convention: 1 RC = 0.5236 m  (7 palms × 4 fingers = 28 fingers)
  This value is back-derived: 230.36 m / 440 = 0.52354 m (Cole);
  Petrie's 9068.8 inches = 230.348 m / 440 = 0.52352 m.
  The canonical 0.5236 m is used throughout Egyptological literature.
"""

import math
from dataclasses import dataclass
from typing import Optional

# ─── Constants ──────────────────────────────────────────────────────────────

RC = 0.5236                # 1 Royal Cubit in metres
PI = math.pi
PHI = (1 + math.sqrt(5)) / 2   # Golden ratio ≈ 1.6180339887
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)
SQRT5 = math.sqrt(5)

def m_to_rc(m: float) -> float:
    """Convert metres to Royal Cubits."""
    return m / RC

def rc_to_m(rc: float) -> float:
    """Convert Royal Cubits to metres."""
    return rc * RC

def inches_to_m(inches: float) -> float:
    """Convert British inches to metres."""
    return inches * 0.0254

def dms_to_deg(d: int, m: int, s: float) -> float:
    """Degrees-minutes-seconds to decimal degrees."""
    return d + m / 60.0 + s / 3600.0


# ═══════════════════════════════════════════════════════════════════════════
# 1. EXTERNAL DIMENSIONS
# ═══════════════════════════════════════════════════════════════════════════

print("=" * 80)
print("GREAT PYRAMID OF GIZA — DIMENSIONAL ANALYSIS IN ROYAL CUBITS")
print("=" * 80)

# --- Base side lengths (Cole 1925 survey, the modern standard) ---
# Cole measured the base at pavement level:
#   North: 230.253 m    East: 230.391 m    South: 230.454 m    West: 230.357 m
# Petrie (1883): mean 9068.8 inches = 230.348 m

cole_sides_m = {
    'North': 230.253,
    'East':  230.391,
    'South': 230.454,
    'West':  230.357,
}
cole_mean_m = sum(cole_sides_m.values()) / 4  # 230.36375

# Petrie's value
petrie_base_inches = 9068.8
petrie_base_m = inches_to_m(petrie_base_inches)

# DESIGN VALUES (consensus):
BASE_CUBITS = 440        # exact design intent
HEIGHT_CUBITS = 280      # exact design intent

base_m = rc_to_m(BASE_CUBITS)
height_m = rc_to_m(HEIGHT_CUBITS)

print("\n── 1. EXTERNAL DIMENSIONS ──\n")
print("Base side lengths (Cole 1925 survey):")
for side, val in cole_sides_m.items():
    print(f"  {side:6s}: {val:.3f} m = {m_to_rc(val):.3f} RC")
print(f"  Mean  : {cole_mean_m:.3f} m = {m_to_rc(cole_mean_m):.3f} RC")
print(f"  Max variation: {max(cole_sides_m.values()) - min(cole_sides_m.values()):.3f} m "
      f"= {m_to_rc(max(cole_sides_m.values()) - min(cole_sides_m.values())):.3f} RC")
print(f"\nPetrie base mean: {petrie_base_m:.3f} m = {m_to_rc(petrie_base_m):.3f} RC")
print(f"\nDESIGN base: {BASE_CUBITS} RC = {base_m:.3f} m")

# Implied cubit length from Cole mean
implied_cubit_cole = cole_mean_m / 440
print(f"\nImplied cubit from Cole mean: {implied_cubit_cole:.6f} m")
print(f"Implied cubit from Petrie mean: {petrie_base_m / 440:.6f} m")
print(f"Standard cubit used: {RC:.4f} m")

# --- Height ---
# Original height with pyramidion: 280 cubits
# Petrie estimated height from slope angle: 5776.0 ± 7.0 inches = 146.71 m
petrie_height_inches = 5776.0
petrie_height_m = inches_to_m(petrie_height_inches)

print(f"\nOriginal height: {HEIGHT_CUBITS} RC = {height_m:.3f} m")
print(f"Petrie height estimate: {petrie_height_m:.3f} m = {m_to_rc(petrie_height_m):.3f} RC")

# --- Slope angle ---
# Seked = 5.5 palms per cubit rise = 5.5/7 run per unit rise
# tan(slope) = rise/run = 1 / (5.5/7) = 7/5.5 = 14/11
seked = 5.5  # palms
slope_tan = 7.0 / seked  # = 14/11
slope_rad = math.atan(slope_tan)
slope_deg = math.degrees(slope_rad)
slope_dms = dms_to_deg(51, 50, 40)

print(f"\nSlope angle:")
print(f"  From seked 5½: tan⁻¹(14/11) = {slope_deg:.6f}° = 51°50'{slope_deg * 60 % 60:.1f}\"")
print(f"  Petrie measured: 51°50'40\" = {slope_dms:.6f}°")
print(f"  Difference: {abs(slope_deg - slope_dms) * 3600:.1f} arc-seconds")

# --- Apothem (slant height of face from base midpoint to apex) ---
# apothem = height / cos(slope from vertical) = height / sin(slope from horizontal)
# Or: apothem² = height² + (base/2)²  ... NO, that's using half-base horizontal
# apothem = height / sin(slope) ... NO
# apothem = sqrt(height² + (base/2)²) where base/2 is horizontal distance
half_base_cubits = BASE_CUBITS / 2  # = 220
apothem_cubits = math.sqrt(HEIGHT_CUBITS**2 + half_base_cubits**2)
apothem_m = rc_to_m(apothem_cubits)

print(f"\nApothem (slant height of face):")
print(f"  = √(h² + (b/2)²) = √({HEIGHT_CUBITS}² + {half_base_cubits}²)")
print(f"  = √({HEIGHT_CUBITS**2} + {half_base_cubits**2}) = √{HEIGHT_CUBITS**2 + half_base_cubits**2}")
print(f"  = {apothem_cubits:.6f} RC = {apothem_m:.3f} m")

# --- Edge length (corner to apex) ---
# Half-diagonal of base = (base/2) * √2 = 220√2
half_diag_cubits = half_base_cubits * SQRT2
edge_cubits = math.sqrt(HEIGHT_CUBITS**2 + half_diag_cubits**2)
edge_m = rc_to_m(edge_cubits)

print(f"\nEdge length (corner to apex):")
print(f"  Half-diagonal = {half_base_cubits}√2 = {half_diag_cubits:.6f} RC")
print(f"  Edge = √(h² + half_diag²) = √({HEIGHT_CUBITS**2} + {half_diag_cubits**2:.2f})")
print(f"  = {edge_cubits:.6f} RC = {edge_m:.3f} m")

# --- Perimeter ---
perimeter_cubits = 4 * BASE_CUBITS
perimeter_m = rc_to_m(perimeter_cubits)
print(f"\nPerimeter: {perimeter_cubits} RC = {perimeter_m:.3f} m")

# --- Areas ---
base_area_cubits2 = BASE_CUBITS**2
face_area_cubits2 = 0.5 * BASE_CUBITS * apothem_cubits
total_lateral_area = 4 * face_area_cubits2
total_surface_area = base_area_cubits2 + total_lateral_area

print(f"\nBase area: {base_area_cubits2} RC² = {rc_to_m(1)**2 * base_area_cubits2:.1f} m²")
print(f"Single face area: {face_area_cubits2:.2f} RC² = {RC**2 * face_area_cubits2:.1f} m²")
print(f"Total lateral area: {total_lateral_area:.2f} RC² = {RC**2 * total_lateral_area:.1f} m²")
print(f"Total surface area: {total_surface_area:.2f} RC² = {RC**2 * total_surface_area:.1f} m²")


# ═══════════════════════════════════════════════════════════════════════════
# 2. INTERNAL CHAMBERS AND PASSAGES
# ═══════════════════════════════════════════════════════════════════════════

print("\n\n── 2. INTERNAL CHAMBERS AND PASSAGES ──\n")

@dataclass
class Chamber:
    name: str
    length_m: float
    width_m: float
    height_m: float
    notes: str = ""

# King's Chamber (Petrie measurements, extremely precise)
# Length: 10.47 m (E-W), Width: 5.23 m (N-S), Height: 5.82 m
# Petrie: L = 412.40", W = 206.12", H = 230.09" (to lowest point of ceiling)
# Note: 2:1 ratio in plan; height relates to diagonal

kings = Chamber("King's Chamber",
    length_m=10.47,    # 20 cubits
    width_m=5.234,     # 10 cubits  
    height_m=5.852,    # ~11.18 cubits ≈ 10√(5/4)? Actually ~5√5 cubits
    notes="Granite. Petrie: L=412.40\", W=206.12\", H=230.09\"")

# Queen's Chamber
# Length: 5.75 m (E-W), Width: 5.23 m (N-S), Height: 6.26 m (peak of gable)
# Walls to gable spring: 4.67 m
queens = Chamber("Queen's Chamber",
    length_m=5.75,
    width_m=5.23,
    height_m=6.26,     # to peak of pointed ceiling
    notes="Limestone. Niche in east wall: ~4.67m high, ~1.57m wide at base")

# Niche dimensions (stepped, corbelled)
queens_niche_height_m = 4.67
queens_niche_width_base_m = 1.57
queens_niche_depth_m = 1.04

# Grand Gallery
# Length: 46.68 m (along slope), Width: 2.09 m (floor), Height: 8.60 m
# Corbelled walls narrow to ~1.04 m at top
# Slope: same as ascending passage ≈ 26°2'30" (Petrie)
grand_gallery = Chamber("Grand Gallery",
    length_m=46.68,     # along slope
    width_m=2.09,       # floor width between ramps
    height_m=8.60,      # 
    notes="Slope ~26°2'30\". Corbelled ceiling. Ramp benches each side ~0.51m wide")

# Ascending Passage
asc_passage_length_m = 39.3    # along slope (Petrie ~1546 inches)
asc_passage_angle = dms_to_deg(26, 2, 30)

# Descending Passage  
desc_passage_length_m = 105.23  # total length along slope (built + rock-cut)
desc_passage_angle = dms_to_deg(26, 26, 46)

# Subterranean Chamber
subterranean = Chamber("Subterranean Chamber",
    length_m=14.08,   # E-W (Petrie: ~554 inches)
    width_m=8.28,     # N-S (Petrie: ~326 inches)  
    height_m=3.18,    # rough, unfinished
    notes="Unfinished. Cut in bedrock ~30m below base level")

chambers = [kings, queens, grand_gallery, subterranean]

for c in chambers:
    l_rc = m_to_rc(c.length_m)
    w_rc = m_to_rc(c.width_m)
    h_rc = m_to_rc(c.height_m)
    print(f"{c.name}:")
    print(f"  Length: {c.length_m:.3f} m = {l_rc:.3f} RC")
    print(f"  Width:  {c.width_m:.3f} m = {w_rc:.3f} RC")
    print(f"  Height: {c.height_m:.3f} m = {h_rc:.3f} RC")
    if c.notes:
        print(f"  Notes:  {c.notes}")
    print()

print("King's Chamber analysis:")
kl = m_to_rc(kings.length_m)
kw = m_to_rc(kings.width_m)
kh = m_to_rc(kings.height_m)
print(f"  L = {kl:.4f} RC  (design: 20 RC)")
print(f"  W = {kw:.4f} RC  (design: 10 RC)")
print(f"  H = {kh:.4f} RC  (design: ???)")
print(f"  L:W ratio = {kl/kw:.6f}  (should be 2.0)")
print(f"  Floor diagonal = √(L² + W²) = √({kl:.2f}² + {kw:.2f}²) = {math.sqrt(kl**2+kw**2):.4f} RC")
print(f"  10√5 = {10*math.sqrt(5):.4f}  — floor diagonal in design cubits: √(20²+10²) = √500 = 10√5")
kh_design = math.sqrt(kl**2 + kw**2) / 2  # half the floor diagonal as height?
print(f"  H ≈ ½ × floor diagonal = {kh_design:.4f} RC  → {kh_design:.4f} vs measured {kh:.4f}")
print(f"  5√5 = {5*SQRT5:.4f}")
print(f"  H/W = {kh/kw:.6f}  (√(5)/2 = {SQRT5/2:.6f}?  No.)")
# Actually Petrie's height 230.09 inches = 5.8443 m → 11.161 RC
# Design: height such that room diagonal = 2 × width?  
# Actually: h = √(20² + 10²) / 2 is one theory... let's check
# Another: KC height = 10 × √(Φ) ? 
print(f"  10√Φ = {10*math.sqrt(PHI):.4f}")
print(f"  Note: Petrie's precise H = 230.09\" = {inches_to_m(230.09):.4f} m = {m_to_rc(inches_to_m(230.09)):.4f} RC")

print(f"\nQueen's Chamber analysis:")
ql = m_to_rc(queens.length_m)
qw = m_to_rc(queens.width_m)
qh = m_to_rc(queens.height_m)
print(f"  L = {ql:.4f} RC  (~11 RC)")
print(f"  W = {qw:.4f} RC  (~10 RC)")
print(f"  H = {qh:.4f} RC  (~12 RC, to gable peak)")
print(f"  Niche height: {m_to_rc(queens_niche_height_m):.3f} RC")
print(f"  Niche width (base): {m_to_rc(queens_niche_width_base_m):.3f} RC")

print(f"\nGrand Gallery analysis:")
gl = m_to_rc(grand_gallery.length_m)
gw = m_to_rc(grand_gallery.width_m)
gh = m_to_rc(grand_gallery.height_m)
print(f"  Length (slope): {gl:.4f} RC")
print(f"  Width (floor):  {gw:.4f} RC  (~4 RC)")
print(f"  Height:         {gh:.4f} RC")

print(f"\nPassages:")
print(f"  Ascending Passage:")
print(f"    Length (slope): {asc_passage_length_m:.2f} m = {m_to_rc(asc_passage_length_m):.3f} RC")
print(f"    Angle: {asc_passage_angle:.4f}° = 26°2'30\"")
print(f"    tan(26°2'30\") = {math.tan(math.radians(asc_passage_angle)):.6f}  (≈ 1/2 = 0.5)")
print(f"  Descending Passage:")
print(f"    Length (slope): {desc_passage_length_m:.2f} m = {m_to_rc(desc_passage_length_m):.3f} RC")
print(f"    Angle: {desc_passage_angle:.4f}° = 26°26'46\"")
print(f"    tan(26°26'46\") = {math.tan(math.radians(desc_passage_angle)):.6f}  (≈ 1/2)")

print(f"\nSubterranean Chamber:")
sl = m_to_rc(subterranean.length_m)
sw = m_to_rc(subterranean.width_m)
sh = m_to_rc(subterranean.height_m)
print(f"  L = {sl:.4f} RC")
print(f"  W = {sw:.4f} RC")
print(f"  H = {sh:.4f} RC")


# ═══════════════════════════════════════════════════════════════════════════
# 3. SHAFT ANGLES
# ═══════════════════════════════════════════════════════════════════════════

print("\n\n── 3. SHAFT ANGLES ──\n")
print("(Gantenbrink 1993 robotic survey; Petrie 1883 for some)")

# Shaft angles (Gantenbrink's Upuaut project, 1993)
shafts = {
    "King's Chamber - North (lower opening)":  32.60,   # ~32°36' Gantenbrink
    "King's Chamber - South (lower opening)":  45.00,   # 45°00' ± some variation
    "Queen's Chamber - North":                 39.60,   # ~39°36' (varies along length: 39°07' to 39°42')
    "Queen's Chamber - South":                 39.67,   # ~39°40' (varies: 38°28' to 39°42')
}

# More precise values from various sources:
# KC North: Petrie 31°33', Gantenbrink 32°36' (bends)
# KC South: Petrie 44°26', Gantenbrink 45°00' (with bends)  
# QC North: Gantenbrink mean ~39°07'28"
# QC South: Gantenbrink mean ~39°36'28"

shafts_precise = {
    "King's Chamber - North":  {"angle": dms_to_deg(32, 36, 0),  "petrie": dms_to_deg(31, 33, 0)},
    "King's Chamber - South":  {"angle": dms_to_deg(45, 0, 0),   "petrie": dms_to_deg(44, 26, 0)},
    "Queen's Chamber - North": {"angle": dms_to_deg(39, 7, 28),  "petrie": None},
    "Queen's Chamber - South": {"angle": dms_to_deg(39, 36, 28), "petrie": None},
}

for name, data in shafts_precise.items():
    a = data["angle"]
    print(f"  {name}:")
    print(f"    Gantenbrink: {a:.4f}°")
    if data["petrie"]:
        print(f"    Petrie:      {data['petrie']:.4f}°")
    print(f"    sin = {math.sin(math.radians(a)):.6f}, cos = {math.cos(math.radians(a)):.6f}, tan = {math.tan(math.radians(a)):.6f}")
    print()


# ═══════════════════════════════════════════════════════════════════════════
# 4. MATHEMATICAL RELATIONSHIPS
# ═══════════════════════════════════════════════════════════════════════════

print("\n\n── 4. MATHEMATICAL RELATIONSHIPS ──\n")

# --- π relationships ---
print("─ π Relationships ─")
print()
ratio_peri_height = perimeter_cubits / HEIGHT_CUBITS
print(f"  Perimeter / Height = {perimeter_cubits} / {HEIGHT_CUBITS} = {ratio_peri_height:.10f}")
print(f"  2π = {2 * PI:.10f}")
print(f"  Difference: {abs(ratio_peri_height - 2*PI):.10f}")
print(f"  Error: {abs(ratio_peri_height - 2*PI) / (2*PI) * 100:.6f}%")
print(f"  → 1760/280 = 44/7 = {44/7:.10f} vs 2π = {2*PI:.10f}")
print(f"  → This is the 22/7 approximation of π: 22/7 = {22/7:.10f} vs π = {PI:.10f}")
print(f"     Error of 22/7: {abs(22/7 - PI)/PI * 100:.6f}%")
print()

# half-perimeter / height = π
half_peri = perimeter_cubits / 2
print(f"  Half-perimeter / Height = {half_peri} / {HEIGHT_CUBITS} = {half_peri/HEIGHT_CUBITS:.10f}")
print(f"  π = {PI:.10f}")
print()

# Apothem relationship  
print(f"  Apothem / half-base = {apothem_cubits:.6f} / {half_base_cubits} = {apothem_cubits/half_base_cubits:.10f}")
print(f"  → Compare to Φ = {PHI:.10f}")
print(f"  Difference: {abs(apothem_cubits/half_base_cubits - PHI):.10f}")
print(f"  Error: {abs(apothem_cubits/half_base_cubits - PHI)/PHI * 100:.6f}%")
print()

# --- Φ (Golden Ratio) relationships ---
print("─ Φ (Golden Ratio) Relationships ─")
print()
# apothem/half-base ≈ Φ
print(f"  Apothem / (Base/2):")
print(f"    = {apothem_cubits:.6f} / {half_base_cubits}")
print(f"    = {apothem_cubits/half_base_cubits:.10f}")
print(f"    Φ = {PHI:.10f}")
print(f"    Error: {abs(apothem_cubits/half_base_cubits - PHI)/PHI * 100:.6f}%")
print()

# Check: if apothem/half-base = Φ exactly, then height/half-base = √(Φ²-1) = √(Φ+1) = √(Φ²-1)
# Φ² = Φ+1, so Φ²-1 = Φ, so √(Φ²-1) = √Φ
# height/half-base = 280/220 = 14/11
print(f"  Height / (Base/2) = {HEIGHT_CUBITS}/{half_base_cubits} = {HEIGHT_CUBITS/half_base_cubits:.10f}")
print(f"  √Φ = {math.sqrt(PHI):.10f}")
print(f"  14/11 = {14/11:.10f}")
print(f"  Difference (h/half-b vs √Φ): {abs(HEIGHT_CUBITS/half_base_cubits - math.sqrt(PHI)):.10f}")
print(f"  Error: {abs(HEIGHT_CUBITS/half_base_cubits - math.sqrt(PHI))/math.sqrt(PHI) * 100:.6f}%")
print()

# Face area / base area
print(f"  Single face area / (Base/2)² = Φ ?")
face_area_over_halfbase_sq = face_area_cubits2 / half_base_cubits**2
print(f"    = {face_area_cubits2:.2f} / {half_base_cubits**2}")
print(f"    = {face_area_over_halfbase_sq:.10f}")
print(f"    Φ = {PHI:.10f}")
print(f"    Error: {abs(face_area_over_halfbase_sq - PHI)/PHI * 100:.6f}%")
print()

# --- √2, √3, √5 relationships ---
print("─ √2, √3, √5 Relationships ─")
print()
print(f"  Base diagonal = {BASE_CUBITS}√2 = {BASE_CUBITS * SQRT2:.4f} RC")
print(f"  Half-diagonal = {half_base_cubits}√2 = {half_base_cubits * SQRT2:.4f} RC")
print(f"  KC floor diagonal = √(20² + 10²) = √500 = 10√5 = {10*SQRT5:.4f} RC")
print(f"  KC space diagonal = √(20² + 10² + h²)")
kc_h_design = m_to_rc(inches_to_m(230.09))  # Petrie's precise measurement
print(f"    with h = {kc_h_design:.4f} RC: = {math.sqrt(400 + 100 + kc_h_design**2):.4f} RC")
print(f"    with h = 5√5: space diag = √(400+100+125) = √625 = 25 RC (!!)")
print()
print(f"  If KC height = 5√5 = {5*SQRT5:.4f} RC = {rc_to_m(5*SQRT5):.4f} m")
print(f"    Petrie measured: {inches_to_m(230.09):.4f} m = {kc_h_design:.4f} RC")
print(f"    Difference: {abs(kc_h_design - 5*SQRT5):.4f} RC = {abs(rc_to_m(kc_h_design) - rc_to_m(5*SQRT5))*100:.2f} cm")
print()

# --- Integer & near-integer cubit values ---
print("─ Integer and Near-Integer Cubit Values ─")
print()
print(f"  Base side:     {BASE_CUBITS} RC  ← EXACT INTEGER (design)")
print(f"  Height:        {HEIGHT_CUBITS} RC  ← EXACT INTEGER (design)")
print(f"  Perimeter:     {perimeter_cubits} RC  ← EXACT INTEGER")
print(f"  Half-base:     {half_base_cubits} RC  ← EXACT INTEGER")
print(f"  KC length:     ≈ 20 RC (design)")
print(f"  KC width:      ≈ 10 RC (design)")
print(f"  KC height:     ≈ {kc_h_design:.3f} RC  (not integer — √5 relationship?)")
print(f"  Apothem:       {apothem_cubits:.4f} RC  (not integer)")
print(f"  Edge:          {edge_cubits:.4f} RC  (not integer)")
print()

# --- Prime numbers ---
print("─ Prime Numbers in Cubit Dimensions ─")
print()
primes_small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
                127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191,
                193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263,
                269, 271, 277, 281, 283]

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

dims_to_check = {
    "Base": BASE_CUBITS,
    "Height": HEIGHT_CUBITS,
    "Perimeter": perimeter_cubits,
    "Half-base": int(half_base_cubits),
    "Base/2": int(half_base_cubits),
}

for name, val in dims_to_check.items():
    factors = []
    n = val
    for p in primes_small:
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.append(n)
    print(f"  {name} = {val} = {' × '.join(str(f) for f in factors)}"
          f"  {'← PRIME' if is_prime(val) else ''}")

print()
print(f"  Note: 440 = 2³ × 5 × 11")
print(f"         280 = 2³ × 5 × 7")
print(f"        1760 = 2⁵ × 5 × 11")
print(f"  GCD(440, 280) = 40 = 2³ × 5")
print(f"  440/280 = 11/7  (ratio involves primes 7 and 11)")
print()

# --- Fibonacci numbers ---
print("─ Fibonacci Numbers ─")
fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
print(f"  Fibonacci sequence: {fibs[:12]}")
print(f"  440 is NOT Fibonacci")
print(f"  280 is NOT Fibonacci")
print(f"  But: 440/280 = 11/7")
print(f"  Consecutive Fibonacci ratio 8/5 = {8/5} → but 11/7 = {11/7:.6f}")
print(f"  Φ = lim(F(n+1)/F(n)) = {PHI:.6f}")
print()

# --- Pythagorean relationships ---
print("─ Pythagorean Relationships ─")
print()
print(f"  The slope triangle (half-section):")
print(f"    Base (half) = 220, Height = 280, Apothem = {apothem_cubits:.4f}")
print(f"    220² + 280² = {220**2} + {280**2} = {220**2 + 280**2}")
print(f"    Apothem² = {apothem_cubits**2:.4f}")
print(f"    √{220**2 + 280**2} = {math.sqrt(220**2 + 280**2):.4f}")
print()
print(f"  Simplify: divide by 20: 11² + 14² = {11**2 + 14**2} = {11**2} + {14**2}")
print(f"    √317 = {math.sqrt(317):.6f}  (NOT a perfect square → not Pythagorean triple)")
print()
print(f"  KC: 20 × 10 × h")
print(f"    If h = 5√5: 10² + (5√5)² = 100 + 125 = 225 = 15²  → 10:5√5:15 ? No, 10² + h² ≠ 15²")
print(f"    Nope. But 20² + 10² = 500 = (10√5)² ← floor diagonal")
print(f"    20:10:(10√5) is the Pythagorean relationship: simplified 2:1:√5")
print()

# --- Relationships to 360, 365.25 ---
print("─ Relationships to 360, 365.25 ─")
print()
print(f"  Perimeter in RC = {perimeter_cubits}")
print(f"  1760 / 4 = {1760/4} (base)")
print(f"  Base in metres = {base_m:.3f}")
print(f"  Perimeter / 2 = {perimeter_cubits/2}")
print(f"  1760 / (2π) = {1760/(2*PI):.4f} ≈ {HEIGHT_CUBITS} (the height — this IS the π relationship)")
print()
print(f"  365.25 (days in year):")
print(f"    Perimeter in metres ≈ {perimeter_m:.2f} m")
print(f"    Half-base in cubits = 220")
print(f"    Base diagonal in cubits = {BASE_CUBITS * SQRT2:.2f}")
print(f"    No obvious 365.25 relationship in the cubit values")
print()
print(f"  360 (degrees in circle):")
print(f"    Diodorus reported workforce of 360,000 — probably symbolic")
print(f"    No direct relationship to 360 in core dimensions")
print()


# --- The π − Φ² relationship ---
print("─ The 'Cubit Constant': π − Φ² ─")
print()
cubit_const = PI - PHI**2
print(f"  π − Φ² = {PI:.10f} − {PHI**2:.10f} = {cubit_const:.10f}")
print(f"  Actual RC in metres = {RC}")
print(f"  (π − Φ²) = {cubit_const:.6f}")
print(f"  This is a numerical curiosity: π − Φ² ≈ 0.5236")
print(f"  Φ² = Φ + 1 = {PHI + 1:.10f}")
print(f"  So π − Φ² = π − Φ − 1 = {PI - PHI - 1:.10f}")
print()
print(f"  Royal Cubit = {RC} m")
print(f"  π − Φ²     = {cubit_const:.10f}")
print(f"  Match to 4 decimal places: {'YES' if round(RC, 4) == round(cubit_const, 4) else 'NO'}")
print(f"  Exact difference: {abs(RC - cubit_const):.10f} m = {abs(RC - cubit_const)*1000:.7f} mm")
print()

# ═══════════════════════════════════════════════════════════════════════════
# 5. THE π − Φ² RECURSION
# ═══════════════════════════════════════════════════════════════════════════

print("\n── 5. π − Φ² RECURSION IN DIMENSION RATIOS ──\n")

print("Checking ratios between dimensions for π, Φ, π/6:")
print()

# All major dimensions in cubits
dims = {
    "Base":         BASE_CUBITS,
    "Height":       HEIGHT_CUBITS,
    "Half-base":    half_base_cubits,
    "Apothem":      apothem_cubits,
    "Edge":         edge_cubits,
    "Perimeter":    perimeter_cubits,
    "KC Length":    20.0,
    "KC Width":     10.0,
    "KC Height":    kc_h_design,
}

# Check all ratios
constants_to_check = {
    "π":      PI,
    "π/2":    PI/2,
    "π/3":    PI/3,
    "π/4":    PI/4,
    "π/6":    PI/6,
    "2π":     2*PI,
    "Φ":      PHI,
    "Φ²":     PHI**2,
    "1/Φ":    1/PHI,
    "√Φ":     math.sqrt(PHI),
    "√2":     SQRT2,
    "√3":     SQRT3,
    "√5":     SQRT5,
    "π−Φ²":   cubit_const,
    "e":      math.e,
}

print("Notable ratios (error < 1%):")
dim_names = list(dims.keys())
for i in range(len(dim_names)):
    for j in range(len(dim_names)):
        if i == j:
            continue
        a_name, a_val = dim_names[i], dims[dim_names[i]]
        b_name, b_val = dim_names[j], dims[dim_names[j]]
        if b_val == 0:
            continue
        ratio = a_val / b_val
        for const_name, const_val in constants_to_check.items():
            if const_val == 0:
                continue
            error = abs(ratio - const_val) / const_val
            if error < 0.01:  # Less than 1% error
                print(f"  {a_name}/{b_name} = {ratio:.6f} ≈ {const_name} = {const_val:.6f}  (error: {error*100:.4f}%)")

print()
print("Does π/6 appear?")
print(f"  π/6 = {PI/6:.6f}")
print(f"  KC Width / KC Length = {10/20:.6f} = 0.5  (not π/6)")
print(f"  Height / Perimeter = {HEIGHT_CUBITS/perimeter_cubits:.6f}  (= 1/2π ≈ {1/(2*PI):.6f})")
print(f"  1/(2π) = {1/(2*PI):.6f} — yes this is the π relationship again")
print()


# ═══════════════════════════════════════════════════════════════════════════
# 6. ASTRONOMICAL / FRINGE CLAIMS
# ═══════════════════════════════════════════════════════════════════════════

print("\n── 6. ASTRONOMICAL ALIGNMENTS & FRINGE CLAIMS ──\n")

# Shaft angles — stellar alignments (c. 2500 BC)
print("Shaft angles and proposed stellar alignments (c. 2500 BC):")
print(f"  KC South shaft (~45°): Aimed at Orion's Belt (Al Nitak) transit altitude")
print(f"  KC North shaft (~32.5°): Aimed at Thuban (Alpha Draconis, pole star)")
print(f"  QC South shaft (~39.5°): Aimed at Sirius transit altitude")
print(f"  QC North shaft (~39°): Aimed at Kochab (Beta Ursae Minoris)")
print(f"  Note: These alignments depend on precise epoch and precession calculations.")
print(f"  Bauval & Gilbert (1994) popularized these; contested by Krupp and others.")
print()

# Speed of light claim
print("Speed of light encoding claim:")
c_light = 299792458  # m/s
lat_pyramid = 29.9792458  # degrees N
print(f"  Pyramid latitude: {lat_pyramid}° N")
print(f"  Speed of light:   {c_light} m/s = 2.99792458 × 10⁸")
print(f"  Claim: latitude encodes speed of light")
print(f"  VERDICT: COINCIDENCE.")
print(f"    - The metre was defined in 1791; ancient Egyptians used cubits")
print(f"    - The latitude to that precision requires modern GPS")  
print(f"    - The pyramid covers ~230m; its centre latitude depends on which point you pick")
print(f"    - The specific digits match because there are only so many digits at ~30°N")
print(f"    - Latitude 29.9792° corresponds to a point ~250m from the actual centre")
print()

# Earth dimensions claim
print("Earth dimensions encoding claim:")
earth_polar_radius_m = 6356752  # m
earth_equatorial_circumference_m = 40075017  # m

print(f"  Pyramid height × 43,200 = {HEIGHT_CUBITS * RC * 43200:.0f} m")
print(f"  Earth polar radius = {earth_polar_radius_m} m")
print(f"  Ratio: {earth_polar_radius_m / (HEIGHT_CUBITS * RC * 43200):.6f}")
print(f"  Error: {abs(earth_polar_radius_m / (HEIGHT_CUBITS * RC * 43200) - 1) * 100:.3f}%")
print()
print(f"  Pyramid perimeter × 43,200 = {perimeter_cubits * RC * 43200:.0f} m")
print(f"  Earth equatorial circumference = {earth_equatorial_circumference_m} m")
print(f"  Ratio: {earth_equatorial_circumference_m / (perimeter_cubits * RC * 43200):.6f}")
print(f"  Error: {abs(earth_equatorial_circumference_m / (perimeter_cubits * RC * 43200) - 1) * 100:.3f}%")
print()
print(f"  The 43,200 factor = 2 × 360 × 60 (minutes in 12 hours)")
print(f"  VERDICT: INTERESTING APPROXIMATION but likely coincidence.")
print(f"    - 43,200 is cherry-picked to make the numbers work")
print(f"    - Any pyramid with a similar height would give a similar result with some multiplier")
print(f"    - The ~1% error is larger than the pyramid's construction precision")
print(f"    - However, the π relationship in the design IS real (via seked)")
print()


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("SUMMARY TABLE — ALL DIMENSIONS")
print("=" * 80)
print()
print(f"{'Dimension':<35} {'Metres':>12} {'Royal Cubits':>14} {'Design RC':>12}")
print("-" * 75)

summary = [
    ("EXTERNAL", None, None, None),
    ("Base side (Cole mean)", cole_mean_m, m_to_rc(cole_mean_m), "440"),
    ("Base side (design)", base_m, BASE_CUBITS, "440"),
    ("  North (Cole)", cole_sides_m['North'], m_to_rc(cole_sides_m['North']), "~440"),
    ("  East (Cole)", cole_sides_m['East'], m_to_rc(cole_sides_m['East']), "~440"),
    ("  South (Cole)", cole_sides_m['South'], m_to_rc(cole_sides_m['South']), "~440"),
    ("  West (Cole)", cole_sides_m['West'], m_to_rc(cole_sides_m['West']), "~440"),
    ("Height (original)", height_m, HEIGHT_CUBITS, "280"),
    ("Apothem (slant height)", apothem_m, apothem_cubits, f"√(280²+220²)"),
    ("Edge (corner to apex)", edge_m, edge_cubits, "√(280²+220²·2)"),
    ("Perimeter", perimeter_m, perimeter_cubits, "1760"),
    ("Half-base", rc_to_m(half_base_cubits), half_base_cubits, "220"),
    ("Base diagonal", rc_to_m(BASE_CUBITS*SQRT2), BASE_CUBITS*SQRT2, "440√2"),
    ("", None, None, None),
    ("INTERNAL", None, None, None),
    ("King's Chamber L", kings.length_m, m_to_rc(kings.length_m), "20"),
    ("King's Chamber W", kings.width_m, m_to_rc(kings.width_m), "10"),
    ("King's Chamber H", kings.height_m, m_to_rc(kings.height_m), "~5√5?"),
    ("Queen's Chamber L", queens.length_m, m_to_rc(queens.length_m), "~11"),
    ("Queen's Chamber W", queens.width_m, m_to_rc(queens.width_m), "~10"),
    ("Queen's Chamber H (gable)", queens.height_m, m_to_rc(queens.height_m), "~12"),
    ("Grand Gallery L (slope)", grand_gallery.length_m, m_to_rc(grand_gallery.length_m), "~89?"),
    ("Grand Gallery W (floor)", grand_gallery.width_m, m_to_rc(grand_gallery.width_m), "~4"),
    ("Grand Gallery H", grand_gallery.height_m, m_to_rc(grand_gallery.height_m), "~16.4"),
    ("Ascending Passage L", asc_passage_length_m, m_to_rc(asc_passage_length_m), "~75"),
    ("Descending Passage L", desc_passage_length_m, m_to_rc(desc_passage_length_m), "~201"),
    ("Subterranean Ch. L", subterranean.length_m, m_to_rc(subterranean.length_m), "~27"),
    ("Subterranean Ch. W", subterranean.width_m, m_to_rc(subterranean.width_m), "~16"),
]

for row in summary:
    name, m_val, rc_val, design = row
    if m_val is None:
        if name:
            print(f"\n  {name}")
        continue
    print(f"  {name:<33} {m_val:>10.3f} m  {rc_val:>12.4f}    {design:>10}")

print()
print("=" * 80)
print("MATHEMATICAL RELATIONSHIPS — CLASSIFICATION")
print("=" * 80)
print()
print("EXACT (by design):")
print("  • Base = 440 RC, Height = 280 RC, Perimeter = 1760 RC")
print("  • Base/Height = 440/280 = 11/7 (seked = 5½ palms)")
print("  • KC: 20 × 10 RC (2:1 ratio)")
print(f"  • Passage angles ≈ 26°26' (tan ≈ 1/2, rise:run = 1:2)")
print()
print("VERY CLOSE APPROXIMATIONS (likely intentional via seked choice):")
print(f"  • Perimeter/Height = 2π (error {abs(44/7 - 2*PI)/(2*PI)*100:.4f}%, from 22/7 ≈ π)")
print(f"  • Apothem/Half-base ≈ Φ (error {abs(apothem_cubits/half_base_cubits - PHI)/PHI*100:.4f}%)")
print(f"  • Height/Half-base ≈ √Φ (error {abs(14/11 - math.sqrt(PHI))/math.sqrt(PHI)*100:.4f}%)")
print(f"  • Face area / (half-base)² ≈ Φ (same relationship)")
print()
print("NUMERICAL COINCIDENCES:")
print(f"  • π − Φ² = {cubit_const:.6f} ≈ 0.5236 m (1 Royal Cubit)")
print(f"    Remarkable to 4 decimal places. Likely coincidence since the cubit")
print(f"    was based on forearm length, not mathematical constants.")
print(f"  • Latitude ≈ speed of light digits (coincidence)")
print(f"  • 43,200× scaling to Earth dimensions (~1% match)")
print()
print("KEY INSIGHT:")
print("  The seked of 5½ palms (rise:run = 14:11) SIMULTANEOUSLY encodes:")
print(f"    - π (via 22/7): perimeter = 2π × height")
print(f"    - Φ (via √(1+(14/11)²) / 1 = apothem/half-base)")
print("  Whether this was intentional or an emergent property of the seked")
print("  choice remains debated. The Rhind Papyrus shows Egyptians used")
print("  sekeds for slope calculation; there is no evidence they knew π or Φ")
print("  as abstract constants. However, the geometric relationships are real.")
print()
print("  The deep reason π and Φ both appear: for ANY pyramid with slope angle θ,")
print("  if 4/tan(θ) ≈ π, then sec(θ) ≈ Φ automatically, because")
print("  sec(arctan(4/π)) = √(1 + 16/π²) ≈ 1.6189... ≈ Φ = 1.6180...")
print("  So encoding π automatically gives you Φ (approximately). One relationship")
print("  implies the other; they are NOT independent discoveries.")
