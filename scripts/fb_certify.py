"""G2.4 -- certification of MATH-Hard orderings on the existing audit, K=2 and K=3.

Primary configuration (G1 decisions): 27 models, faithful sympy semantics for the boxed
verifier, human reference = harness routine (sympy), indeterminate labels as incorrect,
KL intervals (Lemma 1), paired conservative sampling half-width (theory section 6).
Discordant cells are [0, 1]: the old audit is stratified across models, so a per-model
discordant estimate would target a stratum mixture, not p_mc (THEORY section 0).

Sensitivities: string semantics (historical), Math-Verify human reference, indeterminate
dropped, Clopper-Pearson intervals, legacy unpaired and Hoeffding sampling, 17-model subset,
no pooling (per-model concordant intervals).

Run: python scripts/fb_certify.py        Out: results/flipbudget/certify_results.json
"""
import gzip
import json
import math
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from flipbudget import certify as C  # noqa: E402

CENSUS = ROOT / "results" / "flipbudget" / "census_k3.json.gz"
AUDIT = ROOT / "results" / "flipbudget" / "audit_k3_map.json"
OUT = ROOT / "results" / "flipbudget" / "certify_results.json"
N_ITEMS = 1324
ALPHA_A, ALPHA_S = 0.025, 0.025
EPS0 = 0.01  # preregistered scientific tolerance (THEORY 1.1c), a judgement, not a measurement
EPS_GRID = [round(0.0025 * i, 4) for i in range(41)]  # 0 .. 0.10


def spec(K, sem):
    """Verifier fields in cell-string order."""
    sb = f"sb_{sem}"
    return (sb, "em") if K == 2 else ("em", sb, "mv")


class Inputs:
    def __init__(self, census, audit, K, sem, ref, indet, models, interval, new_labels=None):
        """new_labels (G4.1, from scripts/fb_audit_v3_analysis.py): {"pooled": {cell: [x, n]},
        "disc": {(model, cell): [x, n]}} from the v3 audit. Concordant labels join the pooled
        cells; discordant labels give per-model intervals, which are design-valid because the
        v3 strata are (model x cell). Omitted -> the pre-v3 analysis, unchanged."""
        self.K, self.models, self.fields = K, models, spec(K, sem)
        rows = [r for r in census["rows"] if r["model"] in set(models)]
        items = sorted({r["item_id"] for r in rows})
        col = {i: n for n, i in enumerate(items)}
        self.V = {f: np.zeros((len(models), len(items)), dtype=np.int8) for f in self.fields}
        idx = {m: n for n, m in enumerate(models)}
        counts = {m: defaultdict(int) for m in models}
        for r in rows:
            for f in self.fields:
                self.V[f][idx[r["model"]], col[r["item_id"]]] = r[f]
            counts[r["model"]]["".join(str(r[f]) for f in self.fields)] += 1
        self.shares = {m: {c: v / N_ITEMS for c, v in counts[m].items()} | {"N": N_ITEMS} for m in models}
        self.cells = sorted({c for m in models for c in counts[m]})
        self.conc_cells = ["0" * K, "1" * K]
        self.idx = idx
        # audit counts (pooled per concordant cell, and per model for the no-pooling analysis)
        cell_key = f"k{K}_{sem}"
        pooled = {c: [0, 0] for c in self.conc_cells}
        per_model = {m: {c: [0, 0] for c in self.conc_cells} for m in models}
        subpop = {c: defaultdict(int) for c in self.conc_cells}
        for it in audit["items"]:
            if it["model"] not in idx or it[cell_key] not in pooled:
                continue
            if it["indeterminate"] and indet == "drop":
                continue
            y = 0 if it["indeterminate"] else it["ystar"][ref]
            c = it[cell_key]
            pooled[c][0] += y
            pooled[c][1] += 1
            per_model[it["model"]][c][0] += y
            per_model[it["model"]][c][1] += 1
            subpop[c][(it["key_stratum"], it.get("subject"), it.get("quartile"), it["model"])] += 1
        nl = new_labels or {}
        self.pooled_existing = {c: list(v) for c, v in pooled.items()}
        for c, (x, n) in (nl.get("pooled") or {}).items():
            if c in pooled:
                pooled[c][0] += x
                pooled[c][1] += n
        for m in models:  # v3 concordant labels are per (model, cell) too
            for c in self.conc_cells:
                x, n = (nl.get("disc_and_conc_per_model") or {}).get((m, c), (0, 0))
                per_model[m][c][0] += x
                per_model[m][c][1] += n
        self.pooled, self.per_model, self.subpop = pooled, per_model, subpop
        self.ivl = C.kl_interval if interval == "kl" else C.cp_interval
        ivl = self.ivl
        self.level = C.sidak(2, 1 - ALPHA_A)
        self.conc = {c: ivl(*pooled[c], self.level) for c in self.conc_cells}
        self.conc_pm = {m: {c: ivl(*per_model[m][c], C.sidak(4, 1 - ALPHA_A)) for c in self.conc_cells}
                        for m in models}
        self.disc = {c: (0.0, 1.0) for c in self.cells if c not in self.conc_cells}
        self.disc_counts = {k: v for k, v in (nl.get("disc") or {}).items() if k[1] in self.disc}
        # pairwise verifier disagreement d^v_jk (item-matched)
        self.d = {}
        for j, k in combinations(models, 2):
            a, b = idx[j], idx[k]
            self.d[(j, k)] = {f: float(np.mean(self.V[f][a] != self.V[f][b])) for f in self.fields}

    def acc(self, m, f):
        return float(self.V[f][self.idx[m]].mean())

    def n_audited_disc(self, m):
        """Number of discordant parameters of model m estimated from v3 labels."""
        return sum(1 for (mm, c) in self.disc_counts if mm == m)

    def disc_bounds(self, m, level):
        """Per-model discordant intervals: KL/CP from v3 labels where they exist, else [0, 1]."""
        return {c: (self.ivl(*self.disc_counts[(m, c)], level) if (m, c) in self.disc_counts else (0.0, 1.0))
                for c in self.disc}

    def ebar(self, m, conc, eps, disc=None):
        pb = C.model_p_bounds(conc, self.disc if disc is None else disc, eps)
        return {f: C.error_bound(self.shares[m], {c: int(c[n]) for c in self.cells}, pb)
                for n, f in enumerate(self.fields)}

    def pair_bounds(self, j, k):
        """(conc, disc_j, disc_k) at the Sidak level for the parameters this ordering uses:
        the two pooled concordant cells plus each model's v3-audited discordant cells."""
        kk = 2 + self.n_audited_disc(j) + self.n_audited_disc(k)
        lvl = C.sidak(kk, 1 - ALPHA_A)
        conc = {c: self.ivl(*self.pooled[c], lvl) for c in self.conc_cells}
        return conc, self.disc_bounds(j, lvl), self.disc_bounds(k, lvl)

    def halfwidth(self, mode, z, conc=None):
        def h(j, k, eps):
            if mode == "none":
                return 0.0
            if mode == "hoeffding":
                return C.halfwidth_hoeffding(N_ITEMS, 2 * (1 - norm.cdf(z)))
            if mode == "legacy":  # unpaired plug-in from the boxed verifier's accuracy (anchor only)
                a = [self.acc(m, self.fields[0] if self.K == 2 else self.fields[1]) for m in (j, k)]
                return z * math.sqrt(sum(x * (1 - x) for x in a) / N_ITEMS)
            cj, dj, dk = self.pair_bounds(j, k)
            cc = conc if conc is not None else cj
            return C.halfwidth_paired(self.d[(j, k)], self.ebar(j, cc, eps, dj), self.ebar(k, cc, eps, dk),
                                      N_ITEMS, z)
        return h


