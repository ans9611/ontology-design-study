"""Systematic literature search against OpenAlex.

Runs the protocol's search strings, appends a dated row to the search log,
and writes the candidate list (title, year, venue, DOI, citations, abstract)
for title/abstract screening.

    python -m ontostudy.slr                # all strings, defaults
    python -m ontostudy.slr --string S1 --per-string 300

OpenAlex covers ACM, IEEE, Springer and Elsevier metadata, so hit counts are
comparable to, though not identical with, the publisher databases. Record
that in the protocol.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import sys
import time
import urllib.parse
import urllib.request
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOG = ROOT / "docs" / "search-log.csv"
OUT = ROOT / "docs" / "slr"
MAILTO = "moonye1006@gmail.com"  # polite pool; faster rate limit

# The protocol's strings. OpenAlex `search` is full-text over title/abstract/fulltext
# with its own boolean syntax, so the strings are kept close to protocol.md.
STRINGS = {
    "S1": '(ontology OR "knowledge graph") AND ("quality metric" OR "quality evaluation" OR "ontology evaluation" OR "quality assessment")',
    "S2": '("ontology engineering" OR "knowledge graph construction" OR "enterprise knowledge graph") AND (industry OR enterprise OR "lessons learned")',
    "S3": '("graph database" OR "graph query" OR SPARQL OR Cypher) AND ("query complexity" OR "schema design" OR "data model" OR normalization)',
}
# title_and_abstract search (not full text) and computer-science field only; sorted by relevance
FILTERS = "publication_year:>1992,type:article|book-chapter|proceedings-article,primary_topic.field.id:fields/17"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": f"ontostudy/0.1 (mailto:{MAILTO})"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def _abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def search(sid: str, per_string: int) -> tuple[int, list[dict]]:
    q = urllib.parse.quote(STRINGS[sid])
    rows, cursor, total = [], "*", None
    while len(rows) < per_string:
        url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{q},{FILTERS}"
               f"&sort=relevance_score:desc&per-page=200&cursor={cursor}&mailto={MAILTO}")
        d = _get(url)
        total = d["meta"]["count"]
        for w in d["results"]:
            src = (w.get("primary_location") or {}).get("source") or {}
            rows.append({
                "string": sid,
                "openalex_id": w["id"].rsplit("/", 1)[-1],
                "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                "year": w.get("publication_year"),
                "title": w.get("title") or "",
                "venue": src.get("display_name") or "",
                "type": w.get("type"),
                "cited_by": w.get("cited_by_count"),
                "relevance": round(w.get("relevance_score") or 0, 2),
                "abstract": _abstract(w.get("abstract_inverted_index")),
                "title_screen": "",
                "abstract_screen": "",
                "grade": "",
                "note": "",
            })
        cursor = d["meta"].get("next_cursor")
        if not cursor or not d["results"]:
            break
        time.sleep(0.2)
    return total, rows[:per_string]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--string", choices=list(STRINGS), action="append")
    p.add_argument("--per-string", type=int, default=200, help="candidates kept per string, by citation count")
    a = p.parse_args(argv)
    sids = a.string or list(STRINGS)

    OUT.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    new_log = not LOG.exists()
    with LOG.open("a", newline="") as f:
        w = csv.writer(f)
        if new_log:
            w.writerow(["date", "database", "string_id", "string", "hits", "candidates_kept"])
        for sid in sids:
            total, rows = search(sid, a.per_string)
            path = OUT / f"{today}_{sid}.csv"
            with path.open("w", newline="") as g:
                cw = csv.DictWriter(g, fieldnames=list(rows[0].keys()))
                cw.writeheader()
                cw.writerows(rows)
            w.writerow([today, "OpenAlex", sid, STRINGS[sid], total, len(rows)])
            print(f"{sid}: {total} hits, kept {len(rows)} -> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
