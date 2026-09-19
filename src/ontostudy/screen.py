"""Apply title-screening decisions to a candidate CSV.

    python -m ontostudy.screen docs/slr/2026-09-20_S1.csv --include 0 1 2 --maybe 14 --dup 27:19

Rows not listed are marked exclude. Decisions are recorded in the CSV's
`title_screen` and `note` columns so the screened file is the record.
"""

from __future__ import annotations

import argparse
import csv
import sys


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--include", type=int, nargs="*", default=[])
    p.add_argument("--maybe", type=int, nargs="*", default=[])
    p.add_argument("--dup", nargs="*", default=[], help="i:j  row i duplicates row j")
    p.add_argument("--note", nargs="*", default=[], help="i=text")
    p.add_argument("--stage", choices=["title", "abstract"], default="title",
                   help="abstract stage only touches rows that passed the title stage")
    a = p.parse_args(argv)
    col = f"{a.stage}_screen"

    rows = list(csv.DictReader(open(a.csv)))
    dups = {int(x.split(":")[0]): int(x.split(":")[1]) for x in a.dup}
    notes = {int(x.split("=", 1)[0]): x.split("=", 1)[1] for x in a.note}
    for i, r in enumerate(rows):
        if a.stage == "abstract" and r["title_screen"] not in ("include", "maybe"):
            continue
        if i in dups:
            r[col], r["note"] = "exclude", f"duplicate of row {dups[i]}"
        elif i in a.include:
            r[col] = "include"
        elif i in a.maybe:
            r[col] = "maybe"
        else:
            r[col] = "exclude"
        if i in notes:
            r["note"] = (r["note"] + "; " if r["note"] else "") + notes[i]
    with open(a.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    c = {k: sum(1 for r in rows if r[col] == k) for k in ("include", "maybe", "exclude")}
    print(a.csv, c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
