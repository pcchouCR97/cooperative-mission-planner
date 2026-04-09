# Octagonal Geometry Approximation

## Problem

CP-SAT operates on integers. Euclidean distance (sqrt(x^2 + y^2)) requires quadratic constraints
that destroy LP relaxation quality. Manhattan distance (|x| + |y|) is LP-friendly but has 41% error
at 45 degrees.

## Solution: Inscribed Octagon via Pythagorean Triple

The octagonal norm uses the 5-12-13 Pythagorean triple to inscribe a regular 8-gon inside the
Euclidean circle. Three linear constraints (plus symmetry) define the octagon:

```
|dx| + |dy| <= R                  (Manhattan -- clips corners)
12 * |dx| +  5 * |dy| <= 13 * R  (diagonal cut at ~22.6 degrees)
 5 * |dx| + 12 * |dy| <= 13 * R  (diagonal cut at ~67.4 degrees)
```

The integer coefficients 12:5:13 approximate cos(pi/8):sin(pi/8):1 = 0.924:0.383:1.

## Properties

| Metric | Manhattan | Octagon | Euclidean |
|--------|-----------|---------|-----------|
| Shape | Diamond | 8-gon | Circle |
| Max error vs circle | 41.4% | 7.6% | 0% |
| Extra integer variables | 0 | 0 | N/A |
| LP relaxation quality | Poor | Good | N/A (nonlinear) |

The octagon over-approximates the circle by at most 7.6% (at the midpoint of each flat edge)
and under-approximates by 0% (at each vertex). This is sufficient for speed bounds, exclusion
zones, and standoff distances.

## Why Zero Extra Variables

The key insight is that |dx| and |dy| are already decomposed into positive and negative parts
for the LP-tight absolute value formulation:

```
dx = dx_pos - dx_neg,  dx_pos >= 0, dx_neg >= 0
|dx| = dx_pos + dx_neg
```

The diagonal cuts reuse these existing absolute-value variables. No new BoolVars or IntVars
are needed beyond what the Manhattan formulation already requires.

SAM exclusion octagons do require 8 BoolVars per active (agent, SAM, slot) triple:
4 cardinal + 4 diagonal escape directions.

## Application in the Solver

The octagonal norm is used for:
- **Speed bounds**: agent displacement per slot
- **SAM exclusion zones**: hard-kill and MEZ radii
- **Jam range containment**: jammer-to-SAM distance
- **Exit tolerance**: agent-to-exit-point distance
- **Strike standoff**: striker-to-target distance

All use the same 12:5:13 coefficients. The geometry is consistent across all constraint types.

![Octagon vs Manhattan vs Euclidean](../figures/octagon_geometry.png)