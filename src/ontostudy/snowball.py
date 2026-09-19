"""Backward and forward snowballing from the included set, via OpenAlex.

For every paper with abstract_screen == include, fetch its reference list
(backward) and the works that cite it (forward). Works that are not already
in the candidate lists are ranked by how many included papers point at them
or are pointed at by them. Output: docs/slr/<date>_snowball.csv with the
same screening columns as the search lists.

    python -m ontostudy.snowball --min-links 2
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import json
import pathlib
import sys
import time
import urllib.request
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
SLR = ROOT / "docs" / "slr"
MAILTO = "moonye1006@gmail.com"
FIELDS = "id,doi,title,publication_year,type,cited_by_count,primary_location,abstract_inverted_index"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": f"ontostudy/0.1 (mailto:{MAILTO})"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 * (attempt + 1))
    return {}


def _abstract(inv):
    if not inv:
        return ""
    pos = {i: w for w, idxs in inv.items() for i in idxs}
    return " ".join(pos[i] for i in sorted(pos))


def included_ids() -> tuple[set[str], set[str]]:
    inc, seen = set(), set()
    for f in glob.glob(str(SLR / "*_S?.csv")):
        for r in csv.DictReader(open(f)):
            seen.add(r["openalex_id"])
            if r.get("abstract_screen") == "include":
                inc.add(r["openalex_id"])
    return inc, seen


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--min-links", type=int, default=2, help="keep works linked to at least this many included papers")
    p.add_argument("--max-forward", type=int, default=200, help="citing works fetched per included paper")
    a = p.parse_args(argv)

    inc, seen = included_ids()
    print(f"{len(inc)} included papers, {len(seen)} already screened")
    links: dict[str, set[str]] = defaultdict(set)   # candidate -> included papers linked to it
    direction: dict[str, Counter] = defaultdict(Counter)

    for n, wid in enumerate(sorted(inc), 1):
        w = _get(f"https://api.openalex.org/works/{wid}?select=id,referenced_works&mailto={MAILTO}")
        for ref in w.get("referenced_works", []):
            rid = ref.rsplit("/", 1)[-1]
            links[rid].add(wid); direction[rid]["backward"] += 1
        c = _get(f"https://api.openalex.org/works?filter=cites:{wid}&select=id&per-page={a.max_forward}&mailto={MAILTO}")
        for cw in c.get("results", []):
            cid = cw["id"].rsplit("/", 1)[-1]
            links[cid].add(wid); direction[cid]["forward"] += 1
        if n % 10 == 0:
            print(f"  {n}/{len(inc)} fetched, {len(links)} linked works so far")
        time.sleep(0.1)

    cands = [(cid, s) for cid, s in links.items() if cid not in seen and cid not in inc and len(s) >= a.min_links]
    cands.sort(key=lambda x: -len(x[1]))
    print(f"{len(cands)} new candidates with >= {a.min_links} links")

    rows = []
    for i in range(0, len(cands), 50):
        batch = cands[i:i + 50]
        ids = "|".join(c for c, _ in batch)
        d = _get(f"https://api.openalex.org/works?filter=openalex_id:{ids}&select={FIELDS}&per-page=50&mailto={MAILTO}")
        meta = {w["id"].rsplit("/", 1)[-1]: w for w in d.get("results", [])}
        for cid, s in batch:
            w = meta.get(cid, {})
            src = (w.get("primary_location") or {}).get("source") or {}
            rows.append({
                "string": "SB", "openalex_id": cid,
                "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                "year": w.get("publication_year"), "title": w.get("title") or "",
                "venue": src.get("display_name") or "", "type": w.get("type"),
                "cited_by": w.get("cited_by_count"), "relevance": len(s),
                "links_backward": direction[cid]["backward"], "links_forward": direction[cid]["forward"],
                "abstract": _abstract(w.get("abstract_inverted_index")),
                "title_screen": "", "abstract_screen": "", "grade": "", "note": "",
            })
    out = SLR / f"{dt.date.today().isoformat()}_snowball.csv"
    with out.open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    print(f"-> {out.relative_to(ROOT)}")
    for r in rows[:25]:
        print(f"  {r['relevance']:2d} links  {r['year']}  {r['title'][:85]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
