# Cooperative Mission Planner for Manned-Unmanned Teaming

A modular MILP/CP-SAT solver for cooperative multi-agent combat mission planning in contested airspace. Built for the loyal wingman paradigm: F-35A strike aircraft paired with MQ-58 collaborative combat aircraft (CCA) providing electronic warfare support against layered surface-to-air missile (SAM) defenses.

**Status:** All 6 validation scenarios solve to OR-Tools `OPTIMAL` with gaps <= 0.77% in 16-270 seconds. A 5-sector campaign demonstrator (14 agents, 22 SAMs, 1500 km theater) solves all-OPTIMAL in under 9 minutes.

![SC6: HVT Inside SAM -- the only scenario where jamming activates](figures/appendix_sc6.png)
*SC6: Two F-35A strikers and one MQ-58 jammer versus 2 S-300 and 1 Buk-M2, with HVTs inside SAM coverage. MQ-58 escorts strikers through the threat belt with 21 active jam slots. OPTIMAL, 0.01% gap, 302s.*

---

## Problem

Plan cooperative air strike missions where:
- **F-35A** strikers must ingress through SAM threat rings, deliver weapons on assigned targets, and egress to a safe exit point
- **MQ-58** jammers must escort strikers by suppressing SAM fire-control radars from within a computed jam-range envelope
- Jamming, strike, and egress must be **temporally coupled** -- the jammer must be active on the correct SAM at the exact slot the striker passes through its engagement zone
- All agents must satisfy speed limits, fuel budgets, turn-rate physics, and weapon standoff constraints simultaneously

This is **not** a vehicle routing problem. The temporal coupling between electronic attack and kinematic trajectory, combined with disjunctive SAM avoidance over layered threat geometries, makes the problem NP-hard even for two agents.

---

## Architecture

### Solver Pipeline

```
Scenario Config
      |
[L0] Payload Advisor ---- burn-through range, J/S feasibility (1.9 ms)
      |
[L1] Fleet Divider ------ greedy threat-to-team assignment
      |
[L2] DAG Scheduler ------ wave ordering via Kahn's algorithm (0.02 ms)
      |
[L3] Transfer Router ---- A* jammer repositioning between sectors (170 ms)
      |
[L4] Trajectory Solver -- per-team CP-SAT with full constraint set
      |
   OPTIMAL trajectories + mission schedule + fuel report
```

![Five-layer XDSM decomposition](figures/xdsm_architecture.png)
*Hierarchical decomposition: payload advisory, fleet division, DAG scheduling, transfer routing, and per-team trajectory optimization.*

### Key Formulation Decisions

| Component | Approach | Why |
|-----------|----------|-----|
| **Speed model** | Octagonal (12:5:13 Pythagorean triple) | 7.6% error vs Euclidean, zero extra variables, LP-tight |
| **SAM avoidance** | 8-direction disjunction + jam escape | Unified threat avoidance and electronic attack in one constraint |
| **Objective** | Pk-weighted lexicographic (attrition >> time >> cost) | Dollar-valued attrition prevents trivial "fly around everything" solutions |
| **Jam model** | Per-SAM FCR escort jam | Each jammer targets specific SAM fire-control radars per slot |
| **Precompute** | 4-stage pipeline (audit, budget, reachability, fleet reduction) | 40-60% variable reduction before solver starts |

---

## Geometry

The solver uses an octagonal norm (inscribed 8-gon) for speed, distance, and exclusion zone constraints. This replaces the Manhattan (diamond) norm used in earlier versions, reducing geometric error from 41% to 7.6% with zero additional integer variables.

![Octagon vs Manhattan vs Euclidean](figures/octagon_geometry.png)
*Comparison of norm approximations. The octagon (green) closely tracks the Euclidean circle (black) using only linear constraints on existing absolute-value variables.*

---

## Threat Models

### SAM Engagement (Zarchan Model)

Kill probability is modeled as a continuous function of range, guidance quality, and countermeasures:

```
P_k(R) = P_k_max * c_stealth * c_jam * min(1, (R_lethal / R)^alpha)
```

where `alpha` encodes guidance quality (command-guided: 2, semi-active: 3, active: 4).

![Pk curves for F-35A vs four SAM types](figures/pk_model.png)
*Zarchan P_k(R) model showing stealth-only vs stealth+jam kill probability for S-300, S-400, HQ-9, and Buk-M2. Shaded regions indicate hard-kill (red), MEZ (yellow), and detection (green) zones.*

### Electronic Warfare

Jammer placement is constrained by:
- **Jam range envelope:** octagonal containment within effective J/S radius
- **Mainlobe half-plane:** jammer must be on the striker-approach side of the radar
- **Multi-beam AESA:** MQ-58 can simultaneously jam up to 3 SAMs

---

## Validation Results

### Scenario Suite (v6 Pipeline, Lexicographic Objective)

