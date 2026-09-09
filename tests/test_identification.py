"""Real pytest tests -- the same assertions verified interactively in
scripts/fb_t1_symbolic.py and scripts/fb_t2_flipbudget.py, packaged as a
runnable regression suite rather than left as one-off scripts only."""
import numpy as np
import pytest

from flipbudget import g, single_model_extrema, comparison_extrema, flip_budget


def test_g_matches_closed_form():
    assert g(0.65, 0.05, 0.10) == pytest.approx((0.65 - 0.05) / (1 - 0.05 - 0.10))


def test_g_can_fall_outside_unit_interval():
    # T1's finding: the identified set is not automatically within [0,1] --
    # that is why callers must intersect with [0,1] themselves if they need it.
    assert g(0.10, 0.15, 0.20) < 0


@pytest.mark.parametrize("a,alpha0,beta0,d", [
    (0.65, 0.075, 0.10, 0.075),
    (0.10, 0.075, 0.10, 0.075),  # non-monotone dg/dalpha regime
    (0.50, 0.245, 0.245, 0.245),  # near the alpha+beta -> 1 boundary
])
def test_single_model_extrema_matches_grid_search(a, alpha0, beta0, d):
    """Grid a box identical to what single_model_extrema itself searches
    (alpha0-d..alpha0+d, beta0-d..beta0+d, clipped to [0,1]) and confirm the
    corner-based extrema match the grid's extrema to numerical tolerance."""
    n = 401
    alphas = np.linspace(max(0.0, alpha0 - d), min(1.0, alpha0 + d), n)
    betas = np.linspace(max(0.0, beta0 - d), min(1.0, beta0 + d), n)
    AA, BB = np.meshgrid(alphas, betas)
    feasible = (AA + BB) < 0.999
    GG = np.where(feasible, g(a, AA, BB), np.nan)
    grid_min, grid_max = np.nanmin(GG), np.nanmax(GG)

    corner_min, corner_max = single_model_extrema(a, alpha0, beta0, d)
    assert corner_min == pytest.approx(grid_min, abs=1e-3)
    assert corner_max == pytest.approx(grid_max, abs=1e-3)


def test_case_a_preserves_sign():
    rng = np.random.default_rng(42)
    n_fail = 0
    for _ in range(2000):
        a1, a2 = rng.uniform(0, 1, 2)
        alpha, beta = rng.uniform(0, 0.4, 2)
        if alpha + beta >= 0.999:
            continue
        delta = g(a1, alpha, beta) - g(a2, alpha, beta)
        if a1 != a2 and np.sign(delta) != np.sign(a1 - a2):
            n_fail += 1
    assert n_fail == 0


def test_comparison_extrema_collapses_to_point_at_d_zero():
    a1, a2, alpha0, beta0 = 0.70, 0.55, 0.08, 0.12
    mn, mx = comparison_extrema(a1, a2, alpha0, beta0, 0.0)
    expected = g(a1, alpha0, beta0) - g(a2, alpha0, beta0)
    assert mn == pytest.approx(expected, abs=1e-9)
    assert mx == pytest.approx(expected, abs=1e-9)


def test_flip_budget_zero_gap_is_degenerate():
    d_star, degenerate = flip_budget(0.50, 0.50, 0.05, 0.05)
    assert degenerate is True


def test_flip_budget_larger_gap_needs_larger_budget():
    d_small_gap, _ = flip_budget(0.65, 0.62, 0.05, 0.08)
    d_large_gap, _ = flip_budget(0.80, 0.60, 0.02, 0.03)
    assert d_large_gap > d_small_gap
