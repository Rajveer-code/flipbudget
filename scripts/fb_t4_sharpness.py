"""T4 -- sharpness of the identified set.

Is every value in T1's corner-derived interval [g_min, g_max] actually
attainable by some admissible scorer behaviour (alpha,beta in the declared
box)? If yes, the bound is sharp -- tight, not a loose enclosure. If no,
characterise the gap.

Claim: YES, sharp, and constructively so -- g(a,alpha,beta) is continuous in
(alpha,beta) on the connected, convex feasible region {alpha>=0, beta>=0,
alpha+beta<cap} intersected with the box [alpha0-d,alpha0+d]x[beta0-d,beta0+d].
By the intermediate value theorem on a continuous function over a connected
domain whose boundary includes the two corners attaining g_min and g_max,
EVERY value between them is attained somewhere on the straight path between
those two corners (a path that stays inside the convex, hence connected,
feasible box). This is a genuine proof, not an assumption -- verified below
by direct construction: walk the straight line between the argmin and argmax
corners, confirm g is realized continuously and every requested intermediate
value has a real (alpha,beta) point on that segment realizing it to numerical
tolerance.

Run: python scripts/fb_t4_sharpness.py
"""
import numpy as np


def g(a, alpha, beta):
    return (a - alpha) / (1 - alpha - beta)


def find_corners(a, alpha0, beta0, d):
    cap = 0.999
    alphas = [max(0.0, alpha0 - d), min(1.0, alpha0 + d)]
    betas = [max(0.0, beta0 - d), min(1.0, beta0 + d)]
    corners = []
    for al in alphas:
        for be in betas:
            if al + be >= cap:
                be = cap - al - 1e-6
                if be < 0:
                    continue
            corners.append((al, be))
    vals = [g(a, al, be) for al, be in corners]
    imin, imax = int(np.argmin(vals)), int(np.argmax(vals))
    return corners[imin], vals[imin], corners[imax], vals[imax]


def sharpness_check(a=0.65, alpha0=0.05, beta0=0.10, d=0.05, n_probe=200):
    (a_min, b_min), g_min, (a_max, b_max), g_max = find_corners(a, alpha0, beta0, d)
    print(f"a={a}, alpha0={alpha0}, beta0={beta0}, d={d}")
    print(f"  argmin corner: (alpha,beta)=({a_min},{b_min}), g_min={g_min:.6f}")
    print(f"  argmax corner: (alpha,beta)=({a_max},{b_max}), g_max={g_max:.6f}")

    # walk the straight segment between the two corners; both endpoints are
    # inside the convex box, so every point on the segment is too (convexity)
    ts = np.linspace(0, 1, n_probe)
    alphas_path = a_min + ts * (a_max - a_min)
    betas_path = b_min + ts * (b_max - b_min)
    g_path = g(a, alphas_path, betas_path)

    # is g monotone (hence bijective, hence every intermediate value hit
    # exactly once) along this specific segment? Check numerically.
    diffs = np.diff(g_path)
    monotone = np.all(diffs >= -1e-9) or np.all(diffs <= 1e-9)
    print(f"  g is monotone along the argmin-argmax segment: {monotone}")

    # regardless of monotonicity, continuity + IVT guarantees every value in
    # [g_min,g_max] is hit somewhere on this connected path -- verify by
    # requesting several target values and confirming a path point matches
    targets = np.linspace(g_min, g_max, 11)
    max_err = 0.0
    for t in targets:
        idx = np.argmin(np.abs(g_path - t))
        err = abs(g_path[idx] - t)
        max_err = max(max_err, err)
    print(f"  max error finding a real (alpha,beta) realizing 11 probe targets "
          f"across [g_min,g_max]: {max_err:.6f} (probe resolution: "
          f"{(g_max-g_min)/n_probe:.6f})")
    sharp = max_err < 2 * (g_max - g_min) / n_probe + 1e-6
    print(f"  [{'OK' if sharp else 'FAIL'}] every probed target realized within "
          f"probe resolution -- bound is sharp on this segment: {sharp}")
    return sharp


if __name__ == "__main__":
    print("=" * 70)
    print("T4 -- sharpness of the identified set (constructive check)")
    print("=" * 70)
    configs = [
        dict(a=0.65, alpha0=0.05, beta0=0.10, d=0.05),
        dict(a=0.10, alpha0=0.15, beta0=0.20, d=0.10),  # non-monotone dg/dalpha regime
        dict(a=0.50, alpha0=0.45, beta0=0.45, d=0.04),  # near the alpha+beta->1 boundary
    ]
    all_ok = True
    for cfg in configs:
        print()
        ok = sharpness_check(**cfg)
        all_ok = all_ok and ok

    print()
    print("=" * 70)
    if all_ok:
        print("T4 VERIFIED: the identified set is sharp on every tested config --")
        print("every value between the corner-derived min and max is realized by")
        print("some real, feasible (alpha,beta), confirmed constructively along")
        print("the straight path connecting the two extremal corners (which stays")
        print("inside the box by convexity, so continuity + IVT applies rigorously,")
        print("not just plausibly).")
    else:
        print("T4 FAILED on at least one config -- do not claim sharpness without")
        print("further characterizing the gap.")
    print("=" * 70)
