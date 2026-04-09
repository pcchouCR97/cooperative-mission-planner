"""
Electronic Warfare: J/S Ratio and Jam-Range Geometry
=====================================================
Jammer-to-signal ratio model for escort jamming. Used to determine
the effective jam range and mainlobe constraint geometry.

Reference:
  Adamy, D.L. (2015) EW 104: Electronic Warfare Against a New Generation
    of Threats, Artech House.
  Skolnik, M. (2008) Radar Handbook, 3rd ed., McGraw-Hill. Ch. 24.
"""

import math


def js_ratio(Pj_W, Gj_dBi, Rr_km, Pr_W, Gr_dBi, Rj_km,
             sigma_m2, Lj_dB=3.0):
    """
    Jammer-to-signal ratio (linear scale).

        J/S = (Pj * Gj * Rr^2) / (Pr * Gr * Rj^2 * sigma * Lj)

    Parameters
    ----------
    Pj_W    : jammer transmit power (W)
    Gj_dBi  : jammer antenna gain toward radar (dBi)
    Rr_km   : range from radar to target (km)
    Pr_W    : radar transmit power (W)
    Gr_dBi  : radar antenna gain toward jammer (dBi) -- critical term
    Rj_km   : range from jammer to radar (km)
    sigma_m2: target RCS (m^2)
    Lj_dB   : jammer system losses (dB), default 3.0

    Returns
    -------
    J/S ratio (linear). J/S > 1 means jammer overpowers radar return.
    """
    Gj = 10.0 ** (Gj_dBi / 10.0)
    Gr = 10.0 ** (Gr_dBi / 10.0)
    Lj = 10.0 ** (Lj_dB / 10.0)

    Rr_m = Rr_km * 1000.0
    Rj_m = Rj_km * 1000.0

    numerator = Pj_W * Gj * Rr_m**2
    denominator = Pr_W * Gr * Rj_m**2 * sigma_m2 * Lj

    if denominator <= 0:
        return float('inf')
    return numerator / denominator


def js_ratio_dB(Pj_W, Gj_dBi, Rr_km, Pr_W, Gr_dBi, Rj_km,
                sigma_m2, Lj_dB=3.0):
    """J/S ratio in dB."""
    ratio = js_ratio(Pj_W, Gj_dBi, Rr_km, Pr_W, Gr_dBi, Rj_km,
                     sigma_m2, Lj_dB)
    if ratio <= 0:
        return -float('inf')
    return 10.0 * math.log10(ratio)


# -- Angular dependence: geometric enforcement via half-plane --
#
# The radar antenna gain Gr(theta) toward the jammer determines
# escort jamming effectiveness. Rather than modeling Gr(theta)
# analytically, the solver enforces favorable geometry via a
# half-plane constraint:
#
#     n . (p_jammer - p_radar) <= 0
#
# where n is the normal vector from radar toward the striker fleet.
# This forces the jammer to the striker-approach side of the radar,
# placing it in the sidelobe region (low Gr, high J/S) rather than
# the mainlobe (high Gr, low J/S).
#
# Typical angular dependence of Gr:
#
# | Angle from mainlobe | Typical Gr (dBi) | J/S impact             |
# |---------------------|------------------|------------------------|
# | < 15 deg (mainlobe) | 30-40            | Jammer least effective |
# | 15-30 deg           | 10-20            | Moderate               |
# | > 30 deg (sidelobe) | -10 to -20       | Jammer most effective  |


# -- Jam range geometry in the solver --
#
# Jam range containment uses the octagonal norm:
#
#     jam_fcr[j,m,t] = 1  =>  ||jammer[t] - SAM_m||_oct <= R_jam
#
# where R_jam = min(R_platform, max(1.5 * R_hard, 60 km))
#
# Multi-beam AESA allows simultaneous jamming of up to K_max = 3 SAMs:
#
#     sum_m jam_fcr[j,m,t] <= K_max,  for all j, t