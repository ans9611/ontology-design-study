"""Synthetic social-network data in the shape of LDBC SNB.

Entities: Person, Post, Comment, Forum, Tag, TagClass, Organisation (company /
university), Place (city -> country). Relations: knows, hasCreator, likes,
hasMember(joinDate), hasTag, hasType, isSubclassOf, isLocatedIn, workAt(year),
studyAt, replyOf, containerOf.

The generator is deterministic for a given (n_persons, seed). Degrees follow
the same shape as SNB: a preferential-attachment friendship graph, posts per
person proportional to degree, comments as reply trees.

Dated note (docs/hypotheses.md) records why this replaces LDBC Datagen.

`skew` > 0 draws each person's city, employers and each message's tags from a
Zipf distribution over the entities (weight 1 / rank**skew) instead of
uniformly, so a few cities, companies and tags carry most of the fan-in. The
default 0 reproduces the main run exactly.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class Dataset:
    n_persons: int
    seed: int
    persons: list[dict] = field(default_factory=list)      # id, firstName, birthdayMonth, cityId
    knows: list[tuple[int, int, int]] = field(default_factory=list)          # (p1, p2, since)
    posts: list[dict] = field(default_factory=list)        # id, creator, forum, date, tags[]
    comments: list[dict] = field(default_factory=list)     # id, creator, replyOf (post or comment id), date, tags[]
    likes: list[tuple[int, int, int]] = field(default_factory=list)          # (person, message, date)
    forums: list[dict] = field(default_factory=list)       # id, moderator
    memberships: list[tuple[int, int, int]] = field(default_factory=list)    # (forum, person, joinDate)
    tags: list[dict] = field(default_factory=list)         # id, name, tagClass
    tagclasses: list[dict] = field(default_factory=list)   # id, name, parent
    orgs: list[dict] = field(default_factory=list)         # id, name, kind, countryId
    work: list[tuple[int, int, int]] = field(default_factory=list)           # (person, org, year)
    cities: list[dict] = field(default_factory=list)       # id, name, countryId
    countries: list[dict] = field(default_factory=list)    # id, name


def generate(n_persons: int, seed: int = 0, skew: float = 0.0) -> Dataset:
    rng = random.Random(seed)
    D = Dataset(n_persons, seed)
    nid = [0]

    def new() -> int:
        nid[0] += 1
        return nid[0]

    zipf: dict[int, list[float]] = {}   # Zipf weights by pool length; the same list every call, so computed once

    def pick(pool, k=1):
        """k distinct items, uniform when skew == 0, Zipf by list position otherwise."""
        if not skew:
            return rng.sample(pool, k)
        w = zipf.get(len(pool))
        if w is None:
            w = zipf[len(pool)] = [1 / (i + 1) ** skew for i in range(len(pool))]
        out = []
        while len(out) < k:
            x = rng.choices(pool, w)[0]
            if x not in out:
                out.append(x)
        return out

    # places
    n_countries = max(5, n_persons // 400)
    D.countries = [{"id": new(), "name": f"Country{i}"} for i in range(n_countries)]
    for c in D.countries:
        for j in range(4):
            D.cities.append({"id": new(), "name": f"City{c['name'][7:]}_{j}", "countryId": c["id"]})

    # tag classes (3-level tree) and tags
    root = {"id": new(), "name": "Thing", "parent": None}
    D.tagclasses.append(root)
    mids = [{"id": new(), "name": f"Class{i}", "parent": root["id"]} for i in range(8)]
    D.tagclasses += mids
    leaves = []
    for m in mids:
        for j in range(4):
            leaves.append({"id": new(), "name": f"{m['name']}_{j}", "parent": m["id"]})
    D.tagclasses += leaves
    n_tags = max(50, n_persons // 10)
    D.tags = [{"id": new(), "name": f"Tag{i}", "tagClass": rng.choice(leaves)["id"]} for i in range(n_tags)]

    # organisations
    for c in D.countries:
        for j in range(3):
            D.orgs.append({"id": new(), "name": f"Company{c['id']}_{j}", "kind": "company", "countryId": c["id"]})
        D.orgs.append({"id": new(), "name": f"Univ{c['id']}", "kind": "university", "countryId": c["id"]})
    companies = [o for o in D.orgs if o["kind"] == "company"]

    # persons
    for i in range(n_persons):
        D.persons.append({"id": new(), "firstName": f"P{i}", "birthdayMonth": rng.randint(1, 12),
                          "cityId": pick(D.cities)[0]["id"]})
    pid = [p["id"] for p in D.persons]
    city_country = {c["id"]: c["countryId"] for c in D.cities}

    # knows: preferential attachment, m=5, plus locality (same city) bias
    m = 5
    targets = list(pid[:m])
    edges = set()
    for i in range(m, n_persons):
        u = pid[i]
        chosen = set()
        while len(chosen) < m:
            v = rng.choice(targets) if rng.random() < 0.8 else rng.choice(pid[:i])
            if v != u:
                chosen.add(v)
        for v in chosen:
            edges.add((min(u, v), max(u, v)))
            targets += [u, v]
    for (u, v) in sorted(edges):
        D.knows.append((u, v, rng.randint(2010, 2020)))

    # work
    for p in D.persons:
        for o in pick(companies, rng.randint(1, 2)):
            D.work.append((p["id"], o["id"], rng.randint(2000, 2020)))

    # forums and memberships
    n_forums = max(20, n_persons // 5)
    D.forums = [{"id": new(), "moderator": rng.choice(pid)} for _ in range(n_forums)]
    deg = {u: 0 for u in pid}
    for u, v, _ in D.knows:
        deg[u] += 1; deg[v] += 1
    for f in D.forums:
        members = rng.sample(pid, min(len(pid), rng.randint(5, 40)))
        for u in members:
            D.memberships.append((f["id"], u, rng.randint(2010, 2020)))
    member_of = {}
    for f, u, _ in D.memberships:
        member_of.setdefault(u, []).append(f)

    # posts and comments
    for p in D.persons:
        forums = member_of.get(p["id"], [])
        if not forums:
            continue
        for _ in range(1 + deg[p["id"]] // 3):
            post = {"id": new(), "creator": p["id"], "forum": rng.choice(forums), "date": rng.randint(20180101, 20221231),
                    "tags": [t["id"] for t in pick(D.tags, rng.randint(1, 3))]}
            D.posts.append(post)
    all_msgs = [po["id"] for po in D.posts]
    for po in D.posts:
        parent = po["id"]
        for _ in range(rng.randint(0, 4)):
            c = {"id": new(), "creator": rng.choice(pid), "replyOf": parent, "date": po["date"] + rng.randint(0, 100),
                 "tags": [t["id"] for t in pick(D.tags, rng.randint(0, 2))]}
            D.comments.append(c); all_msgs.append(c["id"])
            if rng.random() < 0.5:
                parent = c["id"]
    for msg in all_msgs:
        for u in rng.sample(pid, min(len(pid), rng.randint(0, 3))):
            D.likes.append((u, msg, rng.randint(20180101, 20221231)))
    return D
