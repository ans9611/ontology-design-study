"""Every relation reified as a node carrying the relation's properties."""

from __future__ import annotations

from .base import Schema
from ..synth import Dataset


class NormalizedSchema(Schema):
    name = "normalized"

    def build(self, D: Dataset) -> None:
        G = self.G
        self._n = max(max(c["id"] for c in D.comments), max(t["id"] for t in D.tags), D.persons[-1]["id"]) + 1

        def rel(rtype, src, slabel, dst, dlabel, **props):
            r = self._n; self._n += 1
            G.add_node(r, rtype, **props); G.add_edge(src, slabel, r); G.add_edge(r, dlabel, dst)

        for c in D.countries: G.add_node(c["id"], "Country", name=c["name"])
        for c in D.cities:
            G.add_node(c["id"], "City", name=c["name"]); rel("PartOf", c["id"], "part", c["countryId"], "of")
        for tc in D.tagclasses:
            G.add_node(tc["id"], "TagClass", name=tc["name"])
            if tc["parent"]: rel("Subclass", tc["id"], "sub", tc["parent"], "super")
        for t in D.tags:
            G.add_node(t["id"], "Tag", name=t["name"]); rel("TagType", t["id"], "typed", t["tagClass"], "type")
        for o in D.orgs:
            G.add_node(o["id"], "Organisation", name=o["name"], kind=o["kind"]); rel("OrgLocation", o["id"], "located", o["countryId"], "in")
        for p in D.persons:
            G.add_node(p["id"], "Person", firstName=p["firstName"], birthdayMonth=p["birthdayMonth"])
            rel("Residence", p["id"], "resides", p["cityId"], "in")
        for u, v, since in D.knows:
            r = self._n; self._n += 1
            G.add_node(r, "Knows", since=since)
            G.add_edge(u, "party", r); G.add_edge(v, "party", r); G.add_edge(r, "party", u); G.add_edge(r, "party", v)
        for p, o, y in D.work: rel("Employment", p, "employed", o, "employer", year=y)
        for f in D.forums: G.add_node(f["id"], "Forum", moderator=f["moderator"])
        for f, p, jd in D.memberships: rel("Membership", f, "membership", p, "member", joinDate=jd)
        for po in D.posts:
            G.add_node(po["id"], "Post", date=po["date"])
            rel("Authorship", po["id"], "authored", po["creator"], "author")
            rel("Containment", po["forum"], "contains", po["id"], "content")
            for t in po["tags"]: rel("Tagging", po["id"], "tagging", t, "tag")
        for c in D.comments:
            G.add_node(c["id"], "Comment", date=c["date"])
            rel("Authorship", c["id"], "authored", c["creator"], "author")
            rel("Reply", c["id"], "reply", c["replyOf"], "parent")
            for t in c["tags"]: rel("Tagging", c["id"], "tagging", t, "tag")
        for p, m, d in D.likes: rel("Like", p, "liking", m, "liked", date=d)
        self._tag_by_name = {G.props[t]["name"]: t for t in G.nodes("Tag")}
        self._city_by_name = {G.props[c]["name"]: c for c in G.nodes("City")}
        self._org_by_name = {G.props[o]["name"]: o for o in G.nodes("Organisation")}

    def _via(self, n, l1, l2):
        out = []
        for r, _ in self.G.o(n, l1):
            for x, _ in self.G.o(r, l2):
                out.append((x, r))
        return out

    def _via_in(self, n, l1, l2):
        out = []
        for r, _ in self.G.i(n, l1):
            for x, _ in self.G.i(r, l2):
                out.append((x, r))
        return out

    def friends(self, p):
        out = []
        for r, _ in self.G.o(p, "party"):
            for x, _ in self.G.o(r, "party"):
                if x != p: out.append((x, self.G.p(r, "since")))
        return out
    def _city(self, p): return self._via(p, "resides", "in")[0][0]
    def city_name(self, p): return self.G.p(self._city(p), "name")
    def country_name(self, p): return self.G.p(self._via(self._city(p), "part", "of")[0][0], "name")
    def persons_in_city(self, name): return [u for u, _ in self._via_in(self._city_by_name[name], "in", "resides")]
    def posts_by(self, p): return [(m, self.G.p(m, "date")) for m, _ in self._via_in(p, "author", "authored") if self.G.node_type[m] == "Post"]
    def comments_by(self, p): return [(m, self.G.p(m, "date")) for m, _ in self._via_in(p, "author", "authored") if self.G.node_type[m] == "Comment"]
    def creator(self, m): return self._via(m, "authored", "author")[0][0]
    def tag_names(self, m): return [self.G.p(t, "name") for t, _ in self._via(m, "tagging", "tag")]
    def messages_with_tag(self, name): return [m for m, _ in self._via_in(self._tag_by_name[name], "tag", "tagging")]
    def tag_class_chain(self, name):
        tc = self._via(self._tag_by_name[name], "typed", "type")[0][0]; out = []
        while tc:
            out.append(self.G.p(tc, "name")); up = self._via(tc, "sub", "super"); tc = up[0][0] if up else None
        return out
    def forums_of(self, p): return [(f, self.G.p(r, "joinDate")) for f, r in self._via_in(p, "member", "membership")]
    def members(self, f): return [(u, self.G.p(r, "joinDate")) for u, r in self._via(f, "membership", "member")]
    def posts_in_forum(self, f): return [m for m, _ in self._via(f, "contains", "content")]
    def forum_of_post(self, m): return self._via_in(m, "content", "contains")[0][0]
    def likers(self, m): return [(u, self.G.p(r, "date")) for u, r in self._via_in(m, "liked", "liking")]
    def replies(self, m): return [(c, self.G.p(c, "date")) for c, _ in self._via_in(m, "parent", "reply")]
    def reply_parent(self, c): return self._via(c, "reply", "parent")[0][0]
    def employers(self, p):
        out = []
        for o, r in self._via(p, "employed", "employer"):
            cn = self.G.p(self._via(o, "located", "in")[0][0], "name")
            out.append((self.G.p(o, "name"), cn, self.G.p(r, "year")))
        return out
    def employees(self, name): return [u for u, _ in self._via_in(self._org_by_name[name], "employer", "employed")]
    def person_props(self, p): return {"firstName": self.G.p(p, "firstName"), "birthdayMonth": self.G.p(p, "birthdayMonth")}
    def message_date(self, m): return self.G.p(m, "date")
