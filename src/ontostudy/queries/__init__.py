"""The twenty benchmark questions (QUESTIONS.md), written once against Schema.

Each returns a canonical, order-independent value so answers can be compared
across schemas. Q20 uses PPRMatrix from the pagerank package.
"""

from __future__ import annotations

from collections import Counter, deque
from typing import Any, Callable

import networkx as nx

from ..schemas.base import Schema

Query = Callable[[Schema, dict], Any]
QUERIES: dict[str, Query] = {}


def q(qid: str):
    def deco(fn):
        QUERIES[qid] = fn
        return fn
    return deco


def _fof(S: Schema, p: int) -> set[int]:
    f1 = {v for v, _ in S.friends(p)}
    f2 = set()
    for v in f1:
        f2 |= {w for w, _ in S.friends(v)}
    return (f1 | f2) - {p}


@q("Q01")
def q01(S, a):  # friends' names and cities
    return sorted((S.person_props(v)["firstName"], S.city_name(v)) for v, _ in S.friends(a["person"]))


@q("Q02")
def q02(S, a):  # friends of friends in the same country
    cn = S.country_name(a["person"])
    return sorted(v for v in _fof(S, a["person"]) if S.country_name(v) == cn)


@q("Q03")
def q03(S, a):  # 10 most recent posts by friends
    posts = []
    for v, _ in S.friends(a["person"]):
        posts += [(d, m) for m, d in S.posts_by(v)]
    return sorted(posts, reverse=True)[:10]


@q("Q04")
def q04(S, a):  # tags most used in friends' posts within a date range
    c = Counter()
    for v, _ in S.friends(a["person"]):
        for m, d in S.posts_by(v):
            if a["d0"] <= d <= a["d1"]:
                c.update(S.tag_names(m))
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:10]


@q("Q05")
def q05(S, a):  # forums friends joined after a date, ranked by posts from those friends
    friends = {v for v, _ in S.friends(a["person"])}
    forums = {}
    for v in friends:
        for f, jd in S.forums_of(v):
            if jd > a["year"]:
                forums.setdefault(f, set()).add(v)
    out = []
    for f, fr in forums.items():
        n = sum(1 for m in S.posts_in_forum(f) if S.creator(m) in fr)
        out.append((n, f))
    return sorted(out, reverse=True)[:10]


@q("Q06")
def q06(S, a):  # tags co-occurring with a tag on posts by friends-of-friends
    c = Counter()
    for v in _fof(S, a["person"]):
        for m, _ in S.posts_by(v):
            tags = S.tag_names(m)
            if a["tag"] in tags:
                c.update(t for t in tags if t != a["tag"])
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:10]


@q("Q07")
def q07(S, a):  # recent likers of my posts and whether they are friends
    friends = {v for v, _ in S.friends(a["person"])}
    out = []
    for m, _ in S.posts_by(a["person"]):
        for u, d in S.likers(m):
            out.append((d, u, u in friends))
    return sorted(out, reverse=True)[:20]


@q("Q08")
def q08(S, a):  # latest comments replying to my posts
    out = []
    for m, _ in S.posts_by(a["person"]):
        out += [(d, c) for c, d in S.replies(m)]
    return sorted(out, reverse=True)[:20]


@q("Q09")
def q09(S, a):  # recent messages by friends-of-friends before a date
    out = []
    for v in _fof(S, a["person"]):
        out += [(d, m) for m, d in S.posts_by(v) + S.comments_by(v) if d < a["d1"]]
    return sorted(out, reverse=True)[:20]


@q("Q10")
def q10(S, a):  # friends with birthday in a month, scored by common interests
    mine = Counter()
    for m, _ in S.posts_by(a["person"]):
        mine.update(S.tag_names(m))
    out = []
    for v, _ in S.friends(a["person"]):
        if S.person_props(v)["birthdayMonth"] == a["month"]:
            theirs = Counter()
            for m, _ in S.posts_by(v):
                theirs.update(S.tag_names(m))
            out.append((sum((mine & theirs).values()), v))
    return sorted(out, reverse=True)[:10]


@q("Q11")
def q11(S, a):  # friends who work at companies in a country
    out = []
    for v, _ in S.friends(a["person"]):
        for org, cn, y in S.employers(v):
            if cn == a["country"]:
                out.append((v, org, y))
    return sorted(out)


@q("Q12")
def q12(S, a):  # friends who commented on posts about a tag class
    out = Counter()
    for v, _ in S.friends(a["person"]):
        for c, _ in S.comments_by(v):
            parent = S.reply_parent(c)
            for t in S.tag_names(parent):
                if a["tagclass"] in S.tag_class_chain(t):
                    out[v] += 1
                    break
    return sorted(out.items(), key=lambda kv: (-kv[1], kv[0]))[:10]


@q("Q13")
def q13(S, a):  # shortest path length between two persons
    src, dst = a["person"], a["person2"]
    seen, dq = {src: 0}, deque([src])
    while dq:
        u = dq.popleft()
        if u == dst:
            return seen[u]
        for v, _ in S.friends(u):
            if v not in seen:
                seen[v] = seen[u] + 1; dq.append(v)
    return -1


@q("Q14")
def q14(S, a):  # weighted shortest path, weight = 1/(1+replies between the pair), depth-limited
    import heapq
    src, dst = a["person"], a["person2"]
    dist, pq = {src: 0.0}, [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            return round(d, 4)
        if d > dist.get(u, 1e9) or d > 4:
            continue
        for v, _ in S.friends(u):
            w = 1.0 / (1 + sum(1 for c, _ in S.comments_by(v) if S.creator(S.reply_parent(c)) == u))
            nd = d + w
            if nd < dist.get(v, 1e9):
                dist[v] = nd; heapq.heappush(pq, (nd, v))
    return -1


@q("Q15")
def q15(S, a):  # full comment thread of a post
    out, stack = [], [a["post"]]
    while stack:
        m = stack.pop()
        for c, d in S.replies(m):
            out.append(c); stack.append(c)
    return sorted(out)


@q("Q16")
def q16(S, a):  # forum members grouped by country with post counts
    posts_by = Counter(S.creator(m) for m in S.posts_in_forum(a["forum"]))
    c = Counter()
    for u, _ in S.members(a["forum"]):
        c[S.country_name(u)] += posts_by.get(u, 0)
    return sorted(c.items())


@q("Q17")
def q17(S, a):  # tag distribution of posts by an organisation's employees
    c = Counter()
    for u in S.employees(a["org"]):
        for m, _ in S.posts_by(u):
            c.update(S.tag_names(m))
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:10]


@q("Q18")
def q18(S, a):  # posts per month for a tag over a year
    c = Counter()
    for m in S.messages_with_tag(a["tag"]):
        d = S.message_date(m)
        if a["d0"] <= d <= a["d1"]:
            c[d // 100] += 1
    return sorted(c.items())


@q("Q19")
def q19(S, a):  # people in a place and their employers
    return sorted((u, tuple(sorted(o for o, _, _ in S.employers(u)))) for u in S.persons_in_city(a["city"]))


@q("Q20")
def q20(S, a):  # ego network to depth 2 with PPR scores
    from pagerank import PPRMatrix
    p = a["person"]
    nodes = _fof(S, p) | {p}
    G = nx.Graph()
    for u in nodes:
        for v, _ in S.friends(u):
            if v in nodes:
                G.add_edge(u, v)
    if p not in G:
        return []
    X, _, _ = PPRMatrix(G, weight=None).run([p], d=0.85)
    order = sorted(zip(X[0], list(G)), reverse=True)[:10]
    return [(n, round(s, 6)) for s, n in order]
