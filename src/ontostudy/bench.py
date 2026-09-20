"""Run the twenty questions against the three schemas at several scales.

For each (scale, schema, query) records: static hop count (edge traversals),
property reads, best-of-k latency, and per-schema build time and size. Also
checks that all three schemas return the same answer for every query.

    python -m ontostudy.bench --scales 1000 3000 10000 --repeats 5 --out docs/results/bench.csv

Follow-up runs (docs/results/RESULTS.md, "Follow-up runs"):

    python -m ontostudy.bench --schemas flat flat_indexed mid --out docs/results/bench_indexed.csv
    python -m ontostudy.bench --skew 1 --schemas flat flat_indexed mid normalized --out docs/results/bench_skew.csv

With --skew the query parameters are drawn in proportion to population (a
random person's city, a random job's employer, a random message's tag), so
the head of the distribution is asked about as often as it is populated.
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
from .schemas import SCHEMAS, VARIANTS
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
    runs: str = ""     # every repeat's seconds per query, semicolon-separated, for confidence intervals


def make_args(D: Dataset, rng: random.Random, n: int, weighted: bool = False) -> list[dict]:
    """n parameter sets per query, drawn once per dataset and shared by all schemas."""
    pid = [p["id"] for p in D.persons]
    tags = [t["name"] for t in D.tags]
    cities = [c["name"] for c in D.cities]
    orgs = [o["name"] for o in D.orgs if o["kind"] == "company"]
    if weighted:
        name = {x["id"]: x["name"] for x in D.tags + D.cities + D.orgs}
        tags = [name[t] for m in D.posts + D.comments for t in m["tags"]]
        cities = [name[p["cityId"]] for p in D.persons]
        orgs = [name[o] for _, o, _ in D.work]
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


def run(scales, repeats, n_args, seed=0, schema_names=None, skew=0.0):
    rows, sizes = [], []
    chosen = {k: {**SCHEMAS, **VARIANTS}[k] for k in (schema_names or SCHEMAS)}
    for n in scales:
        D = generate(n, seed, skew)
        args = make_args(D, random.Random(seed), n_args, weighted=skew > 0)
        schemas = {}
        for name, cls in chosen.items():
            t0 = time.perf_counter(); S = cls(D); bt = time.perf_counter() - t0
            c = S.G.counts()
            sizes.append({"scale": n, "schema": name, "build_seconds": round(bt, 3), "nodes": c["nodes"], "edges": c["edges"], "mbytes": round(S.G.nbytes() / 1e6, 1)})
            schemas[name] = S
        for qid, fn in QUERIES.items():
            answers = {}
            for name, S in schemas.items():
                times, hops, reads = [], 0, 0
                for _ in range(repeats):
                    S.G.reset(); t0 = time.perf_counter()
                    res = [fn(S, a) for a in args]
                    times.append((time.perf_counter() - t0) / n_args)
                    hops, reads = S.G.hops, S.G.prop_reads
                answers[name] = res
                rows.append(Row(n, name, qid, hops // n_args, reads // n_args, min(times), True, ";".join(f"{t:.3e}" for t in times)))
            ref = answers.get("normalized", answers["mid"])
            for r in rows[-len(schemas):]:
                r.correct = answers[r.schema] == ref
        print(f"scale {n}: done ({len(rows)} rows)")
    return rows, sizes


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scales", type=int, nargs="+", default=[1000, 3000, 10000])
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--n-args", type=int, default=20, help="parameter sets per query")
    p.add_argument("--out", default="docs/results/bench.csv")
    p.add_argument("--schemas", nargs="+", default=list(SCHEMAS), choices=list(SCHEMAS) + list(VARIANTS))
    p.add_argument("--skew", type=float, default=0.0, help="Zipf exponent for city / employer / tag fan-in (0 = uniform)")
    a = p.parse_args(argv)
    rows, sizes = run(a.scales, a.repeats, a.n_args, schema_names=a.schemas, skew=a.skew)
    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys())); w.writeheader(); w.writerows(asdict(r) for r in rows)
    with out.with_name(out.name.replace("bench", "sizes") if "bench" in out.name else "sizes_" + out.name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sizes[0].keys())); w.writeheader(); w.writerows(sizes)
    bad = [r for r in rows if not r.correct]
    print(f"{len(rows)} rows -> {out.relative_to(ROOT)}; {len(bad)} answer mismatches")
    for r in bad[:10]:
        print("  MISMATCH", r.scale, r.schema, r.query)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
