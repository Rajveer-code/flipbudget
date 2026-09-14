"""Adversarial suite v2 (final validation phase, item 1 of the user's latest
directive). Two parts:

PART A -- principled 12-category taxonomy of CONSTRUCTED cases with known
ground truth, run through the REAL end-to-end harness function
(`process_results`, from vendor/leaderboard_math/utils.py) which computes
BOTH real scorers used anywhere in the actual leaderboard pipeline:
  - exact_match           (math_verify parse/verify -- THIS is the field
                            fb_e1_true_accuracy.py reads for a_hat)
  - exact_match_original   (get_unnormalized_answer + is_equiv -- THIS is
                            the field T-C's human audit has been targeting,
                            via score_boxed's equivalent logic)
Categories, exactly as specified, 2 cases each (should-credit /
should-NOT-credit), pre-declared before running -- not tuned for effect:
formatting, latex, whitespace, delimiters, answer_position, verbosity,
multiple_answers, self_correction, numerical_formatting, case, units,
other_scorer_specific.

PART B -- the real-data grounding check that MOTIVATED this taxonomy
(found while designing the self_correction/answer_position cases): does
exact_match and exact_match_original actually disagree on REAL model
responses, at what rate, in which direction, and does it vary by model?
Already run once ad hoc during investigation; reproduced here as a real,
committed, re-runnable step. Network + HF token required (already
authenticated).

Run: python scripts/fb_adversarial_suite_v2.py
"""
import importlib.util
import json
import sys
import types
import urllib.request

sys.path.insert(0, "scripts")
from huggingface_hub import get_token
import truststore
truststore.inject_into_ssl()

if "datasets" not in sys.modules:
    _stub = types.ModuleType("datasets")
    _stub.Dataset = object
    sys.modules["datasets"] = _stub

_spec = importlib.util.spec_from_file_location("leaderboard_math_utils", "vendor/leaderboard_math/utils.py")
mathutils = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mathutils)

from ea_dominance_study import load, build_model_table

