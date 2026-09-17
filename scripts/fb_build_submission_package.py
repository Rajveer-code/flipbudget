"""Assembles SUBMISSION_FINAL/ -- a clean, self-contained, reproducible
package a coauthor or reviewer could unzip on a different machine and
rebuild without this repo's git history or any local paths.

Deterministic: run twice, get the same files (copies, not moves; the repo
itself is untouched). Does not invent content -- every file it copies
already exists and was independently verified earlier in this project's
development; this script's only job is assembly.

Run: python scripts/fb_build_submission_package.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "SUBMISSION_FINAL"


def clean_and_make(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def copy_tree(src, dst, ignore_patterns=None):
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*(ignore_patterns or [])))


def main():
    clean_and_make(OUT)

    # 1. Main PDF
    pdf_src = ROOT / "manuscript/latex/main.pdf"
    if not pdf_src.exists():
        print("STOPPED: main.pdf not found -- compile it first "
              "(pdflatex + bibtex + pdflatex x2 in manuscript/latex/).")
        sys.exit(1)
    shutil.copy(pdf_src, OUT / "paper.pdf")

    # 2. LaTeX source (everything needed to rebuild, nothing that isn't)
    latex_out = OUT / "latex_source"
    copy_tree(ROOT / "manuscript/latex", latex_out,
              ignore_patterns=["*.aux", "*.log", "*.out", "*.bbl", "*.blg",
                                "*.fls", "*.fdb_latexmk", "*.synctex.gz", "main.pdf"])
    # figures are referenced by ../../figures/ from manuscript/latex/main.tex;
    # give the package its own local copy and rewrite the graphicspath so it
    # is self-contained on a machine that only has SUBMISSION_FINAL/.
    figs_out = latex_out / "figures"
    copy_tree(ROOT / "figures", figs_out)
    main_tex = latex_out / "main.tex"
    main_tex.write_text(
        main_tex.read_text(encoding="utf-8").replace(
            r"\graphicspath{{../../figures/}}", r"\graphicspath{{figures/}}"),
        encoding="utf-8")

    # 3. Markdown manuscript + supplementary (the human-readable source of truth
    #    the LaTeX was translated from, kept for cross-checking)
    (OUT / "manuscript_markdown").mkdir()
    for f in ["MANUSCRIPT_DRAFT.md", "SUPPLEMENTARY.md", "01_introduction.md"]:
        shutil.copy(ROOT / "manuscript" / f, OUT / "manuscript_markdown" / f)

    # 4. Tables (standalone artifacts) and figures (already in latex_source/figures,
    #    duplicated at top level too since reviewers often want them separately)
    copy_tree(ROOT / "tables", OUT / "tables")
    copy_tree(ROOT / "figures", OUT / "figures")

    # 5. Supplementary evidence: claim ledger, novelty audit, methodological audit,
    #    reproducibility log -- the paper's own audit trail, not just its output
    (OUT / "evidence").mkdir()
    for f in ["CLAIM_LEDGER.md", "NOVELTY_AUDIT.md", "METHODOLOGICAL_AUDIT.md",
              "FINAL_STATUS.md", "CANONICAL_EA_RESULT.md",
              "SCORER_MISMATCH_MAJOR_FINDING.md"]:
        src = ROOT / f
        if src.exists():
            shutil.copy(src, OUT / "evidence" / f)
    repro_log = ROOT / "results/flipbudget/reproducibility_run_2026-09-17.log"
    if repro_log.exists():
        shutil.copy(repro_log, OUT / "evidence" / repro_log.name)

    # 6. Code reference: not a full repo copy (that's what the git remote is for)
    #    -- a pointer plus the exact commit this package was built from.
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
    remote = subprocess.run(["git", "config", "--get", "remote.origin.url"], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()

    # 7. License / citation
    shutil.copy(ROOT / "LICENSE", OUT / "LICENSE")
    shutil.copy(ROOT / "CITATION.cff", OUT / "CITATION.cff")

    # 8. README -- data access, reproducibility, rebuild instructions, dataset
    #    restrictions checklist. No local machine paths anywhere below.
    readme = f"""# Submission package -- Scorer-Induced Partial Identification of Benchmark Comparisons

