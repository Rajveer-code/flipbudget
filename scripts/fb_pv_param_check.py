# Compare current map g(a,alpha,beta)=(a-alpha)/(1-alpha-beta) using stratum-conditional
# rates (alpha_raw = P(Y*=0|Yhat=1), beta_raw = P(Y*=1|Yhat=0)) vs the predictive-value
# identity A* = a(1-q) + (1-a) r that those stratum rates actually support.
import sys, json, numpy as np
from itertools import combinations
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
from ea_dominance_study import load, build_model_table
import fb_ea_dominance_canonical as C
Z=1.96
accs, margins = load()
rows, _ = build_model_table(accs, margins)
print("qualifying models:", len(rows))
for m,r in sorted(rows.items(), key=lambda kv: kv[1]["a_hat"]):
    print(f"  {m[:38]:38s} a={r['a_hat']:.3f} n_bench={r['n_bench']} cred {r['x_alpha']}/{r['n0_audit']} wrong {r['x_beta']}/{r['n1_audit']}")
def pv_ext(a, box):
    qlo,qhi,rlo,rhi = box
    return a*(1-qhi)+(1-a)*rlo, a*(1-qlo)+(1-a)*rhi
cur, pv, dom_pv = [], [], 0
empty_cur=0
for m1,m2 in combinations(sorted(rows),2):
    r1,r2=rows[m1],rows[m2]
    a1,a2=r1["a_hat"],r2["a_hat"]
    ws=2*Z*np.sqrt(a1*(1-a1)/r1["n_bench"]+a2*(1-a2)/r2["n_bench"])
    b1=r1["alpha_ci"]+r1["beta_ci"]; b2=r2["alpha_ci"]+r2["beta_ci"]
    lo,hi=C.bounded_comparison(a1,b1,a2,b2)
    if np.isnan(lo): empty_cur+=1
    else: cur.append((hi-lo)/ws)
    l1,h1=pv_ext(a1,b1); l2,h2=pv_ext(a2,b2)
    w=(h1-l2)-(l1-h2); pv.append(w/ws)
    # sign resolved?
cur=np.array(cur); pv=np.array(pv)
print(f"current map: n_valid={len(cur)} empty={empty_cur} median={np.median(cur):.3f} min={cur.min():.3f}")
print(f"PV map     : n_valid={len(pv)} empty=0 median={np.median(pv):.3f} min={pv.min():.3f} %>1={100*np.mean(pv>1):.1f}")
