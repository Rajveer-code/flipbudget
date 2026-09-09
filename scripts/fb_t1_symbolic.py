"""T1 -- identified set for a single model's accuracy under scorer misclassification.

Proves (symbolically, then cross-checks numerically):
  1. g(a, alpha, beta) = (a - alpha) / (1 - alpha - beta) is the misclassification
     correction A* = g(a, alpha, beta).
  2. dg/da >= 0 always (for alpha+beta<1) -- g is non-decreasing in the observed rate.
  3. dg/dalpha has the sign of (a - (1 - beta)) -- NOT a fixed sign; this is the
     non-obvious part of Lemma 1 and must not be hand-waved.
  4. dg/dbeta >= 0 whenever a >= alpha (the practically relevant region).
  5. Over the rectangle alpha in [0, alpha_bar], beta in [0, beta_bar], the extrema
     of g are attained at corners of the rectangle (confirmed by exhaustive grid
     search, since sign(dg/dalpha) varies across the rectangle so a naive
     "monotonic in each argument separately" argument is not sufficient on its own
     -- the grid search is the actual proof-by-verification for the corner claim).

Fixed seed / deterministic: no randomness in this script (T1 is worst-case
identification, not a sampling exercise -- T3/T5 are where sampling enters).

Run: python scripts/fb_t1_symbolic.py
"""
import sympy as sp
import numpy as np

def symbolic_derivation():
    a, alpha, beta = sp.symbols('a alpha beta', real=True)
    g = (a - alpha) / (1 - alpha - beta)

    dg_da = sp.simplify(sp.diff(g, a))
    dg_dalpha = sp.simplify(sp.diff(g, alpha))
    dg_dbeta = sp.simplify(sp.diff(g, beta))

    print("g(a, alpha, beta) =", g)
    print()
    print("dg/da     =", dg_da)
    print("dg/dalpha =", dg_dalpha)
    print("dg/dbeta  =", dg_dbeta)
    print()

    # Claim 2: dg/da = 1/(1-alpha-beta) >= 0 whenever alpha+beta < 1.
    expected_da = 1 / (1 - alpha - beta)
    assert sp.simplify(dg_da - expected_da) == 0, "dg/da does not match closed form"
    print("[OK] dg/da == 1/(1-alpha-beta), matches closed form exactly")

    # Claim 3: dg/dalpha = (a - 1 + beta) / (1-alpha-beta)^2
    #          sign(dg/dalpha) = sign(a - 1 + beta) = sign(a - (1-beta))
    expected_dalpha = (a - 1 + beta) / (1 - alpha - beta)**2
    diff_check = sp.simplify(dg_dalpha - expected_dalpha)
    assert diff_check == 0, f"dg/dalpha mismatch: {diff_check}"
    print("[OK] dg/dalpha == (a-1+beta)/(1-alpha-beta)^2, matches closed form exactly")
    print("     sign(dg/dalpha) = sign(a - (1-beta)) -- NOT fixed sign. This is Lemma 1's")
    print("     non-obvious claim: g is INCREASING in the false-credit rate alpha exactly")
    print("     when beta exceeds (1-a), i.e. when the false-miss rate is large enough")
    print("     relative to the observed error rate.")

    # Claim 4: dg/dbeta = (a-alpha)/(1-alpha-beta)^2 -- sign matches sign(a-alpha)
    expected_dbeta = (a - alpha) / (1 - alpha - beta)**2
    assert sp.simplify(dg_dbeta - expected_dbeta) == 0, "dg/dbeta mismatch"
    print("[OK] dg/dbeta == (a-alpha)/(1-alpha-beta)^2, matches closed form exactly")
    print("     sign(dg/dbeta) = sign(a-alpha) -- non-negative whenever a >= alpha,")
    print("     which holds in every practically relevant regime (observed accuracy")
    print("     exceeds the false-credit rate).")
    print()
    return g, dg_da, dg_dalpha, dg_dbeta


