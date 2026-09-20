"""Run the twenty questions against the three schemas at several scales.

For each (scale, schema, query) records: static hop count (edge traversals),
property reads, best-of-k latency, and per-schema build time and size. Also
checks that all three schemas return the same answer for every query.

    python -m ontostudy.bench --scales 1000 3000 10000 --repeats 5 --out docs/results/bench.csv
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import random
import sys
import time
from dataclasses import asdict, dataclass

from .queries import QUERIES
from .schemas import SCHEMAS
from .synth import Dataset, generate

ROOT = pathlib.Path(__file__).resolve().parents[2]


@dataclass
class Row:
    scale: int
    schema: str
    query: str
    hops: int
    prop_reads: int
    seconds: float
    correct: bool


def make_args(D: Dataset, rng: random.Random, n: int) -> list[dict]:
    """n parameter sets per query, drawn once per dataset and shared by all schemas."""
    pid = [p["id"] for p in D.persons]
    tags = [t["name"] for t in D.tags]
    cities = [c["name"] for c in D.cities]
    orgs = [o["name"] for o in D.orgs if o["kind"] == "company"]
    countries = [c["name"] for c in D.countries]
    classes = [tc["name"] for tc in D.tagclasses if tc["parent"]]
    posts = [po["id"] for po in D.posts]
    forums = [f["id"] for f in D.forums]
    return [{
        "person": rng.choice(pid), "person2": rng.choice(pid), "tag": rng.choice(tags),
        "city": rng.choice(cities), "org": rng.choice(orgs), "country": rng.choice(countries),
        "tagclass": rng.choice(classes), "post": rng.choice(posts), "forum": rng.choice(forums),
        "month": rng.randint(1, 12), "year": 2014, "d0": 20200101, "d1": 20211231,
    } for _ in range(n)]


def run(scales, repeats, n_args, seed=0):
    rows, sizes = [], []
    for n in scales:
        D = generate(n, seed)
        args = make_args(D, random.Random(seed), n_args)
        schemas = {}
        for name, cls in SCHEMAS.items():
            t0 = time.perf_counter(); S = cls(D); bt = time.perf_counter() - t0
            c = S.G.counts()
            sizes.append({"scale": n, "schema": name, "build_seconds": round(bt, 3), "nodes": c["nodes"], "edges": c["edges"], "mbytes": round(S.G.nbytes() / 1e6, 1)})
            schemas[name] = S
        for qid, fn in QUERIES.items():
            answers = {}
            for name, S in schemas.items():
                best, hops, reads = float("inf"), 0, 0
                for _ in range(repeats):
                    S.G.reset(); t0 = time.perf_counter()
                    res = [fn(S, a) for a in args]
                    best = min(best, time.perf_counter() - t0)
                    hops, reads = S.G.hops, S.G.prop_reads
                answers[name] = res
                rows.append(Row(n, name, qid, hops // n_args, reads // n_args, best / n_args, True))
            ref = answers["normalized"]
            for r in rows[-3:]:
                r.correct = answers[r.schema] == ref
        print(f"scale {n}: done ({len(rows)} rows)")
    return rows, sizes


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scales", type=int, nargs="+", default=[1000, 3000, 10000])
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--n-args", type=int, default=20, help="parameter sets per query")
    p.add_argument("--out", default="docs/results/bench.csv")
    a = p.parse_args(argv)
    rows, sizes = run(a.scales, a.repeats, a.n_args)
    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys())); w.writeheader(); w.writerows(asdict(r) for r in rows)
    with out.with_name("sizes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sizes[0].keys())); w.writeheader(); w.writerows(sizes)
    bad = [r for r in rows if not r.correct]
    print(f"{len(rows)} rows -> {out.relative_to(ROOT)}; {len(bad)} answer mismatches")
    for r in bad[:10]:
        print("  MISMATCH", r.scale, r.schema, r.query)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