| Scenario | Fleet | SAMs | HVTs | Status | Gap | Time |
|----------|-------|------|------|--------|-----|------|
| SC1 -- Corridor Strike | 2x F-35A + MQ-58 | 3 | 2 | OPTIMAL | 0.77% | 120s |
| SC2 -- Flanking Maneuver | F-35A + 2x MQ-58 | 4 | 1 | OPTIMAL | 0.00% | 39s |
| SC3 -- SAM Wall | 2x F-35A + MQ-58 | 6 | 2 | OPTIMAL | 0.00% | 16s |
| SC4 -- Layered IADS | 2x F-35A + 2x MQ-58 | 6 | 2 | OPTIMAL | 0.00% | 270s |
| SC5 -- Dense IADS + S-400 | 3x F-35A + MQ-58 | 8 | 3 | OPTIMAL | 0.03% | 267s |
| SC6 -- HVT Inside SAM | 2x F-35A + MQ-58 | 3 | 2 | OPTIMAL | 0.01% | 154s |

SC6 is the only scenario where jamming activates (21 slots) -- all others use standoff weapons (JASSM-ER, 370+ km) to avoid the SAM engagement zone entirely. The precompute pipeline detects this in < 1 second.

### Mission Reports

Each scenario is shown with jammer (left) and without jammer (right), demonstrating the solver's ability to exploit standoff weapons when jamming is unnecessary.

**SC1 -- Corridor Strike** (2x F-35A + MQ-58, 3 SAMs, 2 HVTs)

| With Jammer | Without Jammer |
|:-----------:|:--------------:|
| ![SC1 with jammer](figures/sc1_with_jammer.png) | ![SC1 no jammer](figures/sc1_no_jammer.png) |
| OPTIMAL, 16.0M, 118s, 0 jam slots | OPTIMAL, 10.5M, 49s, 2.4x speedup |

**SC2 -- Flanking Maneuver** (F-35A + 2x MQ-58, 4 SAMs, 1 HVT)

| With Jammer | Without Jammer |
|:-----------:|:--------------:|
| ![SC2 with jammer](figures/sc2_with_jammer.png) | ![SC2 no jammer](figures/sc2_no_jammer.png) |
| OPTIMAL, 17.0M, 149s | OPTIMAL, 12.0M, 5s, 29.8x speedup |

**SC3 -- SAM Wall** (2x F-35A + MQ-58, 6 SAMs, 2 HVTs)

| With Jammer | Without Jammer |
|:-----------:|:--------------:|
| ![SC3 with jammer](figures/sc3_with_jammer.png) | ![SC3 no jammer](figures/sc3_no_jammer.png) |
| OPTIMAL, 209.0M, 39s | OPTIMAL, 9.5M, 4s, 9.8x speedup |

**SC4 -- Layered IADS** (2x F-35A + 2x MQ-58, 6 SAMs, 2 HVTs)

| With Jammer | Without Jammer |
|:-----------:|:--------------:|
| ![SC4 with jammer](figures/sc4_with_jammer.png) | ![SC4 no jammer](figures/sc4_no_jammer.png) |
| OPTIMAL, 211.0M, 271s, 480 escort-jam BoolVars | OPTIMAL, 14.0M, 31s, 8.7x speedup |

**SC5 -- Dense IADS + S-400** (3x F-35A + MQ-58, 8 SAMs, 3 HVTs)

| With Jammer | Without Jammer |
|:-----------:|:--------------:|
| ![SC5 with jammer](figures/sc5_with_jammer.png) | ![SC5 no jammer](figures/sc5_no_jammer.png) |
| OPTIMAL, 28.1M, 267s, 0.03% gap | OPTIMAL, 16.1M, 136s, 2.0x speedup |

**SC6 -- HVT Inside SAM** (2x F-35A + MQ-58, 3 SAMs, 2 HVTs inside MEZ)

| With Jammer | Without Jammer |
|:-----------:|:--------------:|
| ![SC6 with jammer](figures/sc6_with_jammer.png) | ![SC6 no jammer](figures/sc6_no_jammer.png) |
| OPTIMAL, 132.0M, 302s, 21 active jam slots | OPTIMAL, standoff bypass |

*SC6 is the only scenario where the MQ-58 activates jamming. All others exploit standoff weapons to avoid SAM engagement zones entirely.*

### Jammer Ablation

| Scenario | With Jammer | Without | Speedup |
|----------|-------------|---------|---------|
| SC1 | 118s | 49s | 2.4x |
| SC2 | 149s | 5s | 29.8x |
| SC3 | 39s | 4s | 9.8x |
| SC4 | 271s | 31s | 8.7x |
| SC5 | 267s | 136s | 2.0x |

### Constraint Ablation

![Gap reduction waterfall](figures/ablation_waterfall.png)
*Cumulative optimality gap reduction on SC6. Each engineering improvement (octagon speed, IB SAM encoding, turn cap, two-phase solve, warm-start hints) reduces gap from 24.1% to 0.2%.*

### Campaign Demonstrator

