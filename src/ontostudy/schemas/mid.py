"""Entity nodes and direct labelled edges: the LDBC SNB model."""

from __future__ import annotations

from .base import Schema
from ..synth import Dataset


class MidSchema(Schema):
    name = "mid"

    def build(self, D: Dataset) -> None:
        G = self.G
        for c in D.countries: G.add_node(c["id"], "Country", name=c["name"])
        for c in D.cities:
            G.add_node(c["id"], "City", name=c["name"]); G.add_edge(c["id"], "isPartOf", c["countryId"])
        for tc in D.tagclasses:
            G.add_node(tc["id"], "TagClass", name=tc["name"])
            if tc["parent"]: G.add_edge(tc["id"], "isSubclassOf", tc["parent"])
        for t in D.tags:
            G.add_node(t["id"], "Tag", name=t["name"]); G.add_edge(t["id"], "hasType", t["tagClass"])
        for o in D.orgs:
            G.add_node(o["id"], "Organisation", name=o["name"], kind=o["kind"]); G.add_edge(o["id"], "isLocatedIn", o["countryId"])
        for p in D.persons:
            G.add_node(p["id"], "Person", firstName=p["firstName"], birthdayMonth=p["birthdayMonth"])
            G.add_edge(p["id"], "isLocatedIn", p["cityId"])
        for u, v, since in D.knows:
            G.add_edge(u, "knows", v, since=since); G.add_edge(v, "knows", u, since=since)
        for p, o, y in D.work: G.add_edge(p, "workAt", o, year=y)
        for f in D.forums: G.add_node(f["id"], "Forum", moderator=f["moderator"])
        for f, p, jd in D.memberships: G.add_edge(f, "hasMember", p, joinDate=jd)
        for po in D.posts:
            G.add_node(po["id"], "Post", date=po["date"])
            G.add_edge(po["id"], "hasCreator", po["creator"]); G.add_edge(po["forum"], "containerOf", po["id"])
            for t in po["tags"]: G.add_edge(po["id"], "hasTag", t)
        for c in D.comments:
            G.add_node(c["id"], "Comment", date=c["date"])
            G.add_edge(c["id"], "hasCreator", c["creator"]); G.add_edge(c["id"], "replyOf", c["replyOf"])
            for t in c["tags"]: G.add_edge(c["id"], "hasTag", t)
        for p, m, d in D.likes: G.add_edge(p, "likes", m, date=d)
        self._tag_by_name = {G.props[t]["name"]: t for t in G.nodes("Tag")}
        self._city_by_name = {G.props[c]["name"]: c for c in G.nodes("City")}
        self._org_by_name = {G.props[o]["name"]: o for o in G.nodes("Organisation")}

    G = None  # type: ignore

    def friends(self, p): return [(v, e["since"]) for v, e in self.G.o(p, "knows")]
    def _city(self, p): return self.G.o(p, "isLocatedIn")[0][0]
    def city_name(self, p): return self.G.p(self._city(p), "name")
    def country_name(self, p):
        c = self._city(p); return self.G.p(self.G.o(c, "isPartOf")[0][0], "name")
    def persons_in_city(self, name): return [u for u, _ in self.G.i(self._city_by_name[name], "isLocatedIn") if self.G.node_type[u] == "Person"]
    def posts_by(self, p): return [(m, self.G.p(m, "date")) for m, _ in self.G.i(p, "hasCreator") if self.G.node_type[m] == "Post"]
    def comments_by(self, p): return [(m, self.G.p(m, "date")) for m, _ in self.G.i(p, "hasCreator") if self.G.node_type[m] == "Comment"]
    def creator(self, m): return self.G.o(m, "hasCreator")[0][0]
    def tag_names(self, m): return [self.G.p(t, "name") for t, _ in self.G.o(m, "hasTag")]
    def messages_with_tag(self, name): return [m for m, _ in self.G.i(self._tag_by_name[name], "hasTag")]
    def tag_class_chain(self, name):
        tc = self.G.o(self._tag_by_name[name], "hasType")[0][0]; out = []
        while tc:
            out.append(self.G.p(tc, "name")); up = self.G.o(tc, "isSubclassOf"); tc = up[0][0] if up else None
        return out
    def forums_of(self, p): return [(f, e["joinDate"]) for f, e in self.G.i(p, "hasMember")]
    def members(self, f): return [(u, e["joinDate"]) for u, e in self.G.o(f, "hasMember")]
    def posts_in_forum(self, f): return [m for m, _ in self.G.o(f, "containerOf")]
    def forum_of_post(self, m): return self.G.i(m, "containerOf")[0][0]
    def likers(self, m): return [(u, e["date"]) for u, e in self.G.i(m, "likes")]
    def replies(self, m): return [(c, self.G.p(c, "date")) for c, _ in self.G.i(m, "replyOf")]
    def reply_parent(self, c): return self.G.o(c, "replyOf")[0][0]
    def employers(self, p):
        out = []
        for o, e in self.G.o(p, "workAt"):
            cn = self.G.p(self.G.o(o, "isLocatedIn")[0][0], "name")
            out.append((self.G.p(o, "name"), cn, e["year"]))
        return out
    def employees(self, name): return [u for u, _ in self.G.i(self._org_by_name[name], "workAt")]
    def person_props(self, p): return {"firstName": self.G.p(p, "firstName"), "birthdayMonth": self.G.p(p, "birthdayMonth")}
    def message_date(self, m): return self.G.p(m, "date")
