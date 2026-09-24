"""Remove `note = {...}` fields from the manuscript's bibliography.

The bibliography was carried over from an earlier paper, and its note fields annotate entries
with cross-references to that paper's section labels and with counts from that paper's
corpus ("28-model", "14-model roster"). Both are wrong here: the labels do not exist, which
breaks the build, and the counts contradict this paper's data. The notes are annotations, not
bibliographic data, so they are removed rather than rewritten.

Run: python scripts/fb_strip_bib_notes.py manuscript/tmlr/references.bib
"""
import re
import sys
from pathlib import Path


def strip_notes(text: str) -> tuple[str, int]:
    out, i, removed = [], 0, 0
    pattern = re.compile(r"\n\s*note\s*=\s*\{", re.I)
    while True:
        m = pattern.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        depth, j = 1, m.end()
        while j < len(text) and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        while j < len(text) and text[j] in ", \t":  # trailing comma of the removed field
            j += 1
        if j < len(text) and text[j] == "\n":
            j += 1
        i = j
        removed += 1
    return "".join(out), removed


def main():
    p = Path(sys.argv[1])
    text = p.read_text(encoding="utf-8")
    new, n = strip_notes(text)
    assert new.count("@") == text.count("@"), "entry count changed"
    assert "\\ref{" not in new, "a cross-reference survived outside a note field"
    p.write_text(new, encoding="utf-8")
    print(f"removed {n} note field(s); {new.count('@')} entries intact")


if __name__ == "__main__":
    main()
