"""
Radar Detection Model
======================
Monostatic radar range equation with RCS-dependent scaling.
Used to compute detection thresholds for the mission planner.

Reference:
  Skolnik, M. (2008) Radar Handbook, 3rd ed., McGraw-Hill. Eq. 2.1.
  Mahafza, B.R. (2013) Radar Systems Analysis and Design Using MATLAB,
    3rd ed., CRC Press.
"""

import math


def radar_detection_range_m(Pt_W, G_dB, freq_GHz, sigma_m2,
                            Smin_W, losses_dB=3.0):
    """
    Maximum detection range from the monostatic radar range equation.

        R_max = [ (Pt * G^2 * lambda^2 * sigma) / ((4*pi)^3 * Smin * L) ]^(1/4)

    Parameters
    ----------
    Pt_W      : transmit power (W)
    G_dB      : antenna gain (dBi)
    freq_GHz  : radar frequency (GHz)
    sigma_m2  : target radar cross-section (m^2)
    Smin_W    : minimum detectable signal power (W)
    losses_dB : system losses (dB), default 3.0

    Returns
    -------
    R_max in meters.
    """
    c = 3.0e8
    wavelength = c / (freq_GHz * 1.0e9)
    G = 10.0 ** (G_dB / 10.0)
    L = 10.0 ** (losses_dB / 10.0)

    numerator = Pt_W * G**2 * wavelength**2 * sigma_m2
    denominator = (4.0 * math.pi)**3 * Smin_W * L

    return (numerator / denominator) ** 0.25


def detection_range_scale_factor(sigma1_m2, sigma2_m2):
    """
    Fourth-root law: how detection range changes with RCS.

        R2 / R1 = (sigma2 / sigma1)^(1/4)

    Example: halving RCS reduces detection range by only 16%.
    """
    return (sigma2_m2 / sigma1_m2) ** 0.25


# -- Platform RCS reference values (X-band, nose-on) --
#
# | Platform        | Config   | sigma (m^2) | Detection range (km) |
# |-----------------|----------|-------------|----------------------|
# | F-35A           | Stealth  | 0.001       | 160                  |
# | F-35A           | Beast    | 1.0         | 285                  |
# | MQ-58           | Standard | 0.0005      | 120                  |
# | B-21            | Stealth  | 0.0001      | 95                   |
# | EA-18G          | Standard | 10.0        | 320                  |