# Schema assessment against Neo4j modeling guidance

The three RQ3 schemas (`src/ontostudy/schemas/`) reviewed against the practitioner rules in Neo4j's modeling skill (`neo4j-contrib/neo4j-skills@neo4j-modeling-skill`, 2026), which condenses the Neo4j data-modeling guide and field heuristics. The purpose is not to fix the schemas, which were built deliberately to span the design space, but to check whether a practitioner checklist written without measurement predicts the measured results in [results/RESULTS.md](results/RESULTS.md). Each finding notes what the checklist says, what the benchmark measured, and whether they agree.

Provenance: `[official]` is stated in Neo4j documentation, `[field]` is a community heuristic, `[measured]` is this repository's benchmark at 10,000 persons.

## Compliant, all three schemas

- Domain labels only (`Person`, `Post`, `Tag`, ...); no `:Entity` / `:Thing`.
- Relationship direction carries meaning (`hasCreator` from message to person, `replyOf` from comment to parent).
- No embeddings or blobs on business nodes.
- Every schema answers all twenty questions with identical results (540 checks).

## flat

### Entry-point entities stored as properties — WARNING

- **Current**: `city`, `country`, `employers` are properties on `Person`; `tags` is a list property on `Post` and `Comment`. There are no `City`, `Organisation` or `Tag` nodes.
- **Checklist**: "Is it a thing with identity, queried as entry point? → Node" `[official]`. A property is right only when it is "always returned with its parent, never filtered alone". Q17 (employees of an organisation), Q18 (messages with a tag) and Q19 (people in a city) filter on exactly these values.
- **Measured**: with no index, flat scans every `Person` or every message: 3×, 768× and 26× the hops of mid, latency slope 0.8–1.1 against about 0 for mid. Agrees.
- **Fix the checklist prescribes**: either promote to nodes (which is the mid schema) or `CREATE INDEX person_city_idx FOR (p:Person) ON (p.city)` and a fulltext or list index for `tags`. RESULTS lists the indexed variant of flat as the next experiment; the checklist arrives at the same variant from the other direction.

### Junction modelled as a bare property — WARNING

- **Current**: `employers` is a list of `(orgName, countryName, year)` tuples on `Person`.
- **Checklist**: "Junction table modeled as bare property: loses history and extensibility" `[field]`; a many-to-many with its own columns becomes an intermediate node or a propertied relationship.
- **Measured**: the forward read (Q11, friends working in a country) is 4× cheaper than mid because the country is denormalized into the tuple; the reverse read (Q17) is 3× more expensive. Agrees on both sides: the checklist's warning is about the reverse direction and extensibility, and says nothing against the forward gain.

### Low-cardinality value as a property — compliant

- **Current**: `country` (25 values) on `Person`.
- **Checklist**: low-cardinality values used as filters belong on the node (as a label or property), not as a separate node with millions of edges `[official]`.
- **Measured**: Q02 (friends of friends in the same country) costs 175 hops on flat against 503 on mid, because mid walks `Person → City → Country` per candidate. Agrees, and this is the one place where the checklist would move mid toward flat.

## mid

### Country as a node — INFO

- **Current**: `Country` nodes (25) reached through `City -[isPartOf]-> Country`.
- **Checklist**: a 25-value categorical used as a filter is a label or property candidate `[field]`. In this synthetic data each `Country` has degree 8, so it is not a supernode; in real data a country node fed directly by persons would be.
- **Measured**: the extra hop shows up in Q02 (503 vs 175) and Q11 (38 vs 9). Agrees in direction; the size of the effect is small because the fan-in is small.

### One relationship type reused across label pairs — INFO

- **Current**: `isLocatedIn` connects both `Person → City` and `Organisation → Country`; `persons_in_city` filters `node_type == "Person"` after traversal.
- **Checklist**: split by role when a relationship type serves several source labels, so a traversal does not have to filter `[field]`.
- **Measured**: no cost here because nothing else points into `City`. Not testable on this data.

### Propertied relationships kept as direct edges — compliant

- **Current**: `knows {since}`, `workAt {year}`, `hasMember {joinDate}`, `likes {date}` are edges with one property each.
- **Checklist**: promote to an intermediate node only when the relationship has more than two properties, is itself queried, or joins more than two entities `[field]`. None of the four meets that bar.
- **Measured**: mid is within 20% of the best schema on 12 of 20 queries and never the worst. Agrees.

## normalized

### Every relation reified, including those with no properties — WARNING

- **Current**: `PartOf`, `Subclass`, `TagType`, `Authorship`, `Containment`, `Tagging`, `Reply` are intermediate nodes with no properties of their own; `Knows`, `Employment`, `Membership`, `Like` carry one property each.
- **Checklist**: "Junction table (no own columns) → direct relationship; upgrade to intermediate node later" `[official]`. The intermediate-node pattern is reserved for relationships with more than two properties, independent queryability, or n-ary facts.
- **Measured**: one extra hop per relation on every query: median hop ratio 2.03 to mid, latency 2.3×, memory 2.5× at every scale (H1 supported, H3 refuted as a constant factor). Agrees. The checklist gives the rule; the benchmark gives the price.

### Symmetric relation reified with one undirected edge type — WARNING

- **Current**: `Knows` is a node with four `party` edges (`u → r`, `v → r`, `r → u`, `r → v`), and `friends()` filters `x != p` after traversing.
- **Checklist**: direction should encode meaning; a single generic edge type in both directions forces a filter on every traversal `[official]`.
- **Measured**: Q13 and Q20 have a hop ratio of 3.0 instead of the 2.0 seen elsewhere, which RESULTS attributes to exactly this traversal through a shared label in both directions. Agrees; distinct end types (for example `from` / `to`) would bring those two queries back to 2.0 and is a candidate variant for the next run.

### Generic edge labels on reified relations — INFO

- **Current**: `in` is the target edge of both `Residence` and `OrgLocation`; `party` is used for both ends of `Knows`.
- **Checklist**: no generic relationship types `[official]`.
- **Measured**: no cost in this engine, which keys adjacency on `(node, label)`; in a database that indexes by type across the graph it would widen scans.

## What the checklist cannot see, and what the benchmark cannot see

| | practitioner checklist | this benchmark |
|---|---|---|
| Direction of an effect | yes, for every finding above | yes |
| Size of the effect | no; "supernodes degrade traversal" has no number | yes: 2.03× per reification, 768× for an unindexed reverse lookup |
| Scale dependence | no | yes: slope per query, and the fact that the flat penalty is invisible at 1,000 persons |
| Supernodes | yes, with a detection query and mitigations | **no**: the generator caps fan-in. At 10,000 persons the highest-degree node is a `Person` with 570 edges; `City` and `Organisation` medians are about 100 and 200. A real `City` node would carry millions of edges, and mid's reverse lookups would not stay at slope 0 |
| Constraints and indexes | yes | no; the engine has neither |

The last two rows are additions for the threats section of RESULTS and for the next run: a generator with a heavy-tailed entity fan-in (a few cities holding most persons) and a flat variant with property indexes.

## Bearing on the guidelines

- **G2** (entry-point entities get a node or an index) is what the checklist's node-vs-property table says; the benchmark adds the 3× / 768× / 26× and the slope.
- **G3** (reify only where provenance or qualifiers are needed) is the checklist's intermediate-node threshold; the benchmark adds the 2× / 2.5× constant.
- **G4** (default to mid) corresponds to the checklist's "direct relationship first, upgrade later".
- **G5** (measure at three scales) has no counterpart in the checklist, which is the gap this study exists to fill.
