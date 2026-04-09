# Scenario Guide

How to read the scenario definitions and result figures.

## Scenario Config Structure

Each scenario in `scenarios/` defines:

| Field | Description |
|-------|-------------|
| `FLEET` | List of agents with platform type, role, start position, and weapon |
| `SAMS` | List of SAM batteries with type, position, and engagement radius |
| `RADARS` | Early warning radars with position and detection radius |
| `HVTS` | High-value targets with position and hardness |
| `EXIT` | Egress point with tolerance radius |
| `SOLVER` | Time discretization, horizon, and solver parameters |

## Reading the Result Figures

Each scenario figure has two panels:

### Left: Trajectory Map

- **Blue lines**: F-35A striker trajectories
- **Red/pink dashed lines**: MQ-58 jammer trajectories
- **Red triangles**: SAM positions with concentric threat rings
  - Inner ring (dark): hard-kill zone (no entry without jamming)
  - Middle ring: lethal envelope (P_k > 50%)
  - Outer ring (light): missile engagement zone (P_k 5-50%)
- **Green stars**: HVT target positions
- **Blue square**: Exit point
- **Black X markers**: Agent start positions

### Right: Mission Schedule (Gantt Chart)

- **Blue bars**: Agent in transit
- **Green bars**: Strike window (weapon delivery)
- **Orange bars**: Active jamming window
- **Pink bars**: SAM engagement timeline
- Timeline in minutes (slot * dt/60)

## Scenario Suite

| ID | Name | Fleet | SAMs | Key Feature |
|----|------|-------|------|-------------|
| SC1 | Corridor Strike | 2x F-35A + MQ-58 | 3 | Baseline escort-jam |
| SC2 | Flanking Maneuver | F-35A + 2x MQ-58 | 4 | Dual-jammer crossfire |
| SC3 | SAM Wall | 2x F-35A + MQ-58 | 6 | Linear SAM barrier |
| SC4 | Layered IADS | 2x F-35A + 2x MQ-58 | 6 | Three-depth-layer defense |
| SC5 | Dense IADS + S-400 | 3x F-35A + MQ-58 | 8 | Hardest scenario (S-400 anchor) |
| SC6 | HVT Inside SAM | 2x F-35A + MQ-58 | 3 | Only scenario requiring active jam |

## Key Observations

- **SC1-SC5** solve without activating the jammer. Standoff weapons (JASSM-ER, 370+ km range)
  allow strikers to fire from outside the SAM engagement zone. The precompute pipeline detects
  this in < 1 second.

- **SC6** is the critical test case. Both HVTs are inside overlapping S-300 coverage. The solver
  must activate 21 jam slots to suppress SAM fire-control radars during striker ingress and weapon
  delivery.

- **SC4 and SC5** are the hardest computationally (270s and 267s) due to the number of SAM
  avoidance disjunctions: each active (agent, SAM, slot) triple generates a 10-term BoolOr
  constraint.

## SAM Types

| System | Origin | R_max | R_lethal | Guidance | Alpha |
|--------|--------|-------|----------|----------|-------|
| S-300 (SA-20) | Russia | 150 km | 90 km | Semi-active | 3 |
| S-400 (SA-21) | Russia | 400 km | 240 km | Active seeker | 4 |
| HQ-9 | China | 200 km | 120 km | Semi-active | 3 |
| Buk-M2 (SA-17) | Russia | 50 km | 30 km | Beam-rider | 2 |