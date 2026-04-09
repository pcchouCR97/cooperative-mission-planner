"""
SAM Engagement Model (Zarchan)
===============================
Continuous kill probability as a function of range, guidance quality,
and countermeasures. Used to compute Pk-weighted attrition coefficients
for the lexicographic objective.

Reference:
  Zarchan, P. (2012) Tactical and Strategic Missile Guidance, 6th ed.,
    AIAA Progress in Astronautics and Aeronautics, Vol. 239.
"""

import math


def pk_zarchan(R_km, R_lethal_km, Pk_max, alpha,
               cm_stealth=1.0, cm_jam=1.0):
    """
    Kill probability at range R for a single SAM engagement.

        P_k(R) = Pk_max * cm_stealth * cm_jam * min(1, (R_lethal / R)^alpha)

    Parameters
    ----------
    R_km         : engagement range (km)
    R_lethal_km  : lethal envelope radius where P_k = Pk_max (km)
    Pk_max       : maximum kill probability at R <= R_lethal
    alpha        : guidance quality exponent
                     2 = beam-rider (Buk-M2)
                     3 = semi-active homing (S-300, HQ-9)
                     4 = active seeker (S-400)
    cm_stealth   : stealth countermeasure factor in (0, 1]
    cm_jam       : jamming countermeasure factor in (0, 1]

    Returns
    -------
    Kill probability in [0, 1].
    """
    if R_km <= 0:
        return 0.0
    geometric = min(1.0, (R_lethal_km / R_km) ** alpha)
    return Pk_max * cm_stealth * cm_jam * geometric


def average_pk_in_mez(R_inner_km, R_outer_km, R_lethal_km, Pk_max, alpha,
                      cm_stealth=1.0, cm_jam=1.0, n_samples=20):
    """
    Average Pk across the missile engagement zone (MEZ), used as the
    attrition coefficient in the lexicographic objective.

        P_k_bar = (1/n) * sum_{k=1}^{n} P_k(R_k)

    where R_k are uniformly spaced sample points in [R_inner, R_outer].
    """
    if n_samples < 1:
        return 0.0
    total = 0.0
    for i in range(n_samples):
        R = R_inner_km + (R_outer_km - R_inner_km) * (i + 0.5) / n_samples
        total += pk_zarchan(R, R_lethal_km, Pk_max, alpha,
                            cm_stealth, cm_jam)
    return total / n_samples


def salvo_pk(pk_single, n_missiles, chaff_factor=1.0, flare_factor=1.0):
    """
    Kill probability for a salvo of n independent missiles.

        P_kill = 1 - (1 - p_eff)^n

    where p_eff = pk_single * chaff_factor * flare_factor.
    """
    p_eff = pk_single * chaff_factor * flare_factor
    p_eff = max(0.0, min(1.0, p_eff))
    return 1.0 - (1.0 - p_eff) ** n_missiles


# -- SAM platform parameters --
#
# | System  | R_max (km) | R_lethal (km) | Pk_max | alpha | Reaction (s) |
# |---------|------------|---------------|--------|-------|--------------|
# | S-300   | 150        | 90            | 0.85   | 3     | 40           |
# | S-400   | 400        | 240           | 0.90   | 4     | 30           |
# | HQ-9    | 200        | 120           | 0.80   | 3     | 45           |
# | Buk-M2  | 50         | 30            | 0.70   | 2     | 22           |
#
# Example: S-300 vs F-35A (stealth)
#   P_k_bar_unjammed ~ 0.45  ->  attrition coefficient = 0.45 * $80M = $36M/slot
#   P_k_bar_jammed   ~ 0.14  ->  attrition coefficient = 0.14 * $80M = $11.2M/slot