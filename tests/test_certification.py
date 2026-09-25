"""Brute-force checks of the propositions in THEORY_CERTIFICATION.md (P1-P4, Lemma 1).

These check the implementation against independent computation. The derivations themselves
are in the theory document.
"""
import math
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flipbudget import certify as C  # noqa: E402

RNG = np.random.default_rng(20260919)


def _grid_min(a, b, L, U, eps, n=241):
    lo, hi = max(0.0, L - eps), min(1.0, U + eps)
    g = np.linspace(lo, hi, n)
    pj, pk = np.meshgrid(g, g, indexing="ij")
    ok = np.abs(pj - pk) <= eps + 1e-12
    vals = np.where(ok, a * pj - b * pk, np.inf)
    # polygon vertices, exactly
    verts = [(lo, lo), (hi, hi), (lo, min(hi, lo + eps)), (min(hi, lo + eps), lo),
             (hi, max(lo, hi - eps)), (max(lo, hi - eps), hi)]
    return min(vals.min(), min(a * x - b * y for x, y in verts))


def _random_cell():
    L = RNG.uniform(0, 1)
    U = min(1.0, L + RNG.uniform(0, 0.3))
    return RNG.uniform(0, 0.2), RNG.uniform(0, 0.2), L, U, RNG.choice([0.0, RNG.uniform(0, 0.4)])


# ---------------------------------------------------------------- P1
@pytest.mark.parametrize("seed", range(300))
def test_p1_cell_bounds_match_bruteforce(seed):
    a, b, L, U, eps = _random_cell()
    assert C.lb_cell(a, b, L, U, eps) == pytest.approx(_grid_min(a, b, L, U, eps), abs=1e-12)
    # max(a pj - b pk) = -min(b pk - a pj); the region is symmetric in (pj, pk)
    assert C.ub_cell(a, b, L, U, eps) == pytest.approx(-_grid_min(b, a, L, U, eps), abs=1e-12)


def test_p1_eps0_is_the_shared_analysis():
    for _ in range(200):
        a, b, L, U, _ = _random_cell()
        common = (a - b) * (L if a >= b else U)
        assert C.lb_cell(a, b, L, U, 0.0) == pytest.approx(common, abs=1e-15)


def test_p1_boundary_cases():
    # 00 cell with L=0: clipping binds at once; a>=b gives -b*min(h, eps)
    assert C.lb_cell(0.5, 0.2, 0.0, 0.02, 0.01) == pytest.approx(-0.2 * 0.01)
    # zero shares contribute nothing
    assert C.lb_cell(0.0, 0.0, 0.3, 0.4, 0.2) == 0.0
    # eps large: region is [0,1]^2 -> min a*0 - b*1
    assert C.lb_cell(0.3, 0.4, 0.5, 0.5, 1.0) == pytest.approx(-0.4)


@pytest.mark.parametrize("seed", range(300))
def test_p1_minimiser_sits_where_the_proof_says(seed):
    """Appendix A locates the minimiser, not just its value.

    g(x) = a x - b min(h, x + eps) is convex and piecewise linear with a kink at h - eps,
    so the minimum is at x = lo when a >= b and at x = max(lo, h - eps) when a < b. The
    optimal partner is always y = min(h, x + eps). Checking the argmin, and not only the
    value, is what ties the written derivation to lb_cell.
    """
    a, b, L, U, eps = _random_cell()
    lo, hi = max(0.0, L - eps), min(1.0, U + eps)
    x_star = lo if a >= b else max(lo, hi - eps)
    y_star = min(hi, x_star + eps)
    # the stated point is feasible
    assert lo - 1e-12 <= x_star <= hi + 1e-12
    assert lo - 1e-12 <= y_star <= hi + 1e-12
    assert abs(x_star - y_star) <= eps + 1e-12
    # and it attains the implementation's minimum
    assert a * x_star - b * y_star == pytest.approx(C.lb_cell(a, b, L, U, eps), abs=1e-12)


def _legacy_shared_range(sj, sk, conc, disc_j, disc_k):
    """fb_joint_verifier.evaluate 'shared' arithmetic, re-derived by corner enumeration."""
    terms = [(sj[c] - sk[c], *conc[c]) for c in conc]
    terms += [(sj[c], *disc_j[c]) for c in disc_j] + [(-sk[c], *disc_k[c]) for c in disc_k]
    lo = sum(k * (l if k > 0 else h) for k, l, h in terms)
    hi = sum(k * (h if k > 0 else l) for k, l, h in terms)
    return lo, hi


def test_p1_pair_range_eps0_equals_legacy_shared():
    for _ in range(200):
        sh = RNG.dirichlet(np.ones(4), size=2)
        sj, sk = dict(zip("abcd", sh[0])), dict(zip("abcd", sh[1]))
        conc = {"a": (0.95, 0.99), "d": (0.0, 0.03)}
        disc_j = {c: tuple(sorted(RNG.uniform(0, 1, 2))) for c in "bc"}
        disc_k = {c: tuple(sorted(RNG.uniform(0, 1, 2))) for c in "bc"}
        got = C.pair_range(sj, sk, conc, disc_j, disc_k, 0.0)
        assert got == pytest.approx(_legacy_shared_range(sj, sk, conc, disc_j, disc_k), abs=1e-12)


