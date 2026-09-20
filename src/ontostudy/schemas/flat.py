"""Actionable entities as nodes; place, organisation and tag folded into properties."""

from __future__ import annotations

from .base import Schema
from ..synth import Dataset


class FlatSchema(Schema):
    name = "flat"

    def build(self, D: Dataset) -> None:
        G = self.G
        country = {c["id"]: c["name"] for c in D.countries}
        city = {c["id"]: (c["name"], country[c["countryId"]]) for c in D.cities}
        tagname = {t["id"]: t["name"] for t in D.tags}
        tcname = {tc["id"]: tc for tc in D.tagclasses}
        chain = {}
        for t in D.tags:
            tc, out = tcname[t["tagClass"]], []
            while tc:
                out.append(tc["name"]); tc = tcname.get(tc["parent"]) if tc["parent"] else None
            chain[t["name"]] = out
        self._chain = chain
        org = {o["id"]: (o["name"], country[o["countryId"]]) for o in D.orgs}
        work = {}
        for p, o, y in D.work: work.setdefault(p, []).append((org[o][0], org[o][1], y))
        for p in D.persons:
            cn, co = city[p["cityId"]]
            G.add_node(p["id"], "Person", firstName=p["firstName"], birthdayMonth=p["birthdayMonth"],
                       city=cn, country=co, employers=work.get(p["id"], []))
        for u, v, since in D.knows:
            G.add_edge(u, "knows", v, since=since); G.add_edge(v, "knows", u, since=since)
        for f in D.forums: G.add_node(f["id"], "Forum", moderator=f["moderator"])
        for f, p, jd in D.memberships: G.add_edge(f, "hasMember", p, joinDate=jd)
        for po in D.posts:
            G.add_node(po["id"], "Post", date=po["date"], tags=[tagname[t] for t in po["tags"]])
            G.add_edge(po["id"], "hasCreator", po["creator"]); G.add_edge(po["forum"], "containerOf", po["id"])
        for c in D.comments:
            G.add_node(c["id"], "Comment", date=c["date"], tags=[tagname[t] for t in c["tags"]])
            G.add_edge(c["id"], "hasCreator", c["creator"]); G.add_edge(c["id"], "replyOf", c["replyOf"])
        for p, m, d in D.likes: G.add_edge(p, "likes", m, date=d)

    def _scan(self, ntype):
        ns = self.G.nodes(ntype); self.G.hops += len(ns); return ns

    def friends(self, p): return [(v, e["since"]) for v, e in self.G.o(p, "knows")]
    def city_name(self, p): return self.G.p(p, "city")
    def country_name(self, p): return self.G.p(p, "country")
    def persons_in_city(self, name): return [u for u in self._scan("Person") if self.G.p(u, "city") == name]
    def posts_by(self, p): return [(m, self.G.p(m, "date")) for m, _ in self.G.i(p, "hasCreator") if self.G.node_type[m] == "Post"]
    def comments_by(self, p): return [(m, self.G.p(m, "date")) for m, _ in self.G.i(p, "hasCreator") if self.G.node_type[m] == "Comment"]
    def creator(self, m): return self.G.o(m, "hasCreator")[0][0]
    def tag_names(self, m): return list(self.G.p(m, "tags"))
    def messages_with_tag(self, name):
        return [m for m in self._scan("Post") + self._scan("Comment") if name in self.G.p(m, "tags")]
    def tag_class_chain(self, name): return list(self._chain[name])
    def forums_of(self, p): return [(f, e["joinDate"]) for f, e in self.G.i(p, "hasMember")]
    def members(self, f): return [(u, e["joinDate"]) for u, e in self.G.o(f, "hasMember")]
    def posts_in_forum(self, f): return [m for m, _ in self.G.o(f, "containerOf")]
    def forum_of_post(self, m): return self.G.i(m, "containerOf")[0][0]
    def likers(self, m): return [(u, e["date"]) for u, e in self.G.i(m, "likes")]
    def replies(self, m): return [(c, self.G.p(c, "date")) for c, _ in self.G.i(m, "replyOf")]
    def reply_parent(self, c): return self.G.o(c, "replyOf")[0][0]
    def employers(self, p): return list(self.G.p(p, "employers"))
    def employees(self, name): return [u for u in self._scan("Person") if any(o == name for o, _, _ in self.G.p(u, "employers"))]
    def person_props(self, p): return {"firstName": self.G.p(p, "firstName"), "birthdayMonth": self.G.p(p, "birthdayMonth")}
    def message_date(self, m): return self.G.p(m, "date")