def run(inp, eps, sampling="paired", simultaneous=False, pooling=True):
    npairs = len(inp.models) * (len(inp.models) - 1) // 2
    z = float(norm.ppf(1 - ALPHA_S / 2 / (npairs if simultaneous else 1)))
    if pooling:
        bounds = inp.pair_bounds
    else:  # no pooling: per-model concordant intervals enter as model-specific (discordant-like) bounds
        def bounds(j, k):
            lvl = C.sidak(4 + inp.n_audited_disc(j) + inp.n_audited_disc(k), 1 - ALPHA_A)
            return {}, inp.disc_bounds(j, lvl) | inp.conc_pm[j], inp.disc_bounds(k, lvl) | inp.conc_pm[k]
    return C.evaluate(inp.models, inp.shares, bounds, inp.halfwidth(sampling, z), eps)


def ceiling(inp, simultaneous=False):
    """Orderings each verifier alone separates beyond paired sampling noise (no verifier error)."""
    npairs = len(inp.models) * (len(inp.models) - 1) // 2
    z = float(norm.ppf(1 - ALPHA_S / 2 / (npairs if simultaneous else 1)))
    return {f: sum(abs(inp.acc(j, f) - inp.acc(k, f)) > z * math.sqrt(inp.d[(j, k)][f] / N_ITEMS)
                   for j, k in combinations(inp.models, 2)) for f in inp.fields}


def breakdowns(inp, sampling="paired"):
    z = float(norm.ppf(1 - ALPHA_S / 2))
    h = inp.halfwidth(sampling, z)
    out = {}
    for j, k in combinations(inp.models, 2):
        conc, dj, dk = inp.pair_bounds(j, k)

        def margin(e, sign, conc=conc, dj=dj, dk=dk, j=j, k=k):
            lo, hi = C.pair_range(inp.shares[j], inp.shares[k], conc, dj, dk, e)
            return (lo if sign > 0 else -hi) - h(j, k, e)
        e_pos, e_neg = C.breakdown_eps(lambda e: margin(e, 1)), C.breakdown_eps(lambda e: margin(e, -1))
        if e_pos > 0 or e_neg > 0:
            out[f"{j} > {k}" if e_pos > 0 else f"{k} > {j}"] = max(e_pos, e_neg)
    return out