# ---------------------------------------------------------------- P2
def test_p2_lb_nonincreasing_in_eps():
    for _ in range(100):
        a, b, L, U, _ = _random_cell()
        grid = np.linspace(0, 1, 201)
        v = [C.lb_cell(a, b, L, U, e) for e in grid]
        assert all(x >= y - 1e-12 for x, y in zip(v, v[1:]))


def test_p2_breakdown_matches_grid():
    for _ in range(100):
        sj, sk = RNG.dirichlet(np.ones(4)), RNG.dirichlet(np.ones(4))
        sj, sk = dict(zip("abcd", sj)), dict(zip("abcd", sk))
        conc = {"a": (0.97, 0.995), "d": (0.0, 0.02)}
        disc = {c: (0.0, 1.0) for c in "bc"}
        h = RNG.uniform(0, 0.05)
        lb = lambda e: C.pair_range(sj, sk, conc, disc, disc, e)[0] - h  # noqa: E731
        es = C.breakdown_eps(lb)
        if lb(0.0) <= 0:
            assert es == 0.0
            continue
        assert lb(es - 1e-7) > 0 >= lb(min(1.0, es + 1e-7)) or es == 1.0
        grid = np.linspace(0, 1, 20001)
        first_fail = next((e for e in grid if lb(e) <= 0), 1.0)
        assert abs(first_fail - es) <= 1e-4


def test_p2_slope_is_minus_max_share_in_interior():
    a, b, L, U = 0.3, 0.1, 0.5, 0.6
    d = (C.lb_cell(a, b, L, U, 0.02) - C.lb_cell(a, b, L, U, 0.01)) / 0.01
    assert d == pytest.approx(-max(a, b))
    a, b = 0.1, 0.3
    d = (C.lb_cell(a, b, L, U, 0.02) - C.lb_cell(a, b, L, U, 0.01)) / 0.01
    assert d == pytest.approx(-max(a, b))


# ---------------------------------------------------------------- P3
def test_p3_common_mechanism_scales_all_differences():
    for _ in range(500):
        A = RNG.uniform(0, 1, 6)
        q, r = RNG.uniform(0, 1, 2)
        a = q + (1 - q - r) * A
        for j in range(6):
            for k in range(6):
                assert a[j] - a[k] == pytest.approx((1 - q - r) * (A[j] - A[k]), abs=1e-12)
        pi1, pi0 = RNG.uniform(0, 1, 2)
        acc = pi0 + A * (pi1 - pi0)  # A plays the role of the credit rate a_m here
        assert np.allclose(np.subtract.outer(acc, acc), (pi1 - pi0) * np.subtract.outer(A, A))


# ---------------------------------------------------------------- P4
def test_p4_sample_size_and_power():
    assert C.n_required(0.10, 0.80) == 16
    assert C.n_required(0.20, 0.80) == 8
    for rho, pi in product([0.05, 0.1, 0.2, 0.3], [0.5, 0.8, 0.9]):
        n = C.n_required(rho, pi)
        assert 1 - (1 - rho) ** n >= pi > 1 - (1 - rho) ** (n - 1)


def test_p4_without_replacement_power_at_least_with_replacement():
    for N, R, n in [(100, 10, 8), (50, 5, 16), (500, 20, 30)]:
        p0_wor = math.comb(N - R, n) / math.comb(N, n)
        assert p0_wor <= (1 - R / N) ** n


# ---------------------------------------------------------------- Lemma 1
def test_kl_interval_zero_successes_equals_clopper_pearson_upper():
    for n in (10, 145, 400):
        lo, hi = C.kl_interval(0, n, 0.95)
        assert lo == 0.0 and hi == pytest.approx(1 - 0.025 ** (1 / n), rel=1e-9)
        lo, hi = C.kl_interval(n, n, 0.95)
        assert hi == 1.0 and lo == pytest.approx(0.025 ** (1 / n), rel=1e-9)


def test_kl_interval_covers_heterogeneous_without_replacement_mean():
    """Monte Carlo: pooled hypergeometric samples from sub-populations with different rates."""
    sizes, rates, ns = [200, 50, 120, 30], [0.0, 0.1, 0.02, 0.3], [20, 10, 15, 5]
    pops = [np.array([1] * int(round(r * s)) + [0] * (s - int(round(r * s)))) for r, s in zip(rates, sizes)]
    target = sum(n * p.mean() for n, p in zip(ns, pops)) / sum(ns)
    rng, miss, reps = np.random.default_rng(1), 0, 4000
    for _ in range(reps):
        x = sum(rng.choice(p, n, replace=False).sum() for p, n in zip(pops, ns))
        lo, hi = C.kl_interval(int(x), sum(ns), 0.90)
        miss += not (lo <= target <= hi)
    assert miss / reps <= 0.10


def test_kl_interval_contains_point_estimate_and_is_nested():
    for x, n in [(3, 40), (141, 142), (16, 33)]:
        lo95, hi95 = C.kl_interval(x, n, 0.95)
        lo99, hi99 = C.kl_interval(x, n, 0.99)
        assert lo99 <= lo95 <= x / n <= hi95 <= hi99


# ---------------------------------------------------------------- rank intervals
def test_rank_intervals_from_certified_pairs():
    models = ["a", "b", "c", "d"]
    certified = {("a", "b"), ("a", "c"), ("a", "d"), ("b", "d")}  # (winner, loser)
    r = C.rank_intervals(models, certified)
    assert r == {"a": (1, 1), "b": (2, 3), "c": (2, 4), "d": (3, 4)}
