# Decision Variables

Complete variable catalog for the cooperative mission planning MILP.
All variables are integer-scaled by factor S (units per km).

## Position (per agent, per slot)

| Variable | Domain | Description |
|----------|--------|-------------|
| x_i[t], y_i[t] | Z | Spatial coordinates, t = 0,...,N, i in A |
| dx_i[t], dy_i[t] | Z | Per-slot displacement (finite difference) |
| h_i[t] | Z+ | Heading-change auxiliary: \|dx[t+1] - dx[t]\| + \|dy[t+1] - dy[t]\| |

## Mission Binaries

| Variable | Domain | Description |
|----------|--------|-------------|
| strike_i[t] | {0,1} | Striker i fires weapon at slot t |
| at_exit_i[t] | {0,1} | Agent i has reached exit zone by slot t (monotonic) |
| assign_{i,j} | {0,1} | Striker i assigned to HVT j |
| sam_alive_m[t] | {0,1} | SAM m is operational at slot t (SEAD destruction tracking) |

## Per-SAM FCR Jamming (Escort Jam Model)

| Variable | Domain | Description |
|----------|--------|-------------|
| jam_fcr_{j,m}[t] | {0,1} | Jammer j targeting SAM m's fire-control radar at slot t |
| any_jam_m[t] | {0,1} | Disjunction: any jammer targeting SAM m at slot t |

**Multi-beam AESA constraint:**

```
sum_m jam_fcr_{j,m}[t] <= K_max,  for all j, t
```

where K_max = 3 for ALQ-249 / MQ-58 (simultaneous FCR tracks).

## Jammer Mode (ExactlyOne per slot)

```
active_j[t] + esm_j[t] + off_j[t] = 1,  for all j in J, t = 0,...,N-1
```

| Mode | Description |
|------|-------------|
| active_j[t] | Noise jamming -- blinds SAM fire-control radar |
| esm_j[t] | Electronic support measures -- passive listen-only, no emissions |
| off_j[t] | Payload powered down -- transit mode |

## MEZ Exposure Tracking

| Variable | Domain | Description |
|----------|--------|-------------|
| exposed_mez_i[t] | {0,1} | Agent i inside SAM's missile engagement zone at slot t |

Excludes jammers (handled separately via b_{j,s}^{ever} single-occurrence indicator).

## Variable Count

```
4 * n_a * (N+1) [pos] + 2 * n_a * N [vel] + n_a * (N-1) [hdg]
  + O(n_a * n_s * N) [avoidance] + O(N) [mission]
```

Approximately 2,600 variables for SC4 (4 agents, 6 SAMs, 50 slots).