# ---------------------------------------------------------------------------
# PART A: 12-category taxonomy, constructed cases, known ground truth.
# Each case: (category, tag, response_text, gold_boxed_in_solution, expect_credit)
# response_text is what the MODEL supposedly generated (raw, unextracted).
# gold is written as it would appear in the real MATH solution field
# (must itself contain \boxed{...} -- process_results extracts gold FROM
# doc["solution"], matching the real pipeline exactly, not a shortcut).
# ---------------------------------------------------------------------------
CASES = [
    # -- formatting: equivalent LaTeX macro variants --
    ("formatting", "dfrac_vs_frac_credit", r"The answer is \boxed{\dfrac{1}{2}}.",
     r"\boxed{\frac{1}{2}}", True),
    ("formatting", "different_value_no_credit", r"The answer is \boxed{\dfrac{1}{3}}.",
     r"\boxed{\frac{1}{2}}", False),

    # -- latex: sign placement / macro equivalence --
    ("latex", "sign_placement_credit", r"So the result is \boxed{\frac{-1}{2}}.",
     r"\boxed{-\frac{1}{2}}", True),
    ("latex", "genuinely_wrong_sign_no_credit", r"So the result is \boxed{\frac{1}{2}}.",
     r"\boxed{-\frac{1}{2}}", False),

    # -- whitespace: extra/irregular spacing around an equivalent expression --
    ("whitespace", "extra_spacing_credit", "Final Answer:  \\boxed{  5x + 2y  }  \n\n",
     r"\boxed{5x+2y}", True),
    ("whitespace", "spacing_cannot_rescue_wrong_value", "Final Answer:  \\boxed{  6x + 2y  }  \n\n",
     r"\boxed{5x+2y}", False),

    # -- delimiters: bare vs $-wrapped vs \[ \]-wrapped identical value --
    ("delimiters", "dollar_wrapped_credit", r"The answer is \boxed{$7$}.",
     r"\boxed{7}", True),
    ("delimiters", "bracket_wrapped_credit", r"The answer is \boxed{\[7\]}.",
     r"\boxed{7}", True),

    # -- answer_position: correct final answer stated in PROSE, not boxed at all --
    ("answer_position", "unboxed_prose_final_answer",
     "We simplify step by step.\nFinal Answer: The final answer is $2015$. I hope it is correct.\n",
     r"\boxed{2015}", True),
    ("answer_position", "unboxed_prose_wrong_answer_no_credit",
     "We simplify step by step.\nFinal Answer: The final answer is $2016$. I hope it is correct.\n",
     r"\boxed{2015}", False),

    # -- verbosity: long irrelevant preamble before a correct boxed answer --
    ("verbosity", "long_preamble_credit",
     ("Let me think about this very carefully, considering several possible approaches "
      "before committing to one. " * 8) + r"\boxed{42}",
     r"\boxed{42}", True),
    ("verbosity", "terse_correct_credit", r"\boxed{42}", r"\boxed{42}", True),

    # -- multiple_answers: two candidate boxed values, real self-correction sequence --
    ("multiple_answers", "two_boxed_last_is_correct",
     r"First I get \boxed{2012401}, but checking again, \boxed{2012402}.",
     r"\boxed{2012402}", True),
    ("multiple_answers", "two_boxed_last_is_WRONG_true_answer_in_prose",
     (r"First I get \boxed{2012401}, but checking again, \boxed{2012402}. "
      "Actually wait, let me redo this. Final Answer: The final answer is $2015$. I hope it is correct."),
     r"\boxed{2015}", True),  # true answer is 2015, stated last in PROSE after two wrong boxed guesses

    # -- self_correction: model reverses itself mid-response, correct answer LAST --
    ("self_correction", "explicit_correction_final_right",
     r"The answer is \boxed{10}. Wait, that's wrong. The correct answer is \boxed{15}.",
     r"\boxed{15}", True),
    ("self_correction", "explicit_correction_final_still_wrong",
     r"The answer is \boxed{10}. Wait, that's wrong. The correct answer is \boxed{15}.",
     r"\boxed{20}", False),

    # -- numerical_formatting: decimal vs fraction, trailing zeros --
    ("numerical_formatting", "decimal_vs_fraction_credit", r"\boxed{0.5}", r"\boxed{\frac{1}{2}}", True),
    ("numerical_formatting", "trailing_zero_credit", r"\boxed{4.0}", r"\boxed{4}", True),

    # -- case: upper/lower-case variable or word-answer, where case is semantically irrelevant --
    ("case", "lowercase_word_answer_credit", r"\boxed{\text{even}}", r"\boxed{\text{EVEN}}", True),
    ("case", "case_cannot_rescue_wrong_word", r"\boxed{\text{odd}}", r"\boxed{\text{EVEN}}", False),

    # -- units: appended unit text on an otherwise-correct numeric answer --
    ("units", "unit_suffix_null_case", r"\boxed{9 \text{ meters}}", r"\boxed{9}", None),
    ("units", "unit_mismatch_should_not_equate", r"\boxed{9 \text{ meters}}", r"\boxed{9 \text{ seconds}}", False),

    # -- other_scorer_specific: interval/set union order (known structural limitation) --
    ("other_scorer_specific", "interval_union_reordered",
     r"\boxed{(-\infty, -7) \cup (-7, 3) \cup (3, \infty)}",
     r"\boxed{(-\infty, 3) \cup (3, -7) \cup (-7, \infty)}", True),
    ("other_scorer_specific", "no_commit_never_credited", r"I am not sure.", r"\boxed{4}", False),
]


def _exact_match_no_mp_timeout(doc, candidates):
    """Same logic as process_results()'s exact_match path (math_verify
    parse/verify), but with timeout_seconds=None -- math_verify's default
    5s timeout uses multiprocessing.spawn, which crashes when called
    repeatedly from a dynamically-loaded module under this environment's
    Windows Python (a second, distinct Windows-specific timeout-mechanism
    fragility, analogous to is_equiv's SIGALRM issue, MATH_COMPARATOR_BUG.md).
    Disabling the timeout is safe here: every case is a short constructed
    string, not a pathological input that could hang."""
    from math_verify import LatexExtractionConfig, parse, verify
    parsed_candidate = parse(candidates, parsing_timeout=None)
    parsed_answer = parse(doc["solution"], extraction_config=[LatexExtractionConfig()], parsing_timeout=None)
    return bool(verify(parsed_answer, parsed_candidate, timeout_seconds=None))


