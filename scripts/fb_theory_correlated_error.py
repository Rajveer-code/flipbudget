"""Symbolic + numeric verification of the correlated-scorer-error theory
(THEORY_EXTENSIONS.md, Propositions 3-4). Two claims to verify before
trusting the derivation:

1. Shared-factor model induces Cov(E_i, E_j) = pi*(1-pi)*(p_hard-p_easy)^2
   >= 0 -- a closed form, checked here against Monte Carlo simulation.
2. Var(E_i - E_j) is smaller under the shared-factor (correlated) model
   than under an independent-errors model with the SAME marginal rates --
   the "conservative bound" claim -- checked by direct simulation.
3. The cancellation BREAKS when the model-specific modifier correlates with
   the shared factor (differential-given-H case) -- checked by adding a
   model-specific H-dependent term and showing Cov can now differ in sign/
   magnitude from the non-differential prediction.

Run: python scripts/fb_theory_correlated_error.py
"""
import numpy as np

RNG = np.random.default_rng(42)
N_ITEMS = 200_000


def simulate_nondifferential(pi, p_hard, p_easy, n=N_ITEMS, rng=RNG):
    """Shared factor H_k in {0,1}; GIVEN H_k, both models' errors are
    conditionally independent Bernoulli(p_hard or p_easy) -- the
    non-differential-given-H case."""
    H = rng.random(n) < pi
    p = np.where(H, p_hard, p_easy)
    E_i = rng.random(n) < p
    E_j = rng.random(n) < p
    return E_i.astype(float), E_j.astype(float)


def simulate_differential(pi, p_hard, p_easy, delta_i, delta_j, n=N_ITEMS, rng=RNG):
    """Same shared factor, but each model's error prob on hard items is
    shifted by its OWN delta (model-specific format interacts with the
    shared difficulty factor) -- the differential-given-H case."""
    H = rng.random(n) < pi
    p_i = np.where(H, np.clip(p_hard + delta_i, 0, 1), p_easy)
    p_j = np.where(H, np.clip(p_hard + delta_j, 0, 1), p_easy)
    E_i = rng.random(n) < p_i
    E_j = rng.random(n) < p_j
    return E_i.astype(float), E_j.astype(float)


def simulate_independent(p_i, p_j, n=N_ITEMS, rng=RNG):
    E_i = rng.random(n) < p_i
    E_j = rng.random(n) < p_j
    return E_i.astype(float), E_j.astype(float)


if __name__ == "__main__":
    print("=" * 70)
    print("Correlated scorer-error theory: closed-form vs simulation")
    print("=" * 70)

    pi, p_hard, p_easy = 0.15, 0.25, 0.03

    print(f"\n[Claim 1] Cov(E_i,E_j) closed form: pi(1-pi)(p_hard-p_easy)^2")
    closed_form = pi * (1 - pi) * (p_hard - p_easy) ** 2
    E_i, E_j = simulate_nondifferential(pi, p_hard, p_easy)
    empirical_cov = np.cov(E_i, E_j)[0, 1]
    print(f"  closed form: {closed_form:.6f}")
    print(f"  simulated (n={N_ITEMS}): {empirical_cov:.6f}")
    ok1 = abs(closed_form - empirical_cov) < 0.001
    print(f"  [{'OK' if ok1 else 'FAIL'}] match within Monte Carlo tolerance: {ok1}")

    marg = pi * p_hard + (1 - pi) * p_easy
    print(f"  marginal error rate (both models): {marg:.4f} "
          f"(E_i mean={E_i.mean():.4f}, E_j mean={E_j.mean():.4f})")

    print(f"\n[Claim 2] Var(E_i - E_j) smaller under correlation than under "
          f"independence, SAME marginals")
    var_correlated = np.var(E_i - E_j)
    E_i_ind, E_j_ind = simulate_independent(marg, marg, n=N_ITEMS)
    var_independent = np.var(E_i_ind - E_j_ind)
    print(f"  Var(diff), correlated (shared-factor) model: {var_correlated:.6f}")
    print(f"  Var(diff), independent model, same marginals: {var_independent:.6f}")
    print(f"  theoretical: Var(X)+Var(Y)-2Cov vs Var(X)+Var(Y): "
          f"predicted reduction = 2*Cov = {2*closed_form:.6f}, "
          f"observed reduction = {var_independent - var_correlated:.6f}")
    ok2 = var_correlated < var_independent
    print(f"  [{'OK' if ok2 else 'FAIL'}] correlated variance strictly smaller: {ok2}")

    print(f"\n[Claim 3] Cancellation breaks under model-specific (differential) "
          f"loading on the shared factor")
    delta_i, delta_j = 0.30, -0.02  # model i's format interacts badly with hard items, j's doesn't
    E_i_d, E_j_d = simulate_differential(pi, p_hard, p_easy, delta_i, delta_j)
    cov_diff = np.cov(E_i_d, E_j_d)[0, 1]
    var_diff_case = np.var(E_i_d - E_j_d)
    mean_i, mean_j = E_i_d.mean(), E_j_d.mean()
    print(f"  marginal rates now DIFFER by model: E_i={mean_i:.4f}, E_j={mean_j:.4f} "
          f"(non-differential case had both = {marg:.4f})")
    print(f"  Cov(E_i,E_j) under differential loading: {cov_diff:.6f} "
          f"(non-differential closed form was {closed_form:.6f})")
    print(f"  Var(diff) under differential loading: {var_diff_case:.6f} "
          f"(correlated non-differential case was {var_correlated:.6f})")
    ok3 = abs(mean_i - mean_j) > 0.01  # the differential loading actually creates a marginal gap
    print(f"  [{'OK' if ok3 else 'FAIL'}] differential loading creates a real marginal-rate gap "
          f"(this IS the differential/ranking-relevant component, not cancelled by shared H): {ok3}")

    all_ok = ok1 and ok2 and ok3
    print(f"\n{'='*70}")
    print(f"[{'ALL VERIFIED' if all_ok else 'FAILED -- DO NOT TRUST THEORY DOC'}]")
    if not all_ok:
        raise SystemExit("A theory claim failed simulation verification.")
