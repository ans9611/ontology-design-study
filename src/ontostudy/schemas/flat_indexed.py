"""Flat plus reverse indexes on the folded values (city, employer, tag).

Same nodes and properties as flat; the only addition is three dictionaries
built after load, so the memory they cost is visible in sizes.csv. An index
lookup is charged one hop per result, the same as a reverse edge traversal.
"""

from __future__ import annotations

from .flat import FlatSchema
from ..synth import Dataset


class FlatIndexedSchema(FlatSchema):
    name = "flat_indexed"

    def build(self, D: Dataset) -> None:
        super().build(D)
        G = self.G
        by_city, by_org, by_tag = {}, {}, {}
        for u in G.nodes("Person"):
            by_city.setdefault(G.props[u]["city"], []).append(u)
            for o, _, _ in G.props[u]["employers"]:
                by_org.setdefault(o, []).append(u)
        for m in G.nodes("Post") + G.nodes("Comment"):
            for t in G.props[m]["tags"]:
                by_tag.setdefault(t, []).append(m)
        G.indexes = {"city": by_city, "org": by_org, "tag": by_tag}

    def _lookup(self, index, key):
        r = self.G.indexes[index].get(key, [])
        self.G.hops += len(r) if r else 1
        return list(r)

    def persons_in_city(self, name): return self._lookup("city", name)
    def employees(self, name): return self._lookup("org", name)
    def messages_with_tag(self, name): return self._lookup("tag", name)
