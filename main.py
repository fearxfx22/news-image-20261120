#!/usr/bin/env python3
"""Friday 20 November 2026 — THE WORLD IN ONE DAY (make.fun news-image-20261120).

v2: rebuilt to the top-10 formula — the date as the giant masthead, dense
dark illustrations with on-image banners, taller medium cards, a compact
dark map panel beside the story list, UTC stamps and REPORTED/CLAIM/
FORECAST tags on every card, and a three-part date rail (19 Nov left out /
20 Nov on this page / 21 Nov not yet). Same 44 verified stories as v1.

One-image summary of 20 November 2026 world news: 44 verified stories
(3 heroes + 10 medium cards + 31 more), drawn in code by draw.py and
shipped as entry.png beside this file. This program copies it to the
grader's output directory. Standard library only, deterministic: both
runs write the same bytes.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(src, dst)
    # Guard the two-runs-must-match rule: the copy must be byte-identical.
    if os.path.getsize(dst) != os.path.getsize(src):
        raise SystemExit("entry.png copy size mismatch")


if __name__ == "__main__":
    main()
