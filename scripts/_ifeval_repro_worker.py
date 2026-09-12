"""Internal worker: one independent, fresh-process pass over every cached
flagged-item row, calling the real IFEval verifier once per row. Invoked as a
subprocess (never imported) so each call is a genuinely fresh Python process --
no shared random-module state with any other replicate, matching how the real
harness is invoked once per independent evaluation run.

argv: <rowcache.json> <output.json> [seed_int]
  no seed arg  -> unseeded (real harness default: DetectorFactory.seed=None,
                  random module never seeded) -- the condition that actually
                  ships.
  seed given   -> control condition: random.seed(seed) (fixes
                  keywords:letter_frequency's random.choice/randint fallback)
                  AND langdetect.detector_factory.DetectorFactory.seed = seed
                  (fixes the langdetect-internal Detector's own Random
                  instance, confirmed from detector.py: self.random.seed(self.seed)).
"""
import json
import logging
import platform
import random
import sys

logging.disable(logging.ERROR)  # silence the harness's own "unable to detect
                                 # language" logger.error() noise on garbage
                                 # responses -- expected, not a real error

sys.path.insert(0, "scripts")
from fb_eb_ifeval_pull import load_ifeval_verifier

if __name__ == "__main__":
    cache_path, out_path = sys.argv[1], sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else None

    env = {"python_version": platform.python_version(), "seed_applied": seed}
    if seed is not None:
        random.seed(seed)
        import langdetect.detector_factory as ldf
        ldf.DetectorFactory.seed = seed
    else:
        import langdetect.detector_factory as ldf
        env["DetectorFactory_seed_default"] = ldf.DetectorFactory.seed  # should be None

    process_results = load_ifeval_verifier()

    with open(cache_path, encoding="utf-8") as f:
        cache = json.load(f)["rows"]

    out_rows = []
    for row in cache:
        out = process_results(row["doc"], [row["response"]])
        out_rows.append({
            "model": row["model"], "key": row["key"],
            "strict": bool(out["prompt_level_strict_acc"]),
            "loose": bool(out["prompt_level_loose_acc"]),
        })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"env": env, "rows": out_rows}, f)
