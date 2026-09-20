"""Three models of the same Dataset, exposed through one accessor interface.

flat        the entities users act on (Person, Post, Comment, Forum) are
            nodes; place, organisation and tag are string properties copied
            onto them. Reverse lookups on those (who lives in X, who works at
            Y, posts tagged Z) have no index and scan.
mid         every entity is a node, every relation a direct edge with
            properties. This is the LDBC SNB model as published.
normalized  every relation is reified as its own node with the relation's
            properties, so a traversal is always two hops.

VARIANTS holds follow-up schemas that are not part of the main run:
flat_indexed   flat with reverse indexes on city, employer and tag.

Queries in `ontostudy.queries` are written once against `Schema`; the schema
decides how many hops each accessor costs.
"""

from .base import Schema
from .flat import FlatSchema
from .mid import MidSchema
from .normalized import NormalizedSchema
from .flat_indexed import FlatIndexedSchema

SCHEMAS = {"flat": FlatSchema, "mid": MidSchema, "normalized": NormalizedSchema}
VARIANTS = {"flat_indexed": FlatIndexedSchema}

__all__ = ["Schema", "FlatSchema", "MidSchema", "NormalizedSchema", "FlatIndexedSchema", "SCHEMAS", "VARIANTS"]