def eps_reference_a(inp):
    """THEORY 1.1(a): max_c u_c / min_g w_gc over sampled audit sub-populations."""
    refs = {}
    for c in inp.conc_cells:
        n = inp.pooled[c][1]
        if n == 0:
            continue
        err_hi = inp.conc[c][1] if c == "0" * inp.K else 1 - inp.conc[c][0]
        w_min = min(inp.subpop[c].values()) / n
        refs[c] = {"u_c": err_hi, "min_weight": w_min, "bound": err_hi / w_min,
                   "n_sampled_subpops": len(inp.subpop[c])}
    return {"per_cell": refs, "eps_ref_a": max(v["bound"] for v in refs.values())}


def summary(inp):
    return {"n_models": len(inp.models), "n_pairs": len(inp.d), "cells": inp.cells,
            "audit_pooled": {c: {"x_correct": x, "n": n} for c, (x, n) in inp.pooled.items()},
            "conc_intervals": inp.conc, "interval_level": inp.level}


def main():
    census = json.load(gzip.open(CENSUS, "rt", encoding="utf-8"))
    audit = json.load(open(AUDIT, encoding="utf-8"))
    key = {k["uid"]: k for k in json.load(open(ROOT / "results" / "analysis" / "mathhard_labelling_key.json",
                                                encoding="utf-8"))}
    for it in audit["items"]:  # design strata of the old audit
        it["subject"], it["quartile"] = key[it["uid"]]["subject"], key[it["uid"]]["quartile"]
    m27, m17 = census["models"], audit["models17"]
    out = {"config": {"alpha_audit": ALPHA_A, "alpha_sampling": ALPHA_S, "eps0_preregistered": EPS0,
                      "eps_grid": EPS_GRID, "n_items": N_ITEMS}}
    for K in (2, 3):
        prim = Inputs(census, audit, K, "sympy", "sympy", "as_incorrect", m27, "kl")
        res = {"inputs": summary(prim), "ceiling": ceiling(prim), "ceiling_simultaneous": ceiling(prim, True),
               "eps_reference_a": eps_reference_a(prim)}
        res["eps_curve"] = []
        for e in EPS_GRID:
            a, s = run(prim, e), run(prim, e, simultaneous=True)
            res["eps_curve"].append({"eps": e, "audit_only": a["audit_resolved"], "combined": a["combined_resolved"],
                                     "combined_simultaneous": s["combined_resolved"]})
        at0 = run(prim, 0.0)
        sim0 = run(prim, 0.0, simultaneous=True)
        res["eps0_pairs"] = at0["pairs"]
        cert = lambda r: {(p["winner"], [x for x in p["pair"] if x != p["winner"]][0])  # noqa: E731
                          for p in r["pairs"] if p["winner"]}
        res["rank_intervals_simultaneous_eps0"] = C.rank_intervals(m27, cert(sim0))
        res["rank_intervals_per_ordering_eps0_NOT_FAMILYWISE"] = C.rank_intervals(m27, cert(at0))
        res["breakdown_eps"] = breakdowns(prim)
        res["no_pooling"] = {k: v for k, v in run(prim, 0.0, pooling=False).items() if k != "pairs"}
        sens = {}
        for name, args in {
            "string_semantics": (K, "string", "string", "as_incorrect", m27, "kl"),
            "mv_reference": (K, "sympy", "mv", "as_incorrect", m27, "kl"),
            "indeterminate_dropped": (K, "sympy", "sympy", "drop", m27, "kl"),
            "clopper_pearson": (K, "sympy", "sympy", "as_incorrect", m27, "cp"),
            "models17": (K, "sympy", "sympy", "as_incorrect", m17, "kl"),
        }.items():
            inp = Inputs(census, audit, *args)
            r0 = run(inp, 0.0)
            sens[name] = {"audit_pooled": summary(inp)["audit_pooled"], "audit_only": r0["audit_resolved"],
                          "combined": r0["combined_resolved"], "ceiling": ceiling(inp),
                          "combined_eps0": [run(inp, e)["combined_resolved"] for e in (0.0, EPS0)]}
        for mode in ("legacy", "hoeffding"):
            r0 = run(prim, 0.0, sampling=mode)
            sens[f"sampling_{mode}"] = {"combined": r0["combined_resolved"]}
        res["sensitivity"] = sens
        out[f"K{K}"] = res
        c0 = res["eps_curve"][0]
        print(f"K={K}: audit-only {c0['audit_only']}, combined {c0['combined']}, simultaneous "
              f"{c0['combined_simultaneous']}, ceiling {res['ceiling']}, eps_ref_a {res['eps_reference_a']['eps_ref_a']:.4f}")
        print("   eps curve:", [(x["eps"], x["combined"]) for x in res["eps_curve"][::4]])
        print("   no pooling:", res["no_pooling"], "| n breakdowns:", len(res["breakdown_eps"]))
        print("   sensitivity:", {k: (v.get("audit_only"), v["combined"]) for k, v in sens.items()})
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, default=float)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