A 5-sector, 3-wave campaign across a 1500 x 2000 km theater:

| Wave | Sector | Fleet | SAMs | Solve Time | Status |
|------|--------|-------|------|------------|--------|
| 1 | NW Corridor | 3 agents | 4 | 89s | OPTIMAL |
| 1 | NE Wall | 3 agents | 5 | 15s | OPTIMAL |
| 1 | W Flanking | 3 agents | 4 | 30s | OPTIMAL |
| 2 | C Layered IADS | 4 agents | 6 | 224s | OPTIMAL |
| 3 | SE Close Strike | 3 agents | 3 | 124s | OPTIMAL |

**Total: 14 agents, 22 SAMs, 5/5 OPTIMAL in 481 seconds.** MQ-58 jammers transfer between waves via A*-routed corridors (1039 km, 73 min + 750 km, 53 min).

![Campaign theater map](figures/campaign_map.png)
*Five-sector campaign theater. 14 agents, 22 SAMs, jammer transfer routes (dashed), all OPTIMAL in 481s.*

![Campaign Gantt chart](figures/campaign_gantt.png)
*Campaign Gantt: 3-wave sequencing with jammer transfer windows between sectors.*

![Campaign mission schedule](figures/campaign_schedule.png)
*Per-agent mission schedule across all 5 sectors. Ingress, strike, jam, exit, and MQ-58 transfer phases.*

---

## Tech Stack

- **Solver:** Google OR-Tools CP-SAT (CDCL(T) lazy clause generation, 16-worker parallel search)
- **Language:** Python 3.11
- **Physics:** Custom models for radar detection (4th-root law), EW (J/S ratio), SAM engagement (Zarchan Pk), aerodynamic drag (parabolic polar + transonic correction), Breguet fuel consumption
- **Visualization:** Matplotlib tactical reports with mission schedule Gantt charts
- **Platform data:** 14 air platforms, 7 SAM/radar systems, 47 weapon variants

---

## Repository Structure

```
cooperative-mission-planner/
|-- README.md
|-- LICENSE
|-- .gitignore
|-- requirements.txt
|
|-- figures/                    # Paper-quality figures (white background)
|   |-- appendix_sc6.png       # Hero: SC6 full trajectory + Gantt
|   |-- sc1-sc6_with_jammer.png  # With-jammer mission reports
|   |-- sc1-sc6_no_jammer.png    # Without-jammer ablation
|   |-- campaign_map.png       # 5-sector campaign theater
|   |-- campaign_gantt.png     # Campaign wave Gantt
|   |-- campaign_schedule.png  # Per-agent mission schedule
|   |-- xdsm_architecture.png  # Solver pipeline XDSM
|   |-- octagon_geometry.png   # Octagonal norm comparison
|   |-- pk_model.png           # Zarchan Pk(R) curves
|   +-- ablation_waterfall.png # Constraint ablation waterfall
|
|-- formulation/                # Mathematical formulation (cleaned excerpts)
|   |-- variables.md            # Decision variable catalog
|   |-- objective.md            # Lexicographic objective definition
|   |-- constraints.md          # Constraint summary table
|   +-- geometry.md             # Octagonal norm derivation
|
|-- scenarios/                  # Scenario definitions (sanitized configs)
|   |-- sc1_corridor_strike.py
|   |-- sc4_layered_iads.py
|   +-- sc6_hvt_inside_sam.py
|
|-- models/                     # Physics model excerpts
|   |-- radar_detection.py      # Fourth-root RCS-dependent detection
|   |-- sam_engagement.py       # Zarchan Pk(R) model
|   +-- ew_jamming.py           # J/S ratio and jam-range geometry
|
+-- docs/
    |-- solver_architecture.md  # Pipeline description
    +-- scenario_guide.md       # How to read the results
```

---

## Selected Publications

**Chou, P.-C.** (2026). *Cooperative Multi-Agent Combat Mission Planning via Constraint Programming: A Modular Solver for Manned-Unmanned Teaming Operations.* Manuscript in preparation.

---

## About

This project was developed as an independent research effort in combinatorial optimization for defense autonomy. The solver addresses a problem class that sits at the intersection of:

- **Operations research** -- mixed-integer programming with disjunctive constraints
- **Electronic warfare** -- J/S ratio modeling, mainlobe geometry, IADS suppression
- **Flight dynamics** -- speed/fuel/turn-rate physics for heterogeneous platforms
- **Multi-agent coordination** -- temporal coupling between cooperative roles

The full production solver, scenario suite, and paper are maintained in a private repository. This portfolio contains curated artifacts that demonstrate the technical approach and validated results.

---

## Contact

**Po-Chih Chou**
- Email: pcchouCR97@gmail.com
- University of Michigan: pcchou@umich.edu

---

*Built with Google OR-Tools CP-SAT. Platform data derived from open-source references (Jane's, GlobalSecurity, Wikipedia). No classified or export-controlled information is contained in this repository.*