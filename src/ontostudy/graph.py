"""A minimal in-memory property graph with hop counting.

Every schema in `schemas/` builds one of these from the same Dataset. The
graph counts traversals so a query's hop cost can be read off directly, and
`nbytes()` estimates its resident size.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from typing import Any, Hashable, Iterable


class Graph:
    def __init__(self) -> None:
        self.node_type: dict[int, str] = {}
        self.props: dict[int, dict[str, Any]] = {}
        self.out: dict[tuple[int, str], list[tuple[int, dict]]] = defaultdict(list)
        self.inn: dict[tuple[int, str], list[tuple[int, dict]]] = defaultdict(list)
        self.by_type: dict[str, list[int]] = defaultdict(list)
        self.hops = 0          # edge traversals since reset
        self.prop_reads = 0    # property reads since reset
        self.indexes: dict[str, dict] = {}   # secondary indexes a schema chooses to maintain; counted in nbytes

    # --- construction
    def add_node(self, nid: int, ntype: str, **props: Any) -> int:
        self.node_type[nid] = ntype
        self.props[nid] = props
        self.by_type[ntype].append(nid)
        return nid

    def add_edge(self, u: int, label: str, v: int, **props: Any) -> None:
        self.out[(u, label)].append((v, props))
        self.inn[(v, label)].append((u, props))

    # --- traversal (counted)
    def reset(self) -> None:
        self.hops = 0
        self.prop_reads = 0

    def o(self, u: int, label: str) -> list[tuple[int, dict]]:
        r = self.out.get((u, label), ())
        self.hops += len(r) if r else 1
        return list(r)

    def i(self, v: int, label: str) -> list[tuple[int, dict]]:
        r = self.inn.get((v, label), ())
        self.hops += len(r) if r else 1
        return list(r)

    def p(self, n: int, key: str, default: Any = None) -> Any:
        self.prop_reads += 1
        return self.props[n].get(key, default)

    def nodes(self, ntype: str) -> list[int]:
        return self.by_type[ntype]

    # --- size
    def counts(self) -> dict[str, int]:
        return {"nodes": len(self.node_type), "edges": sum(len(v) for v in self.out.values())}

    def nbytes(self) -> int:
        seen: set[int] = set()

        def sz(o: Any) -> int:
            if id(o) in seen:
                return 0
            seen.add(id(o))
            s = sys.getsizeof(o)
            if isinstance(o, dict):
                s += sum(sz(k) + sz(v) for k, v in o.items())
            elif isinstance(o, (list, tuple, set)):
                s += sum(sz(x) for x in o)
            return s

        return sz(self.node_type) + sz(self.props) + sz(self.out) + sz(self.inn) + sz(self.by_type) + sz(self.indexes)
