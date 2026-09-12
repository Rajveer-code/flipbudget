"""E-B, first scale-out benchmark: IFEval. Pulls per-model raw generations +
real verifier scores for the same 27-model roster used throughout this project.

WHY IFEval, not GPQA (the earlier recommendation): checked the actual task
configs before building anything. GPQA/MMLU-PRO/MuSR are all
`output_type: multiple_choice` -- loglikelihood-scored, no free-text generation,
no parsing/extraction step at all, so no analogous scorer-error mechanism can
exist there. IFEval is `output_type: generate_until` -- the model free-text
generates, and a PROGRAMMATIC VERIFIER checks compliance -- with the harness's
OWN "strict" vs "loose" scoring variants already acknowledging the verifier
itself is ambiguous (loose tries 8 response-formatting variants before
crediting compliance). Wherever strict != loose for the SAME response, that is
a direct, human-label-free proxy for scorer/verifier ambiguity -- this
project's exact object of study, without needing new labels to detect it.

BLOCKED: `open-llm-leaderboard/<model>-details` on HuggingFace is a GATED
dataset (confirmed via huggingface_hub.hf_hub_download -> GatedRepoError, not
merely a missing HF_TOKEN). Needs an authenticated, access-granted account.
This script is written and the scorer-reuse path independently verified
(see the stub-loading block below, confirmed working against the real 25-entry
instruction registry on a synthetic compliant/non-compliant pair) so it is
ready to run the moment access exists -- set HF_TOKEN and run.

Run: python scripts/fb_eb_ifeval_pull.py
"""
import json
import os
import re
import sys
import types
from pathlib import Path

import truststore
truststore.inject_into_ssl()  # local Windows CA-cert workaround, same fix already
                               # needed for every other HF Hub call this session

KNOWLEDGESHIFT_ROOT = Path(r"D:\Projects\knowledgeshift")
VENDOR_ROOT = KNOWLEDGESHIFT_ROOT / "vendor" / "lm-evaluation-harness"


def load_ifeval_verifier():
    """Load the real IFEval scorer without triggering the full harness's heavy
    dependency chain (TaskManager -> ... -> sacrebleu), which is irrelevant to
    reusing two leaf scoring files. Verified working: 25-entry instruction
    registry, correctly distinguishes a synthetic compliant/non-compliant pair.
    Needs `pip install langdetect immutabledict nltk` (real runtime deps of the
    verifier itself, not artifacts of this loading trick -- installed and
    confirmed during this session)."""
    vendor_str = str(VENDOR_ROOT)
    if vendor_str not in sys.path:
        sys.path.insert(0, vendor_str)

    def stub_package(name, subpath):
        if name in sys.modules:
            return
        m = types.ModuleType(name)
        m.__path__ = [str(VENDOR_ROOT / subpath)]
        sys.modules[name] = m

    stub_package("lm_eval", "lm_eval")
    stub_package("lm_eval.tasks", "lm_eval/tasks")
    stub_package("lm_eval.tasks.ifeval", "lm_eval/tasks/ifeval")
    stub_package("lm_eval.tasks.leaderboard", "lm_eval/tasks/leaderboard")
    stub_package("lm_eval.tasks.leaderboard.ifeval", "lm_eval/tasks/leaderboard/ifeval")

    from lm_eval.tasks.leaderboard.ifeval.utils import process_results
    return process_results


def decode_model_name(dirname_or_repo: str) -> str:
    name = dirname_or_repo
    if name.startswith("open-llm-leaderboard_"):
        name = name[len("open-llm-leaderboard_"):]
    if name.endswith("-details"):
        name = name[: -len("-details")]
    return name.replace("__", "/", 1)


def load_roster_models():
    with open("results/flipbudget/e4_mathhard_per_model.json", encoding="utf-8") as f:
        return sorted(json.load(f)["per_model"].keys())


def fetch_model_ifeval(model: str, token: str):
    """One model's latest IFEval sample file. Requires network + an
    authenticated, access-granted HF token (see module docstring -- currently
    blocked, gated repo, not a missing-token issue)."""
    import urllib.request
    encoded = model.replace("/", "__")
    api_url = f"https://huggingface.co/api/datasets/open-llm-leaderboard/{encoded}-details"
    req = urllib.request.Request(api_url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        meta = json.load(resp)
    names = [s["rfilename"] for s in meta["siblings"]]
    ifeval_files = [n for n in names if "/samples_leaderboard_ifeval" in n]
    if not ifeval_files:
        return None
    latest = sorted(ifeval_files)[-1]  # timestamp sorts lexicographically
    file_url = (f"https://huggingface.co/datasets/open-llm-leaderboard/{encoded}-details"
                f"/resolve/main/{latest}")
    req = urllib.request.Request(file_url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def build_roster(models, token):
    process_results = load_ifeval_verifier()
    population = []
    n_fetch_failed = []
    for i, model in enumerate(models, 1):
        try:
            rows = fetch_model_ifeval(model, token)
        except Exception as e:
            n_fetch_failed.append({"model": model, "error": str(e)})
            print(f"  [{i}/{len(models)}] {model}: FETCH FAILED -- {e}")
            continue
        if rows is None:
            n_fetch_failed.append({"model": model, "error": "no ifeval file found"})
            continue
        for row in rows:
            doc = row.get("doc") or {}
            resps = row.get("resps") or row.get("filtered_resps") or []
            if not resps:
                continue
            response = resps[0][0] if isinstance(resps[0], list) else resps[0]
            if not isinstance(response, str):
                continue
            try:
                out = process_results(doc, [response])
            except Exception as e:
                continue  # a malformed doc/instruction id -- skip, don't fabricate a score
            population.append({
                "model": model, "key": doc.get("key"),
                "strict": bool(out["prompt_level_strict_acc"]),
                "loose": bool(out["prompt_level_loose_acc"]),
                "disagree": bool(out["prompt_level_strict_acc"]) != bool(out["prompt_level_loose_acc"]),
            })
        print(f"  [{i}/{len(models)}] {model}: {len(population)} rows so far")
    return population, n_fetch_failed


if __name__ == "__main__":
    print("=" * 70)
    print("E-B / IFEval: pull real per-model verifier scores (strict + loose)")
    print("=" * 70)
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit(
            "HF_TOKEN not set. Also note: open-llm-leaderboard/*-details is a GATED "
            "dataset (confirmed via GatedRepoError, not just a missing token) -- "
            "your HF account needs granted access before a token will work at all."
        )

    models = load_roster_models()
    print(f"Roster: {len(models)} models\n")
    population, failed = build_roster(models, token)

    print(f"\nTotal rows: {len(population)}, models failed: {len(failed)}")
    if population:
        n_disagree = sum(1 for r in population if r["disagree"])
        print(f"Strict/loose disagreement rate (human-label-free scorer-ambiguity "
              f"proxy): {n_disagree}/{len(population)} ({100*n_disagree/len(population):.1f}%)")

    out = {"n_models_attempted": len(models), "n_fetch_failed": len(failed),
           "fetch_failures": failed, "population": population}
    with open("results/analysis/ifeval_full_roster.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/analysis/ifeval_full_roster.json")