def _score_boxed(response, gold_solution):
    """T-C's ACTUAL audited comparator (fb_pull_roster.py imports this exact
    logic from knowledgeshift/scripts/19_l1_rescore_leaderboard.py's
    score_boxed) -- last_boxed_only_string extraction, NOT the
    'Final Answer: ... I hope it is correct.' regex that
    get_unnormalized_answer/process_result_v1/exact_match_original actually
    uses (confirmed by reading both functions directly -- these are TWO
    DIFFERENT extraction strategies in this codebase, easy to conflate,
    and conflating them was an earlier bug in this same script, caught
    before being reported)."""
    from fb_math_comparator_fixed import is_equiv_fixed
    boxed = mathutils.last_boxed_only_string(response)
    if not boxed or boxed == mathutils.INVALID_ANSWER:
        return False  # unparsed -> not credited
    try:
        answer = mathutils.normalize_final_answer(mathutils.remove_boxed(boxed))
    except (AssertionError, IndexError, ValueError):
        return False
    gold_extracted = mathutils.remove_boxed(mathutils.last_boxed_only_string(gold_solution))
    normalized_gold = mathutils.normalize_final_answer(gold_extracted)
    return answer.strip() == normalized_gold.strip() or is_equiv_fixed(answer, normalized_gold)


def run_case(category, tag, response, gold_solution, expect):
    doc = {"solution": gold_solution}
    try:
        em = _exact_match_no_mp_timeout(doc, response)
        emo = _score_boxed(response, gold_solution)
        error = None
    except Exception as e:
        em, emo, error = None, None, str(e)
    return {"category": category, "tag": tag, "response": response, "gold_solution": gold_solution,
            "expect_credit": expect, "exact_match": em, "exact_match_original": emo, "error": error}


def classify(expect, actual):
    if expect is None or actual is None:
        return "null_or_error"
    if actual == expect:
        return "correct"
    if actual and not expect:
        return "false_credit"
    return "false_miss"


def part_a():
    print("=" * 78)
    print("PART A -- 12-category constructed-case taxonomy (both real scorers)")
    print("=" * 78)
    results = [run_case(*c) for c in CASES]
    by_category = {}
    for r in results:
        cat = r["category"]
        by_category.setdefault(cat, []).append(r)
        r["exact_match_classification"] = classify(r["expect_credit"], r["exact_match"])
        r["exact_match_original_classification"] = classify(r["expect_credit"], r["exact_match_original"])
        print(f"  [{r['tag']:<45}] expect={r['expect_credit']!s:<5} "
              f"exact_match={r['exact_match']!s:<5}({r['exact_match_classification']:<11}) "
              f"exact_match_original={r['exact_match_original']!s:<5}({r['exact_match_original_classification']})")

    print()
    print("-" * 78)
    print("PER-CATEGORY SUMMARY -- false_credit / false_miss counts, per scorer,")
    print("plus whether the effect is scorer-specific or general (both scorers agree/disagree)")
    print("-" * 78)
    category_summary = {}
    for cat, rs in by_category.items():
        em_fc = sum(1 for r in rs if r["exact_match_classification"] == "false_credit")
        em_fm = sum(1 for r in rs if r["exact_match_classification"] == "false_miss")
        emo_fc = sum(1 for r in rs if r["exact_match_original_classification"] == "false_credit")
        emo_fm = sum(1 for r in rs if r["exact_match_original_classification"] == "false_miss")
        n_scorer_disagree = sum(1 for r in rs if r["exact_match"] != r["exact_match_original"]
                                 and r["exact_match"] is not None and r["exact_match_original"] is not None)
        general = (em_fc + em_fm) > 0 and (emo_fc + emo_fm) > 0
        scorer_specific = ((em_fc + em_fm) > 0) != ((emo_fc + emo_fm) > 0)
        category_summary[cat] = {
            "n_cases": len(rs),
            "exact_match_false_credit": em_fc, "exact_match_false_miss": em_fm,
            "exact_match_original_false_credit": emo_fc, "exact_match_original_false_miss": emo_fm,
            "n_the_two_real_scorers_disagree_on_this_category": n_scorer_disagree,
            "effect_is_general_across_both_scorers": general,
            "effect_is_scorer_specific": scorer_specific,
            "null_result": (em_fc + em_fm + emo_fc + emo_fm) == 0,
        }
        print(f"  {cat:<24} n={len(rs)}  exact_match(fc={em_fc},fm={em_fm})  "
              f"exact_match_original(fc={emo_fc},fm={emo_fm})  "
              f"scorers_disagree_on={n_scorer_disagree}  "
              f"[{'NULL' if category_summary[cat]['null_result'] else ('SCORER-SPECIFIC' if scorer_specific else 'GENERAL' if general else 'PARTIAL')}]")

    return results, category_summary


