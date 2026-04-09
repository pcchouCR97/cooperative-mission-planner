# Constraint Summary

All constraints in the cooperative mission planning MILP, organized by category.

## Kinematic Constraints

### Speed Bounds (Octagonal)

```
|dx_i| + |dy_i| <= v_max                         (Manhattan outer bound)
12 * |dx_i| +  5 * |dy_i| <= 13 * v_max          (diagonal cut 1)
 5 * |dx_i| + 12 * |dy_i| <= 13 * v_max          (diagonal cut 2)
```

where v_max = V_max_i * dt * S (max displacement per slot in solver units).

Integer ratio 12:5:13 approximates cos(pi/8):sin(pi/8):1.
Minimum speed enforced via circumscribed octagon lower bound.

### Turn Rate Cap

```
h_i[t] <= kappa_i,  for all t
```

where kappa_i is derived from sustained-g physics:

```
kappa_i = (g * n_z / V_i) * dt * V_i * S * f_stores * f_weight
```

### Fuel Range

```
sum_t d_i[t] + (alpha_AB - 1) * sum_{t in D_i} d_i[t] <= R_max_i * S
```

- alpha_AB ~ 2.47 (afterburner fuel multiplier)
- D_i = {t : d_i[t] > v_cruise * dt * S} (afterburner slots)

## Threat Avoidance

### SAM Avoidance with Escort-Jam Escape

```
BoolOr( b_L, b_R, b_U, b_D, b_NW, b_NE, b_SW, b_SE, any_jam_m[t], NOT(s_m[t]) )
```

Ten-term disjunction per (agent, SAM, slot):
- 4 cardinal escape directions (agent outside SAM bbox)
- 4 diagonal escape directions (octagonal exclusion zone)
- SAM is being jammed
- SAM has been destroyed by SEAD

### MEZ Exposure (Soft Penalty)

Agents inside the missile engagement zone (P_k 5-50%) incur Tier B attrition cost but are not hard-excluded.

## Mission Coupling

### Jam-at-Strike

```
strike_i[t] = 1  =>  any_jam_m[t] = 1,  for all SAMs m threatening the target
```

When a striker fires, every SAM whose lethal zone covers the target must be actively jammed.

### Jam Range Containment

```
jam_fcr_{j,m}[t] = 1  =>  ||j[t] - p_s(m)||_oct <= R_jam
```

where R_jam = min(R_platform, max(1.5 * R_hard, 60 km)).

### Mainlobe Half-Plane

```
jam_fcr_{j,m}[t] = 1  =>  n . (p_j[t] - p_radar) <= 0
```

Jammer must be on the striker-approach side of the radar (sidelobe J/S requirement).

### Strike Standoff

Target must be within weapon standoff range at the strike slot.

### Exit Reification

```
at_exit_i[t] = 1  =>  ||i[t] - e_i||_1 <= epsilon * S     (forward)
at_exit_i[t] = 0  =>  BoolOr(b_out_L, b_out_R, b_out_U, b_out_D)  (backward)
```

Monotonic: at_exit_i[t+1] >= at_exit_i[t]. After exit, agent freezes (dx = dy = 0).

## Constraint Count

| Category | Count (SC4: 4 agents, 6 SAMs, 50 slots) |
|----------|------------------------------------------|
| Kinematics | ~800 |
| Speed bounds | ~600 |
| SAM avoidance | ~2,400 (after spatial pruning) |
| Mission coupling | ~400 |
| Exit + symmetry | ~200 |
| **Total** | **~4,400** |

Spatial pruning removes 40-60% of avoidance constraints by skipping unreachable (agent, SAM, slot) triples.