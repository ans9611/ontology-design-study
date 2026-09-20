"""Second engine: the three schemas in Kùzu (embedded, Cypher) on the six diagnostic queries.

The main run uses an in-memory Python graph whose constants (latency, memory)
are not those of a database. This loads the same Dataset into Kùzu three ways,
writes each diagnostic query in Cypher once per schema, and records engine
execution time (best of k), result agreement across schemas, and on-disk size.
Hop counts are not available here; they are the Python engine's metric.

    python -m ontostudy.engine_kuzu --scales 1000 3000 10000 --out docs/results/bench_kuzu.csv

Queries: Q02, Q11, Q13, Q17, Q18, Q19 (the two forward reads where flat wins,
the path query, and the three reverse lookups where unindexed flat scans).
Kùzu has no secondary property indexes, so flat's reverse lookups scan here as
in the Python engine; mid and normalized reach the entity node by primary key.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import random
import shutil
import sys
import tempfile
import time

import kuzu

from .bench import make_args
from .synth import Dataset, generate

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _csv(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    return str(path)


def _lst(xs):
    return "[" + ",".join(str(x) for x in xs) + "]"


def load(D: Dataset, schema: str, workdir: pathlib.Path) -> kuzu.Connection:
    dbdir = workdir / f"{schema}.kuzu"
    shutil.rmtree(dbdir, ignore_errors=True)          # one database per (scale, schema); the workdir is reused
    if dbdir.exists(): dbdir.unlink()
    db = kuzu.Database(str(dbdir)); c = kuzu.Connection(db)
    tmp = workdir / f"{schema}_csv"; tmp.mkdir(exist_ok=True)
    country = {x["id"]: x["name"] for x in D.countries}
    city = {x["id"]: (x["name"], country[x["countryId"]]) for x in D.cities}
    org = {x["id"]: (x["name"], country[x["countryId"]]) for x in D.orgs}
    tag = {x["id"]: x["name"] for x in D.tags}
    knows = D.knows + [(v, u, s) for u, v, s in D.knows]          # both directions, as the Python graph stores it
    msgs = [(m["id"], m["date"], "Post", m["creator"], m["tags"]) for m in D.posts] + \
           [(m["id"], m["date"], "Comment", m["creator"], m["tags"]) for m in D.comments]

    if schema == "flat":
        work = {}
        for p, o, y in D.work: work.setdefault(p, []).append(o)
        c.execute("CREATE NODE TABLE Person(id INT64, city STRING, country STRING, employerNames STRING[], employerCountries STRING[], PRIMARY KEY(id))")
        c.execute("CREATE NODE TABLE Message(id INT64, date INT64, kind STRING, tags STRING[], PRIMARY KEY(id))")
        c.execute("CREATE REL TABLE knows(FROM Person TO Person, since INT64)")
        c.execute("CREATE REL TABLE hasCreator(FROM Message TO Person)")
        c.execute(f'COPY Person FROM "{_csv(tmp / "person.csv", [(p["id"], city[p["cityId"]][0], city[p["cityId"]][1], _lst(org[o][0] for o in work.get(p["id"], [])), _lst(org[o][1] for o in work.get(p["id"], []))) for p in D.persons], ["id", "city", "country", "employerNames", "employerCountries"])}" (HEADER=true)')
        c.execute(f'COPY Message FROM "{_csv(tmp / "msg.csv", [(i, d, k, _lst(tag[t] for t in ts)) for i, d, k, _, ts in msgs], ["id", "date", "kind", "tags"])}" (HEADER=true)')
        c.execute(f'COPY knows FROM "{_csv(tmp / "knows.csv", knows, ["from", "to", "since"])}" (HEADER=true)')
        c.execute(f'COPY hasCreator FROM "{_csv(tmp / "creator.csv", [(i, cr) for i, _, _, cr, _ in msgs], ["from", "to"])}" (HEADER=true)')
        return c

    # shared entity tables for mid and normalized
    c.execute("CREATE NODE TABLE Country(id INT64, name STRING, PRIMARY KEY(id))")
    c.execute("CREATE NODE TABLE City(id INT64, name STRING, PRIMARY KEY(id))")
    c.execute("CREATE NODE TABLE Organisation(id INT64, name STRING, PRIMARY KEY(id))")
    c.execute("CREATE NODE TABLE Tag(id INT64, name STRING, PRIMARY KEY(id))")
    c.execute("CREATE NODE TABLE Person(id INT64, PRIMARY KEY(id))")
    c.execute("CREATE NODE TABLE Message(id INT64, date INT64, kind STRING, PRIMARY KEY(id))")
    c.execute(f'COPY Country FROM "{_csv(tmp / "country.csv", [(x["id"], x["name"]) for x in D.countries], ["id", "name"])}" (HEADER=true)')
    c.execute(f'COPY City FROM "{_csv(tmp / "city.csv", [(x["id"], x["name"]) for x in D.cities], ["id", "name"])}" (HEADER=true)')
    c.execute(f'COPY Organisation FROM "{_csv(tmp / "org.csv", [(x["id"], x["name"]) for x in D.orgs], ["id", "name"])}" (HEADER=true)')
    c.execute(f'COPY Tag FROM "{_csv(tmp / "tag.csv", [(x["id"], x["name"]) for x in D.tags], ["id", "name"])}" (HEADER=true)')
    c.execute(f'COPY Person FROM "{_csv(tmp / "person.csv", [(p["id"],) for p in D.persons], ["id"])}" (HEADER=true)')
    c.execute(f'COPY Message FROM "{_csv(tmp / "msg.csv", [(i, d, k) for i, d, k, _, _ in msgs], ["id", "date", "kind"])}" (HEADER=true)')

    if schema == "mid":
        c.execute("CREATE REL TABLE knows(FROM Person TO Person, since INT64)")
        c.execute("CREATE REL TABLE personIn(FROM Person TO City)")
        c.execute("CREATE REL TABLE cityIn(FROM City TO Country)")
        c.execute("CREATE REL TABLE orgIn(FROM Organisation TO Country)")
        c.execute("CREATE REL TABLE workAt(FROM Person TO Organisation, year INT64)")
        c.execute("CREATE REL TABLE hasCreator(FROM Message TO Person)")
        c.execute("CREATE REL TABLE hasTag(FROM Message TO Tag)")
        c.execute(f'COPY knows FROM "{_csv(tmp / "knows.csv", knows, ["from", "to", "since"])}" (HEADER=true)')
        c.execute(f'COPY personIn FROM "{_csv(tmp / "pin.csv", [(p["id"], p["cityId"]) for p in D.persons], ["from", "to"])}" (HEADER=true)')
        c.execute(f'COPY cityIn FROM "{_csv(tmp / "cin.csv", [(x["id"], x["countryId"]) for x in D.cities], ["from", "to"])}" (HEADER=true)')
        c.execute(f'COPY orgIn FROM "{_csv(tmp / "oin.csv", [(x["id"], x["countryId"]) for x in D.orgs], ["from", "to"])}" (HEADER=true)')
        c.execute(f'COPY workAt FROM "{_csv(tmp / "work.csv", D.work, ["from", "to", "year"])}" (HEADER=true)')
        c.execute(f'COPY hasCreator FROM "{_csv(tmp / "creator.csv", [(i, cr) for i, _, _, cr, _ in msgs], ["from", "to"])}" (HEADER=true)')
        c.execute(f'COPY hasTag FROM "{_csv(tmp / "hastag.csv", [(i, t) for i, _, _, _, ts in msgs for t in ts], ["from", "to"])}" (HEADER=true)')
        return c

    # normalized: one node table per relation, two edge tables per relation
    nid = [max(m[0] for m in msgs) + max(t for t in tag) + 1]
    def fresh(): nid[0] += 1; return nid[0]
    rels = {}   # name -> (node rows, from rows, to rows)
    def reify(name, pairs, props=None):
        nodes, fr, to = [], [], []
        for k, (u, v) in enumerate(pairs):
            r = fresh(); nodes.append((r,) + ((props[k],) if props else ())); fr.append((u, r)); to.append((r, v))
        rels[name] = (nodes, fr, to)
    reify("Knows", [(u, v) for u, v, _ in knows], [s for _, _, s in knows])
    reify("Residence", [(p["id"], p["cityId"]) for p in D.persons])
    reify("PartOf", [(x["id"], x["countryId"]) for x in D.cities])
    reify("OrgLocation", [(x["id"], x["countryId"]) for x in D.orgs])
    reify("Employment", [(p, o) for p, o, _ in D.work], [y for _, _, y in D.work])
    reify("Authorship", [(i, cr) for i, _, _, cr, _ in msgs])
    reify("Tagging", [(i, t) for i, _, _, _, ts in msgs for t in ts])
    ends = {"Knows": ("Person", "Person", "since"), "Residence": ("Person", "City", None), "PartOf": ("City", "Country", None),
            "OrgLocation": ("Organisation", "Country", None), "Employment": ("Person", "Organisation", "year"),
            "Authorship": ("Message", "Person", None), "Tagging": ("Message", "Tag", None)}
    for name, (nodes, fr, to) in rels.items():
        a, b, prop = ends[name]
        c.execute(f"CREATE NODE TABLE {name}(id INT64{', ' + prop + ' INT64' if prop else ''}, PRIMARY KEY(id))")
        c.execute(f"CREATE REL TABLE {name}From(FROM {a} TO {name})")
        c.execute(f"CREATE REL TABLE {name}To(FROM {name} TO {b})")
        c.execute(f'COPY {name} FROM "{_csv(tmp / f"{name}.csv", nodes, ["id"] + ([prop] if prop else []))}" (HEADER=true)')
        c.execute(f'COPY {name}From FROM "{_csv(tmp / f"{name}_from.csv", fr, ["from", "to"])}" (HEADER=true)')
        c.execute(f'COPY {name}To FROM "{_csv(tmp / f"{name}_to.csv", to, ["from", "to"])}" (HEADER=true)')
    return c


# One Cypher text per (query, schema). Parameters match bench.make_args.
CYPHER = {
    "Q02": {
        "flat": """MATCH (p:Person {id: $person})-[:knows]->(f:Person)-[:knows]->(ff:Person)
                   WHERE ff.id <> p.id AND ff.country = p.country RETURN DISTINCT ff.id AS x ORDER BY x""",
        "mid": """MATCH (p:Person {id: $person})-[:knows]->(f:Person)-[:knows]->(ff:Person),
                        (p)-[:personIn]->(:City)-[:cityIn]->(c:Country), (ff)-[:personIn]->(:City)-[:cityIn]->(c)
                  WHERE ff.id <> p.id RETURN DISTINCT ff.id AS x ORDER BY x""",
        "normalized": """MATCH (p:Person {id: $person})-[:KnowsFrom]->(:Knows)-[:KnowsTo]->(f:Person)-[:KnowsFrom]->(:Knows)-[:KnowsTo]->(ff:Person),
                               (p)-[:ResidenceFrom]->(:Residence)-[:ResidenceTo]->(:City)-[:PartOfFrom]->(:PartOf)-[:PartOfTo]->(c:Country),
                               (ff)-[:ResidenceFrom]->(:Residence)-[:ResidenceTo]->(:City)-[:PartOfFrom]->(:PartOf)-[:PartOfTo]->(c)
                         WHERE ff.id <> p.id RETURN DISTINCT ff.id AS x ORDER BY x""",
    },
    "Q11": {
        "flat": """MATCH (p:Person {id: $person})-[:knows]->(f:Person)
                   UNWIND range(1, size(f.employerNames)) AS i
                   WITH f, f.employerNames[i] AS org, f.employerCountries[i] AS cn WHERE cn = $country
                   RETURN f.id AS x, org ORDER BY x, org""",
        "mid": """MATCH (p:Person {id: $person})-[:knows]->(f:Person)-[:workAt]->(o:Organisation)-[:orgIn]->(c:Country {name: $country})
                  RETURN f.id AS x, o.name AS org ORDER BY x, org""",
        "normalized": """MATCH (p:Person {id: $person})-[:KnowsFrom]->(:Knows)-[:KnowsTo]->(f:Person)-[:EmploymentFrom]->(:Employment)-[:EmploymentTo]->(o:Organisation)
                               -[:OrgLocationFrom]->(:OrgLocation)-[:OrgLocationTo]->(c:Country {name: $country})
                         RETURN f.id AS x, o.name AS org ORDER BY x, org""",
    },
    "Q13": {
        "flat": """MATCH p = (a:Person {id: $person})-[:knows* SHORTEST 1..12]->(b:Person {id: $person2}) RETURN length(p) AS x""",
        "mid": """MATCH p = (a:Person {id: $person})-[:knows* SHORTEST 1..12]->(b:Person {id: $person2}) RETURN length(p) AS x""",
        "normalized": """MATCH p = (a:Person {id: $person})-[:KnowsFrom|:KnowsTo* SHORTEST 1..24]->(b:Person {id: $person2}) RETURN length(p) / 2 AS x""",
    },
    "Q17": {
        "flat": """MATCH (u:Person)<-[:hasCreator]-(m:Message {kind: 'Post'}) WHERE list_contains(u.employerNames, $org)
                   UNWIND m.tags AS t RETURN t AS x, count(*) AS n ORDER BY n DESC, x LIMIT 10""",
        "mid": """MATCH (o:Organisation {name: $org})<-[:workAt]-(u:Person)<-[:hasCreator]-(m:Message {kind: 'Post'})-[:hasTag]->(t:Tag)
                  RETURN t.name AS x, count(*) AS n ORDER BY n DESC, x LIMIT 10""",
        "normalized": """MATCH (o:Organisation {name: $org})<-[:EmploymentTo]-(:Employment)<-[:EmploymentFrom]-(u:Person)
                               <-[:AuthorshipTo]-(:Authorship)<-[:AuthorshipFrom]-(m:Message {kind: 'Post'})-[:TaggingFrom]->(:Tagging)-[:TaggingTo]->(t:Tag)
                         RETURN t.name AS x, count(*) AS n ORDER BY n DESC, x LIMIT 10""",
    },
    "Q18": {
        "flat": """MATCH (m:Message) WHERE list_contains(m.tags, $tag) AND m.date >= $d0 AND m.date <= $d1
                   RETURN m.date / 100 AS x, count(*) AS n ORDER BY x""",
        "mid": """MATCH (t:Tag {name: $tag})<-[:hasTag]-(m:Message) WHERE m.date >= $d0 AND m.date <= $d1
                  RETURN m.date / 100 AS x, count(*) AS n ORDER BY x""",
        "normalized": """MATCH (t:Tag {name: $tag})<-[:TaggingTo]-(:Tagging)<-[:TaggingFrom]-(m:Message) WHERE m.date >= $d0 AND m.date <= $d1
                         RETURN m.date / 100 AS x, count(*) AS n ORDER BY x""",
    },
    "Q19": {
        "flat": """MATCH (u:Person {city: $city}) RETURN u.id AS x, u.employerNames AS orgs ORDER BY x""",
        "mid": """MATCH (c:City {name: $city})<-[:personIn]-(u:Person) OPTIONAL MATCH (u)-[:workAt]->(o:Organisation)
                  RETURN u.id AS x, collect(o.name) AS orgs ORDER BY x""",
        "normalized": """MATCH (c:City {name: $city})<-[:ResidenceTo]-(:Residence)<-[:ResidenceFrom]-(u:Person)
                         OPTIONAL MATCH (u)-[:EmploymentFrom]->(:Employment)-[:EmploymentTo]->(o:Organisation)
                         RETURN u.id AS x, collect(o.name) AS orgs ORDER BY x""",
    },
}


def _norm(rows):
    """Comparable form: sort list-valued cells so collect() order does not matter."""
    return [tuple(sorted(v) if isinstance(v, list) else v for v in r) for r in rows]


def run(scales, repeats, n_args, seed=0, workdir=None):
    workdir = pathlib.Path(workdir or tempfile.mkdtemp(prefix="ontostudy_kuzu_"))
    rows, sizes = [], []
    for n in scales:
        D = generate(n, seed)
        args = make_args(D, random.Random(seed), n_args)
        conns = {}
        for schema in ("flat", "mid", "normalized"):
            t0 = time.perf_counter(); conns[schema] = load(D, schema, workdir); bt = time.perf_counter() - t0
            mb = sum(f.stat().st_size for f in (workdir / f"{schema}.kuzu").rglob("*") if f.is_file()) / 1e6 if (workdir / f"{schema}.kuzu").is_dir() else (workdir / f"{schema}.kuzu").stat().st_size / 1e6
            sizes.append({"scale": n, "schema": schema, "build_seconds": round(bt, 3), "mbytes": round(mb, 1)})
        for qid, texts in CYPHER.items():
            answers = {}
            for schema, c in conns.items():
                q = texts[schema]; times = []
                for _ in range(repeats):
                    tot, res = 0.0, []
                    for a in args:
                        r = c.execute(q, {k: v for k, v in a.items() if f"${k}" in q})
                        tot += r.get_execution_time(); res.append(_norm(r.get_all()))
                    times.append(tot / n_args / 1000)          # seconds per query
                answers[schema] = res
                rows.append({"scale": n, "schema": schema, "query": qid, "seconds": min(times), "correct": True,
                             "runs": ";".join(f"{t:.3e}" for t in times)})
            for r in rows[-3:]:
                r["correct"] = answers[r["schema"]] == answers["mid"]
        for c in conns.values(): c.close()
        print(f"scale {n}: done ({len(rows)} rows)")
    shutil.rmtree(workdir, ignore_errors=True)
    return rows, sizes


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scales", type=int, nargs="+", default=[1000, 3000, 10000])
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--n-args", type=int, default=20)
    p.add_argument("--out", default="docs/results/bench_kuzu.csv")
    a = p.parse_args(argv)
    rows, sizes = run(a.scales, a.repeats, a.n_args)
    out = ROOT / a.out
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with out.with_name(out.name.replace("bench", "sizes") if "bench" in out.name else "sizes_" + out.name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sizes[0].keys())); w.writeheader(); w.writerows(sizes)
    bad = [r for r in rows if not r["correct"]]
    print(f"{len(rows)} rows -> {out}; {len(bad)} answer mismatches")
    for r in bad[:10]: print("  MISMATCH", r["scale"], r["schema"], r["query"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
