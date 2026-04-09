"""
SC4: Layered IADS
==================
Three-layer integrated air defense with 6 SAMs across 3 depth bands.
Two F-35A strikers + two MQ-58 jammers must penetrate layered defenses
to strike a hardened C2 bunker and an ammo depot at depth.

Fleet: 2x F-35A + 2x MQ-58
SAMs:  2x Buk-M2 (layer 1), 2x HQ-9 (layer 2), 2x S-300 (layer 3)
HVTs:  2 (C2 Bunker + Ammo Depot)

Result: OPTIMAL, 0.00% gap, 270s
"""

# -- Scenario geometry (all positions in km) --

FLEET = [
    {"name": "F-35A-1", "platform": "F-35A", "role": "striker",
     "start": (-100, 0), "target": "HVT-A", "weapon": "JDAM_2000"},
    {"name": "F-35A-2", "platform": "F-35A", "role": "striker",
     "start": (100, 0),  "target": "HVT-B", "weapon": "JDAM_2000"},
    {"name": "MQ-58A",  "platform": "MQ-58", "role": "jammer",
     "start": (-60, 40)},
    {"name": "MQ-58B",  "platform": "MQ-58", "role": "jammer",
     "start": (60, 40)},
]

SAMS = [
    # Layer 1: short-range point defense (y=120)
    {"name": "Buk-M2 West",  "type": "Buk-M2", "pos": (-40, 120), "R_km": 15},
    {"name": "Buk-M2 East",  "type": "Buk-M2", "pos": (40, 120),  "R_km": 15},
    # Layer 2: medium-range area defense (y=220)
    {"name": "HQ-9 West",    "type": "HQ-9",   "pos": (-90, 220), "R_km": 50},
    {"name": "HQ-9 East",    "type": "HQ-9",   "pos": (90, 220),  "R_km": 50},
    # Layer 3: long-range strategic defense (y=320)
    {"name": "S-300 West",   "type": "S-300",   "pos": (-70, 320), "R_km": 40},
    {"name": "S-300 East",   "type": "S-300",   "pos": (70, 320),  "R_km": 40},
]

RADARS = [
    {"name": "Radar-EW", "pos": (0, 180), "R_km": 120},
]

HVTS = [
    {"name": "HVT-A", "label": "C2 Bunker",  "pos": (-50, 450),
     "hardness_kg_tnt": 2000, "hardened": True},
    {"name": "HVT-B", "label": "Ammo Depot", "pos": (50, 450),
     "hardness_kg_tnt": 200},
]

EXIT = {"pos": (250, 450), "tolerance_km": 50}

# -- Solver parameters --
SOLVER = {
    "dt": 60,
    "N": 50,
    "S": 5,
    "solver_time_limit": 600,
    "gap_limit": 0.001,
    "objective_mode": "lexicographic",
    "escort_jam_mode": True,
    "max_simultaneous_fcr_jam": 3,
}