# Solver Architecture

## Overview

The solver uses a five-layer hierarchical decomposition that separates combinatorial assignment
from continuous trajectory optimization. Only Layer 4 invokes the CP-SAT solver; Layers 0-3
run in milliseconds and reduce the problem before the solver sees it.

## Pipeline

```
Scenario Config (fleet, threats, targets, terrain)
       |
[L0]  Payload Advisor
       |  - Burn-through range analysis
       |  - J/S feasibility check
       |  - Weapon-geometry coupling assessment
       |  - Runtime: ~1.9 ms
       |
[L1]  Fleet Divider
       |  - Greedy threat-to-team assignment
       |  - Jammer allocation (jam budget formula)
       |  - Output: team assignments
       |
[L2]  DAG Scheduler
       |  - Wave ordering via Kahn's algorithm
       |  - Dependency: shared jammer transfers between sectors
       |  - Runtime: ~0.02 ms
       |
[L3]  Transfer Router
       |  - A* routing for jammer repositioning between waves
       |  - Threat-aware corridors (avoid active SAM coverage)
       |  - Runtime: ~170 ms
       |
[L4]  Trajectory Solver (per team)
       |  - Google OR-Tools CP-SAT
       |  - CDCL(T) lazy clause generation
       |  - 16-worker parallel search
       |  - Integer-only arithmetic (all positions scaled by S=5 units/km)
       |
   OPTIMAL trajectories + mission schedule + fuel report
```

## Precompute Pipeline (inside Layer 4)

Before the CP-SAT model is built, four preprocessing stages reduce the search space:

1. **Infeasibility audit**: verify all agents can physically reach their targets and exit
   within N time slots. Detects impossible missions in < 1 second (vs 600s solver timeout).

2. **Jam budget computation**: calculate minimum slots for each jammer to reach jam position,
   hold jam, and egress. Drop provably redundant jammers.

3. **Backward reachability domain tightening**: for each agent and slot, compute the set of
   positions from which the exit point is still reachable. Tightens variable domains by ~31%
   at the midpoint of the trajectory.

4. **Fleet reduction**: remove agents that cannot contribute to any target assignment.

Typical reduction: 40-60% fewer variables and constraints before the solver starts.

## Solver Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Solver | OR-Tools CP-SAT | CDCL(T) with lazy clause generation |
| Workers | 16 | Parallel search threads |
| Time limit | 120-600s | Scenario-dependent |
| Gap tolerance | 0.1% | Terminates when proven within this bound |
| Arithmetic | Integer-only | Positions scaled by S=5 (200m resolution) |
| Linearization | Level 2 | CP-SAT internal linearization |

## Key Design Decisions

**Why CP-SAT over Gurobi/SCIP?**
- Free, no license management for research
- Native `OnlyEnforceIf` for conditional constraints (cleaner than big-M reification)
- Multi-threaded out of the box
- Integer-only arithmetic matches the discrete time-slot formulation naturally

**Why lexicographic over weighted-sum?**
- Weighted-sum requires hand-tuning relative weights
- Lexicographic makes priority structural: one unjammed SAM exposure always outweighs
  any amount of time savings, by construction
- Empirically faster: 0.00% gap on SC2 in 12s (vs 0.98% with weighted-sum)

**Why octagonal over Manhattan?**
- Manhattan (diamond) over-approximates the Euclidean circle by 41% at diagonals
- Agents exploit this by flying diagonal "zig-zag" trajectories through SAM gaps that
  don't exist in reality
- Octagon reduces error to 7.6% with zero extra integer variables