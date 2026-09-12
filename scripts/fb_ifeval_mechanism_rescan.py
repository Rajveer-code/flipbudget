"""Comprehensive rescan of all 541 IFEval items for EVERY verifier nondeterminism
mechanism -- not just the 2 originally found. Run before trusting any downstream
reproducibility number, because the original 33-item flagged set (response_language
+ letter_frequency-invalid-letter only) was discovered to be incomplete: source
inspection of instructions.py showed langdetect.detect() is ALSO called, unseeded,
by change_case:english_capital and change_case:english_lowercase -- two more
checker types never scanned for. This script re-derives the flagged set from
source, two ways, not one:

  Type-1 (checker-class nondeterminism, unconditional): any instruction whose
  check_following() calls langdetect.detect() -- confirmed from
  langdetect/detector.py: self.random.seed(self.seed) with self.seed=None when
  DetectorFactory.seed is never set, so the algorithm's internal n-gram
  subsampling is OS-entropy-seeded on every call, regardless of kwargs.
  Static membership check: language:response_language, change_case:english_capital,
  change_case:english_lowercase.

  Type-2 (kwarg-dependent nondeterminism): any instruction whose build_description
  falls back to random.choice/randint because the DATASET's own kwargs for that
  item left a field None or invalid (e.g. letter='!' fails the a-z check).
  Detected empirically, not by hand-mapping every field name: monkeypatch
  random.choice/randint, call the REAL process_results() for each item with a
  placeholder response, and record whether global random state was touched.
  This is what the real harness executes, so it catches everything the harness
  can trigger -- not just the two mechanisms found by manual inspection.

Run: python scripts/fb_ifeval_mechanism_rescan.py
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from fb_eb_ifeval_pull import fetch_model_ifeval, load_roster_models, load_ifeval_verifier
from huggingface_hub import get_token
import truststore
truststore.inject_into_ssl()

LANGDETECT_CHECKER_IDS = {
    "language:response_language",
    "change_case:english_capital",
    "change_case:english_lowercase",
}

OLD_FLAGGED_PATH = Path("results/flipbudget/ifeval_nondeterminism_flagged_items.json")
OUT_PATH = Path("results/flipbudget/ifeval_nondeterminism_flagged_items.json")

# Fixed historical fact: the original, incomplete scan (before this script
# existed) flagged 33/541 items, checking only language:response_language
# and keywords:letter_frequency. See IFEVAL_REPRODUCIBILITY_CHECK.md.
ORIGINAL_SCAN_N_FLAGGED = 33


def fetch_all_docs(token):
    models = load_roster_models()
    rows = fetch_model_ifeval(models[0], token)
    docs = {}
    for r in rows:
        d = r["doc"]
        docs[d["key"]] = d
    return docs, models[0]


def type1_langdetect_ids(doc):
    return sorted(set(doc["instruction_id_list"]) & LANGDETECT_CHECKER_IDS)


def type2_random_fallback(doc, process_results):
    """Empirically detect kwarg-dependent randomness: monkeypatch random.choice
    and random.randint, run the real scorer once on a placeholder response, and
    see if either was called. Restores the real functions immediately after."""
    calls = {"choice": 0, "randint": 0}
    real_choice, real_randint = random.choice, random.randint

    def counting_choice(seq):
        calls["choice"] += 1
        return real_choice(seq)

    def counting_randint(a, b):
        calls["randint"] += 1
        return real_randint(a, b)

    random.choice = counting_choice
    random.randint = counting_randint
    try:
        process_results(doc, ["placeholder response for mechanism detection"])
    except Exception as e:
        return calls, str(e)
    finally:
        random.choice = real_choice
        random.randint = real_randint
    return calls, None


if __name__ == "__main__":
    print("=" * 70)
    print("IFEval mechanism rescan -- comprehensive, source-verified")
    print("=" * 70)

    token = get_token()
    if not token:
        raise SystemExit("No local HF token found (huggingface_hub.get_token()).")

    docs, doc_source_model = fetch_all_docs(token)
    print(f"Docs fetched from: {doc_source_model} ({len(docs)} unique items)")

    process_results = load_ifeval_verifier()

    flagged = {}
    n_type1_only, n_type2_only, n_both = 0, 0, 0
    errors = []
    for key, doc in sorted(docs.items()):
        t1 = type1_langdetect_ids(doc)
        calls, err = type2_random_fallback(doc, process_results)
        if err:
            errors.append({"key": key, "error": err})
            continue
        t2_triggered = calls["choice"] > 0 or calls["randint"] > 0
        mechanisms = []
        if t1:
            mechanisms.append({"type": "langdetect_unseeded", "checker_ids": t1})
        if t2_triggered:
            mechanisms.append({"type": "random_fallback_kwarg", "random_calls": calls})
        if mechanisms:
            flagged[str(key)] = mechanisms
            if t1 and t2_triggered:
                n_both += 1
            elif t1:
                n_type1_only += 1
            else:
                n_type2_only += 1

    print(f"\nTotal items scanned: {len(docs)}")
    print(f"Errors during scan (skipped, not counted): {len(errors)}")
    for e in errors:
        print(f"  key {e['key']}: {e['error']}")
    print(f"\nFlagged (any mechanism): {len(flagged)}")
    print(f"  langdetect-only: {n_type1_only}")
    print(f"  random-fallback-only: {n_type2_only}")
    print(f"  both mechanisms: {n_both}")

    # old_n is a fixed historical fact (the incomplete scan's count BEFORE this
    # script existed) -- NOT re-derived from OUT_PATH's live content.
    # OLD_FLAGGED_PATH and OUT_PATH are the same file, so on a re-run (e.g.
    # fb_reproduce_all.py's reproducibility check) reading "prior" from it
    # would compare this run against ITSELF: a real bug this project's own
    # reproducibility pipeline caught -- the first re-run silently replaced
    # the true historical 33 with 96 in the recorded "prior_n_flagged" field.
    old_n = ORIGINAL_SCAN_N_FLAGGED
    print(f"\nOriginal (pre-correction) flagged-set size: {old_n} (fixed historical constant)")

    if OLD_FLAGGED_PATH.exists():
        with open(OLD_FLAGGED_PATH, encoding="utf-8") as f:
            prev_run = json.load(f)
        prev_keys = set(prev_run.get("flagged_keys", {}).keys())
        new_keys = set(flagged.keys())
        idempotent = prev_keys == new_keys
        print(f"Idempotency check against the file currently on disk "
              f"({prev_run.get('n_flagged')} keys): "
              f"{'identical -- reproducible' if idempotent else 'DIFFERENT -- investigate before trusting'}")

    out = {
        "n_total_items": len(docs),
        "n_flagged": len(flagged),
        "n_flagged_langdetect_only": n_type1_only,
        "n_flagged_random_fallback_only": n_type2_only,
        "n_flagged_both_mechanisms": n_both,
        "doc_source_model": doc_source_model,
        "scan_errors": errors,
        "prior_n_flagged": old_n,
        "prior_scan_was_incomplete": True,
        "correction_note": (
            "Prior scan (n=33) checked only language:response_language and "
            "keywords:letter_frequency. This rescan additionally found "
            "change_case:english_capital and change_case:english_lowercase call "
            "unseeded langdetect.detect() (source: instructions.py lines ~1469, "
            "~1501), and empirically detects ANY kwarg-driven random.choice/"
            "randint fallback via monkeypatch rather than manual field mapping."
        ),
        "flagged_keys": flagged,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nWritten to {OUT_PATH}")
