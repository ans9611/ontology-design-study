"""Collect the study's tables into one JSON file for the static site in docs/site/.

    python -m ontostudy.site            # writes docs/site/data.json

Reads docs/metrics-matrix.md (RQ1), docs/cases/ (RQ2), docs/results/*.csv and
src/ontostudy/queries/QUESTIONS.md (RQ3), docs/guidelines.md, and the reference list in README.md. Nothing is typed in here by hand; if a
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
    from .report import cost_model
    return {
        "run_date": run,
        "cost_model": cost_model(),
        "scales": main["scales"],
        "schemas": main["schemas"],
        "queries": questions,
        "bench": main["bench"],
        "sizes": main["sizes"],
        "hypotheses": hypotheses,
        "followups": followups,
        "writes": writes,
    }


SKIP_LABELS = {"likes", "liking", "liked", "replyOf", "reply", "parent"}   # kept out of the sample neighbourhood for size


def schema_graphs(n: int = 300) -> dict:
    """Each schema as a graph of types, plus one person's neighbourhood drawn in that schema.

    kind is "entity" for a node type mid also has, "relation" for a reified relation
    (normalized only); props lists the properties flat carries that mid stores as nodes.
    """
    from collections import Counter
    from .schemas import SCHEMAS
    from .synth import generate

    D = generate(n)
    graphs = {name: cls(D).G for name, cls in SCHEMAS.items()}
    mid_types = set(graphs["mid"].node_type.values())
    mid_props = {t: set(next(graphs["mid"].props[u] for u in graphs["mid"].nodes(t))) for t in mid_types}
    p0 = D.persons[0]
    friends = [v for u, v, _ in D.knows if u == p0["id"]][:2] + [u for u, v, _ in D.knows if v == p0["id"]][:2]
    post = next(m for m in D.posts if m["creator"] == p0["id"])
    country = next(c["countryId"] for c in D.cities if c["id"] == p0["cityId"])
    org = next(o for pp, o, _ in D.work if pp == p0["id"])
    friend_orgs = [next(o for pp, o, _ in D.work if pp == f) for f in friends[:2]]           # so a friend's employer's country is reachable (Q11)
    org_country = {o["id"]: o["countryId"] for o in D.orgs}
    sample_ids = [p0["id"], *friends[:2], p0["cityId"], country, org, *friend_orgs, *[org_country[o] for o in friend_orgs],
                  post["id"], *post["tags"][:2], post["forum"]]
    out = {}
    for name, G in graphs.items():
        counts = Counter(G.node_type.values())
        edges = Counter()
        for (u, label), lst in G.out.items():
            for v, _ in lst:
                edges[(G.node_type[u], label, G.node_type[v])] += 1
        types = []
        for t, c in counts.items():
            props = sorted(set(G.props[G.nodes(t)[0]]) - mid_props.get(t, set())) if t in mid_props else []
            types.append({"id": t, "count": c, "kind": "entity" if t in mid_types else "relation", "props": props})
        # sample neighbourhood: the same entities in every schema (ids are shared), so only the schema differs
        chosen = list(dict.fromkeys(sample_ids))
        present = [v for v in chosen if v in G.node_type]
        rel_nodes, sample_edges = [], []
        for (u, label), lst in G.out.items():
            if u in present:
                for v, _ in lst:
                    if v in present:
                        sample_edges.append((u, v, label))
                    elif name == "normalized" and G.node_type[v] not in mid_types:   # relation node: keep it if its other end is chosen too
                        for (r, l2), lst2 in G.out.items():
                            if r == v:
                                for w, _ in lst2:
                                    if w in present and w != u:
                                        rel_nodes.append(v); sample_edges += [(u, v, label), (v, w, l2)]
        order = present + list(dict.fromkeys(rel_nodes))
        seen = set(order)
        undirected = {}
        for a, b, l in sample_edges:
            if a in seen and b in seen:
                undirected.setdefault((min(a, b), max(a, b), l), (a, b, l))   # knows and party are stored both ways; draw once
        sample_edges = list(undirected.values())
        def label_of(v):
            pr = G.props[v]; return str(pr.get("name") or pr.get("firstName") or G.node_type[v])
        sample = {"nodes": [{"id": v, "type": G.node_type[v], "kind": "entity" if G.node_type[v] in mid_types else "relation", "label": label_of(v),
                             "props": {k: G.props[v][k] for k in (set(G.props[v]) - mid_props.get(G.node_type[v], set())) if G.node_type[v] in mid_props}} for v in order],
                  "edges": [{"s": a, "t": b, "label": l} for a, b, l in sample_edges]}
        out[name] = {"types": types, "edges": [{"s": a, "label": l, "t": b, "count": c} for (a, l, b), c in sorted(edges.items())], "sample": sample}
    return out


def guidelines() -> list[dict]:
    rows = md_tables((DOCS / "guidelines.md").read_text())[0][1:]
    return [{"id": r[0], "guideline": r[1], "evidence": r[2], "strength": r[3]} for r in rows]


def references() -> list[dict]:
    """The numbered list under "## References" in README.md, the numbering every [n] in the docs uses."""
    text = (ROOT / "README.md").read_text().split("\n## References\n", 1)[1]
    out = []
    for m in re.finditer(r"^\[(\d+)\] (.+)$", text, flags=re.M):
        doi = re.search(r"doi:(\S+)", m.group(2))
        out.append({"n": int(m.group(1)), "text": re.sub(r"\s*doi:\S+$", "", m.group(2)), "doi": doi.group(1) if doi else None})
    return out


def build() -> dict:
    return {"rq1": rq1(), "rq2": rq2(), "rq3": rq3(), "guidelines": guidelines(), "schemas": schema_graphs(), "references": references()}


if __name__ == "__main__":
    data = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(data['rq1']['rows'])} frameworks, "
          f"{len(data['rq2']['cases'])} cases, {len(data['rq3']['bench'])} bench rows")