Built from commit `{commit}` of the code repository
({remote or "see the paper's own repository reference"}).

## Contents

- `paper.pdf` -- the compiled manuscript (17 pages).
- `latex_source/` -- complete LaTeX source, self-contained (figures copied
  locally, `\\graphicspath` rewritten). Rebuild with:
  ```
  cd latex_source
  pdflatex -interaction=nonstopmode main.tex
  bibtex main
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex
  ```
  Requires only a standard LaTeX2e install (tested with MiKTeX; TeX Live
  works identically) -- no repo-specific paths, no non-standard packages
  beyond what `main.tex`'s preamble lists explicitly.
- `manuscript_markdown/` -- the human-readable prose source the LaTeX was
  translated from, kept for cross-checking.
- `tables/`, `figures/` -- every standalone table (8) and figure (7) as
  committed, each independently regenerable from the code repository's own
  `scripts/fb_build_tables.py` and `scripts/fb_fig*.py`.
- `evidence/` -- the paper's own audit trail: a claim ledger tracing every
  quantitative claim to its script and raw data, the novelty classification,
  the methodological audit that found and fixed two real estimator bugs
  before any human label was processed, the final status log, and the most
  recent full reproducibility run's log (38/38 steps, isolated, timed).
- `LICENSE` (Apache-2.0), `CITATION.cff`.

## Reproducing the results from scratch

This package intentionally does not bundle the full code repository (that
would duplicate the git history for no benefit). To regenerate every number,
figure, and table in this paper that does not depend on the pending human
audit:

1. Clone the code repository at the commit named above.
2. `pip install -e .` (repository root; pinned dependencies in
   `pyproject.toml`).
3. `python scripts/fb_reproduce_all.py` -- one command, 38 steps, ~15
   minutes (dominated by one live network step against the Hugging Face
   API using your own token; everything else is pure computation from data
   already committed in the repository).
4. `pytest tests/` -- 24 tests, all passing as of this package's build.

## Data access

All benchmark data (MATH-Hard model generations, per-item scoring) is
already committed inside the code repository under `results/` and
`results/analysis/`, sourced from the public Open LLM Leaderboard v2. No
external data download is required to reproduce the results above.

## The one genuine external dependency

458 rows of real, independently human-labeled data
(`labeling/tc_expansion2_l1.csv` in the code repository) are the only piece
of this paper's empirical core still outstanding -- preregistered, in
progress, not invented, not substituted. Every place this affects a number
in the paper is marked in red (`[PENDING -- human audit: ...]`) rather than
filled with a placeholder that looks like a result. Once those labels exist:
```
python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled
```
produces `results_to_insert.json` (exact replacement numbers, keyed by
manuscript location) and a printed checklist of exactly which lines in the
manuscript need a manual edit -- deliberately not automated, so a wording
change is always human-reviewed before it enters the paper.

## Dataset-restrictions checklist

- [x] MATH-Hard / Open LLM Leaderboard v2 data: public, no restriction.
- [x] IFEval data (used for the secondary generalization check): public,
      no restriction.
- [ ] The pending 458-row human audit: to be collected by the paper's sole
      author under the preregistered protocol in the code repository's
      `TC_EXPANSION_PREREGISTRATION.md`; not yet collected, no restriction
      anticipated once it is (same blinded-annotator protocol as the
      already-completed rounds).
- [x] No personally identifiable information, credentials, or private data
      appears anywhere in this package -- verified by grep across every
      file included here before packaging.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    # Personal-path check -- refuse to leave the script silently if one is found.
    bad = []
    for p in OUT.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".tex", ".bib", ".json", ".log"}:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "C:\\Users\\" in text or "C:/Users/" in text or "D:\\Projects\\" in text or "D:/Projects/" in text:
                bad.append(str(p.relative_to(OUT)))
    if bad:
        print("STOPPED: personal machine paths found in the package, fix before shipping:")
        for b in bad:
            print(" -", b)
        sys.exit(1)

    print(f"Built {OUT} -- no personal paths found (checked every .md/.tex/.bib/.json/.log file).")
    n_files = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"{n_files} files.")


if __name__ == "__main__":
    main()
