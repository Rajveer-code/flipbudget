"""Build the row cache for the reproducibility check: for every (model, key) row
whose key is in the corrected nondeterminism-flagged set (see
fb_ifeval_mechanism_rescan.py), cache the real doc + real response text, plus
the strict/loose verdict already on record in ifeval_full_roster.json (the
value obtained the first time this row was pulled -- one realization, kept as
a reference point, not treated as ground truth given the mechanism is random).

Fetches each of the 27 models once (network + HF token required), reused by
the reproducibility check so replicate runs never touch the network.

Run: python scripts/fb_ifeval_repro_cache.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from fb_eb_ifeval_pull import fetch_model_ifeval, load_roster_models
from huggingface_hub import get_token
import truststore
truststore.inject_into_ssl()

OUT_PATH = Path("results/flipbudget/ifeval_repro_rowcache.json")


def load_flagged_keys():
    with open("results/flipbudget/ifeval_nondeterminism_flagged_items.json", encoding="utf-8") as f:
        return set(json.load(f)["flagged_keys"].keys())


def load_roster_original():
    with open("results/analysis/ifeval_full_roster.json", encoding="utf-8") as f:
        return json.load(f)["population"]


if __name__ == "__main__":
    print("=" * 70)
    print("IFEval reproducibility row cache: fetch flagged-item rows once")
    print("=" * 70)

    token = get_token()
    if not token:
        raise SystemExit("No local HF token found (huggingface_hub.get_token()).")

    flagged_keys = load_flagged_keys()
    print(f"Flagged keys (corrected scan): {len(flagged_keys)} of 541 items")

    roster = load_roster_original()
    roster_by_mk = {(r["model"], r["key"]): r for r in roster}
    print(f"Roster loaded: {len(roster)} rows")

    models = load_roster_models()
    rows = []
    n_missing_roster = 0
    for i, model in enumerate(models, 1):
        raw = fetch_model_ifeval(model, token)
        n_kept = 0
        for r in raw:
            doc = r["doc"]
            key = doc["key"]
            if str(key) not in flagged_keys:
                continue
            resps = r.get("resps") or r.get("filtered_resps") or []
            if not resps:
                continue
            response = resps[0][0] if isinstance(resps[0], list) else resps[0]
            if not isinstance(response, str):
                continue
            orig = roster_by_mk.get((model, key))
            if orig is None:
                n_missing_roster += 1
                orig_strict, orig_loose = None, None
            else:
                orig_strict, orig_loose = orig["strict"], orig["loose"]
            rows.append({
                "model": model, "key": key, "doc": doc, "response": response,
                "roster_original_strict": orig_strict, "roster_original_loose": orig_loose,
            })
            n_kept += 1
        print(f"  [{i}/{len(models)}] {model}: {n_kept} flagged-item rows cached")

    print(f"\nTotal cached rows: {len(rows)} (expected up to {len(flagged_keys)}*{len(models)}="
          f"{len(flagged_keys)*len(models)})")
    print(f"Rows with no matching roster entry (unexpected): {n_missing_roster}")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"n_rows": len(rows), "rows": rows}, f)
    print(f"Written to {OUT_PATH}")
