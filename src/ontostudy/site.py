"""Collect the study's tables into one JSON file for the static site in docs/site/.

    python -m ontostudy.site            # writes docs/site/data.json

Reads docs/metrics-matrix.md (RQ1), docs/cases/ (RQ2), docs/results/*.csv and
src/ontostudy/queries/QUESTIONS.md (RQ3), and docs/guidelines.md. Nothing is typed in here by hand; if a
table changes, rerun this.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
OUT = DOCS / "site" / "data.json"


def md_tables(text: str) -> list[list[list[str]]]:
    """Every pipe table in a markdown string, as rows of cells (separator rows dropped)."""
    tables, cur = [], []
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            cur.append(cells)
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    return tables


def rq1() -> dict:
    header, *rows = md_tables((DOCS / "metrics-matrix.md").read_text())[0]
    return {
        "columns": [c.strip("*") for c in header[1:]],
        "rows": [{"framework": r[0], "cells": r[1:]} for r in rows],
    }


def rq2() -> dict:
    patterns_t, outcome_t = md_tables((DOCS / "cases" / "README.md").read_text())[:2]
    case_ids = patterns_t[0][1:]
    outcomes = dict(zip(case_ids, outcome_t[0][1:]))  # one-row table: the header carries the values
    matrix = {r[0]: [cid for cid, v in zip(case_ids, r[1:]) if v == "1"] for r in patterns_t[1:]}
    cases = []
    for cid in case_ids:
        path = next(p for p in sorted((DOCS / "cases").glob(f"{cid}*.md")))  # "amazon" -> amazon-product-graph.md
        text = path.read_text()
        fields = {r[0]: r[1] for r in md_tables(text)[0][1:]}
        cases.append({
            "id": cid,
            "name": re.match(r"# Case: (.+)", text).group(1),
            "organization": fields.get("Organization", ""),
            "domain": fields.get("Domain", ""),
            "period": fields.get("Period", ""),
            "grade": fields.get("Source grade", ""),
            "outcome": outcomes[cid],
            "patterns": [p for p, cs in matrix.items() if cid in cs],
        })
    return {"cases": cases, "patterns": list(matrix), "matrix": matrix}


def load_run(name: str) -> dict | None:
    """One benchmark run (bench*.csv + sizes*.csv) as plain rows; None if absent."""
    path = DOCS / "results" / name
    if not path.exists():
        return None
    with open(path) as f:
        bench = [
            {"scale": int(r["scale"]), "schema": r["schema"], "query": r["query"],
             **({"hops": int(r["hops"]), "prop_reads": int(r["prop_reads"])} if "hops" in r else {}),
             "ms": round(float(r["seconds"]) * 1000, 4), "correct": r["correct"] == "True",
             **({"runs_ms": [round(float(x) * 1000, 4) for x in r["runs"].split(";")]} if r.get("runs") else {})}
            for r in csv.DictReader(f)
        ]
    sizes_path = DOCS / "results" / name.replace("bench", "sizes")
    sizes = []
    if sizes_path.exists():
        with open(sizes_path) as f:
            sizes = [{k: (float(v) if k in ("build_seconds", "mbytes") else int(v) if k in ("scale", "nodes", "edges") else v) for k, v in r.items()}
                     for r in csv.DictReader(f)]
    return {
        "scales": sorted({b["scale"] for b in bench}),
        "schemas": list(dict.fromkeys(b["schema"] for b in bench)),
        "bench": bench,
        "sizes": sizes,
    }


def rq3() -> dict:
    questions = [
        {"id": r[0], "question": r[1], "kind": r[2]}
        for r in md_tables((ROOT / "src/ontostudy/queries/QUESTIONS.md").read_text())[0][1:]
    ]
    main = load_run("bench.csv")
    followups = {k: v for k, v in ((tag, load_run(name)) for tag, name in
                 (("indexed", "bench_indexed.csv"), ("skew", "bench_skew.csv"), ("kuzu", "bench_kuzu.csv"))) if v}
    writes_path = DOCS / "results" / "writes.csv"
    writes = []
    if writes_path.exists():
        with open(writes_path) as f:
            writes = [{"scale": int(r["scale"]), "schema": r["schema"], "update": r["update"],
                       "records": int(r["records"]), "us": round(float(r["seconds"]) * 1e6, 2)} for r in csv.DictReader(f)]
    results = (DOCS / "results" / "RESULTS.md").read_text()
    hyp_table = next(t for t in md_tables(results) if t[0][:1] == [""] and t[1][0].startswith("H"))
    hypotheses = []
    for hid, statement, verdict in hyp_table[1:]:
        m = re.match(r"\*\*(.+?)\*\*:?\s*(.*)", verdict)
        hypotheses.append({"id": hid, "statement": statement, "verdict": m.group(1), "note": m.group(2)})
    run = re.search(r"[Rr]un on (\d{4}-\d{2}-\d{2})", results).group(1)
    return {
        "run_date": run,
        "scales": main["scales"],
        "schemas": main["schemas"],
        "queries": questions,
        "bench": main["bench"],
        "sizes": main["sizes"],
        "hypotheses": hypotheses,
        "followups": followups,
        "writes": writes,
    }


def guidelines() -> list[dict]:
    rows = md_tables((DOCS / "guidelines.md").read_text())[0][1:]
    return [{"id": r[0], "guideline": r[1], "evidence": r[2], "strength": r[3]} for r in rows]


def build() -> dict:
    return {"rq1": rq1(), "rq2": rq2(), "rq3": rq3(), "guidelines": guidelines()}


if __name__ == "__main__":
    data = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(data['rq1']['rows'])} frameworks, "
          f"{len(data['rq2']['cases'])} cases, {len(data['rq3']['bench'])} bench rows")
