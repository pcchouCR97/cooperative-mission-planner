# Objective Function

Pk-weighted lexicographic objective with four strict tiers.
Higher tiers dominate lower tiers by construction (big-M separation).

## Priority Ordering

```
Tier B (attrition) >> Tier B.5 (jammer MEZ) >> Tier C (time) >> Tier D (cost)
```

## Tier B -- Striker Attrition (Pk-Weighted)

```
sum_{(i,s,t)} [ P_k_uj(i,s) * C_i * b_uj(i,s,t) + P_k_j(i,s) * C_i * b_j(i,s,t) ]
  + sum_{strikers} 0.5 * P_k_uj(i,s) * C_i * sigma_i[t]
```

| Symbol | Meaning | Example |
|--------|---------|---------|
| P_k_uj(i,s) | Average unjammed kill probability, agent i vs SAM s | S-300 vs F-35A: 0.45 |
| P_k_j(i,s) | Average jammed kill probability (with countermeasure factor c_j) | S-300 vs F-35A jammed: 0.14 |
| C_i | Platform replacement cost (USD) | F-35A: $80M, MQ-58: $25M |

## Tier B.5 -- Jammer MEZ Attrition

```
sum_{(j,s)} 0.30 * C_j * b_ever(j,s)
```

- b_ever(j,s): single-occurrence indicator (jammer j ever entered SAM s MEZ)
- MQ-58 coefficient: 0.30 * $25M = $7.5M

## Tier C -- Mission Time

```
M_C * T_exit_max + M_C' * sum_i T_dep_i
```

| Coefficient | Value | Meaning |
|-------------|-------|---------|
| M_C | $500,000 | Per exit-slot penalty |
| M_C' | M_C / (4 * \|S\|) | Departure time (secondary) |
| T_exit_max | IntVar | Latest exit time across all agents |

## Tier D -- Operational Cost

```
M_D * [ sum_i (c_cpfh * T_i + c_fuel * sum_t d_i[t]) + c_jam * sum_{j,t} a_j[t] ]
```

| Coefficient | Value | Source |
|-------------|-------|--------|
| M_D | 1 | Dollar-denominated |
| c_cpfh | $600/slot | F-35A: $36,000/hr at dt=60s |
| c_fuel | $2.30/km | JP-8 fuel proxy |
| c_jam | $500/slot | Pod amortization + home-on-jam risk premium |

## Lexicographic Separation (Big-M)

| Domination | Proof |
|------------|-------|
| B >> C | One unjammed attrition slot >= M_C * N_max + 1 (e.g., $36M > $32.5M) |
| C >> D | One Tier C slot ($500K) exceeds entire Tier D budget (~$22K) |
| B.5 between B and C | Jammer coefficient ($7.5M) sits between by construction |

No solver tuning parameter controls the priority -- it is a structural property of the coefficient magnitudes.