"""Write-path cost of the three schemas: how many stored records one change touches.

The read benchmark rewards flat for copying city, country and employer names
onto every person. This measures what that copy costs when the world changes.
Four updates, each applied to every schema; the count is the number of node
property writes plus edge insertions or deletions the update needs, and the
time is best of k.

    python -m ontostudy.writes --scales 1000 3000 10000 --out docs/results/writes.csv

Updates
    rename_city      a city changes its name (every person living there, in flat)
    move_person      one person moves to another city
    change_employer  one person leaves one company for another
    rename_tag       a tag is renamed (every message carrying it, in flat)
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import random
import sys
import time

from .schemas import SCHEMAS, VARIANTS
from .synth import Dataset, generate

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Writes:
    """One method per (update, schema family). Each returns the record count."""

    def __init__(self, S):
        self.S, self.G = S, S.G
        self.kind = "flat" if S.name.startswith("flat") else S.name
        self.cur: dict[int, str] = {}   # current name of a renamed city or tag, keyed by id

    # -- helpers
    def _set(self, n, key, value):
        self.G.props[n][key] = value; return 1

    def _drop_edge(self, u, label, v):
        self.G.out[(u, label)] = [(x, e) for x, e in self.G.out[(u, label)] if x != v]
        self.G.inn[(v, label)] = [(x, e) for x, e in self.G.inn[(v, label)] if x != u]
        return 2

    def _add_edge(self, u, label, v, **props):
        self.G.add_edge(u, label, v, **props); return 2

    def _reindex(self, index, old_key, new_key, item):
        idx = self.G.indexes.get(index)
        if idx is None: return 0
        if old_key is not None and item in idx.get(old_key, []): idx[old_key].remove(item)
        if new_key is not None: idx.setdefault(new_key, []).append(item)
        return 1

    # -- updates
    def rename_city(self, D: Dataset, rng):
        c = rng.choice(D.cities); old = self.cur.get(c["id"], c["name"]); new = old + "_r"; self.cur[c["id"]] = new
        if self.kind == "flat":
            n = 0
            affected = self.G.indexes["city"].get(old, []) if "city" in self.G.indexes else self.G.nodes("Person")
            for u in affected:
                if self.G.props[u]["city"] == old:
                    n += self._set(u, "city", new)
            if "city" in self.G.indexes:
                self.G.indexes["city"][new] = self.G.indexes["city"].pop(old, []); n += 1
            return n
        return self._set(c["id"], "name", new)

    def move_person(self, D: Dataset, rng):
        p = rng.choice(D.persons); city = rng.choice(D.cities); country = next(x for x in D.countries if x["id"] == city["countryId"])
        if self.kind == "flat":
            old, cname = self.G.props[p["id"]]["city"], self.cur.get(city["id"], city["name"])
            n = self._set(p["id"], "city", cname) + self._set(p["id"], "country", country["name"])
            return n + self._reindex("city", old, cname, p["id"])
        if self.kind == "mid":
            old = self.G.o(p["id"], "isLocatedIn")[0][0]
            return self._drop_edge(p["id"], "isLocatedIn", old) + self._add_edge(p["id"], "isLocatedIn", city["id"])
        r = self.G.o(p["id"], "resides")[0][0]                       # normalized: repoint the Residence node
        old = self.G.o(r, "in")[0][0]
        return self._drop_edge(r, "in", old) + self._add_edge(r, "in", city["id"])

    def change_employer(self, D: Dataset, rng):
        p = rng.choice(D.persons); companies = [o for o in D.orgs if o["kind"] == "company"]
        new = rng.choice(companies); country = next(x for x in D.countries if x["id"] == new["countryId"])
        if self.kind == "flat":
            emp = list(self.G.props[p["id"]]["employers"])
            old = emp[0][0] if emp else None
            emp = emp[1:] + [(new["name"], country["name"], 2021)]
            return self._set(p["id"], "employers", emp) + self._reindex("org", old, new["name"], p["id"])
        if self.kind == "mid":
            cur = self.G.o(p["id"], "workAt")
            n = self._drop_edge(p["id"], "workAt", cur[0][0]) if cur else 0
            return n + self._add_edge(p["id"], "workAt", new["id"], year=2021)
        cur = self.G.o(p["id"], "employed")
        n = 0
        if cur:
            r = cur[0][0]; old = self.G.o(r, "employer")[0][0]
            n += self._drop_edge(p["id"], "employed", r) + self._drop_edge(r, "employer", old) + 1   # node retired
        r = self.S._n; self.S._n += 1
        self.G.add_node(r, "Employment", year=2021)
        return n + 1 + self._add_edge(p["id"], "employed", r) + self._add_edge(r, "employer", new["id"])

    def rename_tag(self, D: Dataset, rng):
        t = rng.choice(D.tags); old = self.cur.get(t["id"], t["name"]); new = old + "_r"; self.cur[t["id"]] = new
        if self.kind == "flat":
            n = 0
            affected = self.G.indexes["tag"].get(old, []) if "tag" in self.G.indexes else self.G.nodes("Post") + self.G.nodes("Comment")
            for m in affected:
                tags = self.G.props[m]["tags"]
                if old in tags:
                    n += self._set(m, "tags", [new if x == old else x for x in tags])
            if "tag" in self.G.indexes:
                self.G.indexes["tag"][new] = self.G.indexes["tag"].pop(old, []); n += 1
            return n
        return self._set(t["id"], "name", new)


UPDATES = ["rename_city", "move_person", "change_employer", "rename_tag"]


def run(scales, repeats, n_ops, seed=0):
    rows = []
    for n in scales:
        D = generate(n, seed)
        for name, cls in {**SCHEMAS, **VARIANTS}.items():
            S = cls(D); W = Writes(S)
            for upd in UPDATES:
                best, records = float("inf"), 0
                for _ in range(repeats):
                    rng = random.Random(seed); records = 0
                    t0 = time.perf_counter()
                    for _ in range(n_ops):
                        records += getattr(W, upd)(D, rng)
                    best = min(best, (time.perf_counter() - t0) / n_ops)
                rows.append({"scale": n, "schema": name, "update": upd, "records": records // n_ops, "seconds": best})
        print(f"scale {n}: done")
    return rows


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scales", type=int, nargs="+", default=[1000, 3000, 10000])
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--n-ops", type=int, default=20)
    p.add_argument("--out", default="docs/results/writes.csv")
    a = p.parse_args(argv)
    rows = run(a.scales, a.repeats, a.n_ops)
    out = ROOT / a.out
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} rows -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