def part_b():
    print()
    print("=" * 78)
    print("PART B -- real-data grounding: exact_match vs exact_match_original,")
    print("full qualifying roster, algebra_hard subject")
    print("=" * 78)
    token = get_token()
    if not token:
        print("NO HF TOKEN -- skipping Part B, Part A results still valid and written.")
        return None

    def score_boxed_equiv(math, response, gold):
        boxed = math.last_boxed_only_string(response)
        if not boxed or boxed == math.INVALID_ANSWER:
            return 0, False
        try:
            answer = math.normalize_final_answer(math.remove_boxed(boxed))
        except (AssertionError, IndexError, ValueError):
            return 0, False
        normalized_gold = math.normalize_final_answer(gold)
        return int(answer.strip() == normalized_gold.strip() or math.is_equiv(answer, normalized_gold)), True

    def fetch(model, fname):
        encoded = model.replace("/", "__")
        file_url = f"https://huggingface.co/datasets/open-llm-leaderboard/{encoded}-details/resolve/main/{fname}"
        req = urllib.request.Request(file_url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode("utf-8", errors="replace")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def latest_file(model, subject_substr):
        encoded = model.replace("/", "__")
        api_url = f"https://huggingface.co/api/datasets/open-llm-leaderboard/{encoded}-details"
        req = urllib.request.Request(api_url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            meta = json.load(resp)
        names = [s["rfilename"] for s in meta["siblings"]]
        cands = sorted(n for n in names if f"samples_leaderboard_math_{subject_substr}" in n)
        return cands[-1] if cands else None

    accs, margins = load()
    rows, excl = build_model_table(accs, margins)
    models = sorted(rows.keys())

    per_model = {}
    totals = {"n_total": 0, "n_match": 0, "n_unparsed_by_original": 0,
              "n_exactmatch1_original0": 0, "n_exactmatch0_original1": 0}
    for model in models:
        try:
            fname = latest_file(model, "algebra_hard")
            if not fname:
                continue
            recs = fetch(model, fname)
        except Exception as e:
            print(f"{model}: FETCH FAILED {e}")
            continue
        n_total, n_match, n_unparsed, a, b = 0, 0, 0, 0, 0
        for r in recs:
            gold = r["doc"].get("answer")
            resps = r.get("resps") or []
            if not resps or gold is None:
                continue
            t = resps[0][0] if isinstance(resps[0], list) else resps[0]
            if not isinstance(t, str):
                continue
            stored = r.get("exact_match")
            score, found = score_boxed_equiv(mathutils, t, gold)
            n_total += 1
            if not found:
                n_unparsed += 1
            if stored == score:
                n_match += 1
            elif stored == 1 and score == 0:
                a += 1
            elif stored == 0 and score == 1:
                b += 1
        if n_total == 0:
            continue
        per_model[model] = {"n": n_total, "agree_pct": 100 * n_match / n_total,
                             "unparsed_by_original_pct": 100 * n_unparsed / n_total,
                             "exactmatch1_original0": a, "exactmatch0_original1": b}
        totals["n_total"] += n_total
        totals["n_match"] += n_match
        totals["n_unparsed_by_original"] += n_unparsed
        totals["n_exactmatch1_original0"] += a
        totals["n_exactmatch0_original1"] += b
        print(f"  {model:<45} n={n_total:<5} agree={100*n_match/n_total:.1f}%  "
              f"unparsed_by_original={100*n_unparsed/n_total:.1f}%  em1/orig0={a}  em0/orig1={b}")

    print()
    print(f"AGGREGATE: n={totals['n_total']}  overall_agreement={100*totals['n_match']/totals['n_total']:.2f}%  "
          f"overall_disagreement={100*(1-totals['n_match']/totals['n_total']):.2f}%  "
          f"(vs. previously-reported pooled alpha ~3.1%)")
    return {"per_model": per_model, "totals": totals}


if __name__ == "__main__":
    part_a_results, part_a_summary = part_a()
    part_b_results = part_b()

    out = {
        "part_a_taxonomy_cases": part_a_results,
        "part_a_category_summary": part_a_summary,
        "part_b_real_data_grounding": part_b_results,
    }
    with open("results/flipbudget/adversarial_suite_v2.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/adversarial_suite_v2.json")
