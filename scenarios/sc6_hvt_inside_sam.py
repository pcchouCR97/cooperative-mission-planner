"""
SC6: HVT Inside SAM Coverage
==============================
Both high-value targets are located inside overlapping S-300 engagement
zones. Standoff weapons cannot reach -- strikers must penetrate the MEZ,
requiring active escort jamming. This is the only scenario in the suite
where the jammer activates (21 jam slots).

Fleet: 2x F-35A + 1x MQ-58
SAMs:  2x S-300, 1x Buk-M2
HVTs:  2 (both inside SAM coverage)

Result: OPTIMAL, 0.01% gap, 154s, 21 jam slots active
"""

# -- Scenario geometry (all positions in km) --

FLEET = [
    {"name": "F-35A-1", "platform": "F-35A", "role": "striker",
     "start": (-40, 0), "target": "HVT-West", "weapon": "JDAM_2000"},
    {"name": "F-35A-2", "platform": "F-35A", "role": "striker",
     "start": (40, 0),  "target": "HVT-East", "weapon": "JDAM_2000"},
    {"name": "MQ-58",   "platform": "MQ-58", "role": "jammer",
     "start": (0, 80)},
]

SAMS = [
    {"name": "S-300 West",  "type": "S-300",  "pos": (-70, 200), "R_km": 40},
    {"name": "S-300 East",  "type": "S-300",  "pos": (70, 200),  "R_km": 40},
    {"name": "Buk-M2 Fwd", "type": "Buk-M2", "pos": (0, 100),   "R_km": 15},
]

RADARS = [
    {"name": "Radar-EW", "pos": (0, 150), "R_km": 100},
]

HVTS = [
    {"name": "HVT-West", "label": "Target West", "pos": (-20, 200),
     "hardness_kg_tnt": 200},
    {"name": "HVT-East", "label": "Target East", "pos": (20, 200),
     "hardness_kg_tnt": 200},
]

EXIT = {"pos": (100, 300), "tolerance_km": 30}

# -- IADS C2 network --
IADS_LINKS = {
    "Radar-EW": ["S-300 West", "S-300 East", "Buk-M2 Fwd"],
}

# -- Solver parameters --
SOLVER = {
    "dt": 60,
    "N": 40,
    "S": 5,
    "solver_time_limit": 300,
    "gap_limit": 0.001,
    "objective_mode": "lexicographic",
    "escort_jam_mode": True,
    "max_simultaneous_fcr_jam": 3,
}