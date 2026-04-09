"""
SC1: Corridor Strike
=====================
Baseline escort-jam scenario. Two F-35A strikers + one MQ-58 jammer
navigate a narrow corridor defended by two short-range SAMs and one
medium-range SAM to strike two HVTs.

Fleet: 2x F-35A + 1x MQ-58
SAMs:  2x Buk-M2, 1x S-300
HVTs:  2 (Depot + Airfield)

Result: OPTIMAL, 0.77% gap, 120s
"""

# -- Scenario geometry (all positions in km) --

FLEET = [
    {"name": "F-35A-1", "platform": "F-35A", "role": "striker",
     "start": (-40, 0), "target": "HVT-A", "weapon": "JDAM_2000"},
    {"name": "F-35A-2", "platform": "F-35A", "role": "striker",
     "start": (40, 0), "target": "HVT-B", "weapon": "JDAM_2000"},
    {"name": "MQ-58",   "platform": "MQ-58", "role": "jammer",
     "start": (0, 30)},
]

SAMS = [
    {"name": "Buk-M2 West",  "type": "Buk-M2",  "pos": (-30, 100), "R_km": 15},
    {"name": "Buk-M2 East",  "type": "Buk-M2",  "pos": (30, 100),  "R_km": 15},
    {"name": "S-300 Flank",  "type": "S-300",    "pos": (80, 200),  "R_km": 40},
]

RADARS = [
    {"name": "Radar-EW", "pos": (0, 80), "R_km": 100},
]

HVTS = [
    {"name": "HVT-A", "label": "Depot",    "pos": (-20, 300), "hardness_kg_tnt": 200},
    {"name": "HVT-B", "label": "Airfield", "pos": (40, 300),  "hardness_kg_tnt": 1000},
]

EXIT = {"pos": (200, 350), "tolerance_km": 30}

# -- Solver parameters --
SOLVER = {
    "dt": 60,              # seconds per slot
    "N": 35,               # time horizon (slots)
    "S": 5,                # spatial scale (units per km)
    "solver_time_limit": 120,
    "gap_limit": 0.001,
    "objective_mode": "lexicographic",
    "escort_jam_mode": True,
    "max_simultaneous_fcr_jam": 3,
}