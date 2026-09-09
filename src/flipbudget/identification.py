"""T1/T2 -- the identification theory, as a library.

Ported from scripts/fb_t1_symbolic.py and scripts/fb_t2_flipbudget.py, whose
symbolic derivations and Monte-Carlo cross-checks remain the source of truth
for correctness (see tests/test_identification.py, which re-runs the same
assertions as real pytest tests rather than duplicating the derivation).
"""
from __future__ import annotations

import numpy as np

DENOM_CAP = 0.999  # alpha+beta must stay below 1; float safety margin


def g(a: float, alpha: float, beta: float) -> float:
    """The misclassification correction: A* = (a - alpha) / (1 - alpha - beta).

    a: observed (published) rate. alpha: false-credit rate,
    P(scorer says correct | truly wrong). beta: false-miss rate,
    P(scorer says wrong | truly correct)."""
    denom = 1 - alpha - beta
    return (a - alpha) / denom


def single_model_extrema(a: float, alpha0: float, beta0: float, d: float
                          ) -> tuple[float, float]:
    """Min/max of g(a, alpha, beta) over alpha in [alpha0-d, alpha0+d],
    beta in [beta0-d, beta0+d], clipped to the valid domain. Attained at box
    corners (T1's proven result) -- sharp (T4), not merely an enclosure."""
    alphas = [max(0.0, alpha0 - d), min(1.0, alpha0 + d)]
    betas = [max(0.0, beta0 - d), min(1.0, beta0 + d)]
    vals = []
    for al in alphas:
        for be in betas:
            if al + be >= DENOM_CAP:
                be = DENOM_CAP - al - 1e-6
                if be < 0:
                    continue
            vals.append(g(a, al, be))
    return min(vals), max(vals)


def comparison_extrema(a1: float, a2: float, alpha0: float, beta0: float,
                        d: float) -> tuple[float, float]:
    """Identified interval for Delta* = A*_1 - A*_2 under a shared baseline
    (alpha0, beta0) with each model allowed to deviate independently by up to
    d (T2's Case B). Extrema separate because g1, g2 depend on disjoint free
    variables: max(Delta) = max(g1) - min(g2), min(Delta) = min(g1) - max(g2)."""
    min_g1, max_g1 = single_model_extrema(a1, alpha0, beta0, d)
    min_g2, max_g2 = single_model_extrema(a2, alpha0, beta0, d)
    return min_g1 - max_g2, max_g1 - min_g2


def flip_budget(a1: float, a2: float, alpha0: float, beta0: float,
                 d_max: float = 0.5, tol: float = 1e-6
                 ) -> tuple[float | None, bool]:
    """Smallest d such that 0 falls inside the Case-B identified interval for
    Delta* -- the least amount of differential scorer misclassification that
    would put the comparison's sign in doubt. Returns (d_star, degenerate);
    degenerate=True means the comparison is already inconclusive at d=0
    (0 is inside the interval even under non-differential error), so no
    flip-budget number is meaningful -- report that plainly, per
    PREREGISTRATION_FLIPBUDGET.md's degenerate-case rule, rather than a
    fabricated value."""
    min0, max0 = comparison_extrema(a1, a2, alpha0, beta0, 0.0)
    if min0 <= 0 <= max0:
        return 0.0, True

    minM, maxM = comparison_extrema(a1, a2, alpha0, beta0, d_max)
    if not (minM <= 0 <= maxM):
        return None, False  # not flippable within d_max -- report as such, don't fabricate

    lo, hi = 0.0, d_max
    while hi - lo > tol:
        mid = (lo + hi) / 2
        mn, mx = comparison_extrema(a1, a2, alpha0, beta0, mid)
        if mn <= 0 <= mx:
            hi = mid
        else:
            lo = mid
    return hi, False