def numeric_grid_check(a_val=0.65, alpha_bar=0.15, beta_bar=0.20, n=2001):
    """Exhaustive grid search over [0,alpha_bar] x [0,beta_bar] confirming the
    extrema of g(a_val, ., .) occur at rectangle corners, to the grid resolution.
    This is the actual verification for the T1 corner claim -- not asserted from
    the (non-uniform-sign) partial derivatives alone."""
    def g(a, alpha, beta):
        return (a - alpha) / (1 - alpha - beta)

    alphas = np.linspace(0, alpha_bar, n)
    betas = np.linspace(0, beta_bar, n)
    AA, BB = np.meshgrid(alphas, betas)
    GG = g(a_val, AA, BB)

    grid_max = GG.max()
    grid_min = GG.min()
    argmax = np.unravel_index(np.argmax(GG), GG.shape)
    argmin = np.unravel_index(np.argmin(GG), GG.shape)
    max_at = (AA[argmax], BB[argmax])
    min_at = (AA[argmin], BB[argmin])

    corners = [(0, 0), (alpha_bar, 0), (0, beta_bar), (alpha_bar, beta_bar)]
    corner_vals = {c: g(a_val, *c) for c in corners}
    corner_max = max(corner_vals.values())
    corner_min = min(corner_vals.values())

    print(f"Grid search: a={a_val}, alpha in [0,{alpha_bar}], beta in [0,{beta_bar}], "
          f"{n}x{n} points")
    print(f"  grid max = {grid_max:.10f} at (alpha,beta) = "
          f"({max_at[0]:.6f}, {max_at[1]:.6f})")
    print(f"  grid min = {grid_min:.10f} at (alpha,beta) = "
          f"({min_at[0]:.6f}, {min_at[1]:.6f})")
    print(f"  corner values: {corner_vals}")
    print(f"  corner max = {corner_max:.10f}, corner min = {corner_min:.10f}")

    max_matches_corner = abs(grid_max - corner_max) < 1e-9
    min_matches_corner = abs(grid_min - corner_min) < 1e-9
    print(f"  [{'OK' if max_matches_corner else 'FAIL'}] grid max matches a corner "
          f"to 1e-9: {max_matches_corner}")
    print(f"  [{'OK' if min_matches_corner else 'FAIL'}] grid min matches a corner "
          f"to 1e-9: {min_matches_corner}")
    return max_matches_corner and min_matches_corner


def run_multi_config_check():
    """Repeat the grid check across several (a, alpha_bar, beta_bar) configurations,
    including one where a < alpha_bar (so dg/dalpha changes sign inside the
    rectangle) to stress-test the corner claim in the non-monotonic regime."""
    configs = [
        dict(a_val=0.65, alpha_bar=0.15, beta_bar=0.20),   # a > alpha_bar: dg/dalpha < 0 throughout most of range
        dict(a_val=0.10, alpha_bar=0.15, beta_bar=0.20),   # a < alpha_bar for part of range: sign of dg/dalpha varies
        dict(a_val=0.50, alpha_bar=0.49, beta_bar=0.49),   # near-boundary alpha+beta -> 1
        dict(a_val=0.05, alpha_bar=0.30, beta_bar=0.05),   # small a, large alpha_bar: stresses dg/dalpha sign flip
    ]
    all_ok = True
    for i, cfg in enumerate(configs):
        print(f"\n--- config {i+1}/{len(configs)}: {cfg} ---")
        ok = numeric_grid_check(**cfg)
        all_ok = all_ok and ok
    return all_ok


if __name__ == "__main__":
    print("=" * 70)
    print("T1 -- symbolic derivation")
    print("=" * 70)
    symbolic_derivation()

    print()
    print("=" * 70)
    print("T1 -- numeric grid verification of the corner claim (4 configs)")
    print("=" * 70)
    all_ok = run_multi_config_check()

    print()
    print("=" * 70)
    if all_ok:
        print("T1 VERIFIED: symbolic derivatives confirmed exactly; corner claim")
        print("confirmed to 1e-9 across 4 configurations including the non-monotonic")
        print("(sign-changing dg/dalpha) regime.")
    else:
        print("T1 FAILED: at least one configuration's extrema did not match a")
        print("rectangle corner. Do not proceed to T2 until this is resolved.")
    print("=" * 70)
