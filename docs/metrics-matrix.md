# RQ1: what do existing quality metrics measure?

Draft from the seed papers. Every row is to be re-checked against the paper while screening; add rows as the review proceeds.

Columns are the property groups. A cell says how the framework measures it, or is empty if it does not.

| framework | structural (depth, breadth, richness) | instance completeness / correctness | formal soundness (taxonomy) | usability / fitness for task | **operational cost (hops, latency, memory)** | adoption / maintenance |
|---|---|---|---|---|---|---|
| OntoQA [5] | schema metrics: relationship richness, attribute richness, inheritance richness; knowledge-base metrics: class richness, cohesion | instance distribution across classes ("class connectivity", "class importance") | | | | |
| OQuaRE [6] | structural sub-characteristics mapped onto ISO/IEC 25000 (SQuaRE) | | | functional adequacy, reliability, operability, maintainability, compatibility, transferability, all as SQuaRE characteristics | "performance efficiency" appears as a SQuaRE characteristic but is scored from structural proxies, not measured | maintainability sub-characteristics (modularity, reusability, analysability, changeability) |
| Vrandečić [7] | covers structure as one of several aspects (vocabulary, syntax, structure, semantics, representation, context) | gold-standard and data-driven evaluation | | application-based evaluation: does the ontology work in the application it was built for | | |
| OntoClean [13] | | | rigidity, identity, unity, dependence constraints on the subsumption hierarchy | | | |
| Paulheim [14] | | completeness and correctness of KG instances; refinement methods evaluated by precision/recall | | | | |
| Noy et al. [15] | | entity resolution and provenance as recurring challenges | | schema must be populated to be useful; "the schema is what people will actually fill in" | | schema evolution, governance, tooling named as open challenges |
| Wikidata [16] | | property constraints checked continuously | | | | community process as quality control |

## What this table does not cover: benchmark literature

The table holds *quality-evaluation* frameworks. A separate literature measures query performance over ontologies and RDF stores directly: LUBM [25] (OWL knowledge base systems, a fixed university ontology, queries scaled by number of universities), SP²Bench [26] (SPARQL over a DBLP-shaped dataset), BSBM [27] (an e-commerce use case) and LDBC SNB [8]. All of them measure latency and scale; none varies the ontology's structure as the treatment. The RQ1 claim is therefore not "nobody measures operational cost" but "quality frameworks do not measure it, and benchmarks that do measure it hold the design fixed". Both halves are needed for the gap this study addresses.

## Observations so far

1. Structural metrics are the most developed and the least connected to any outcome. Depth and breadth of a taxonomy are easy to compute; nothing in the seed set relates them to anything a user experiences.
2. OQuaRE names performance efficiency but derives it from structure rather than from measurement. Among quality frameworks this is the closest to RQ3; among benchmarks, LDBC SNB is the closest because its schema is the one RQ3 varies.
3. Application-based evaluation [7] is the only approach that would capture operational cost, and it is the least standardized.
4. Industry accounts [15] treat schema evolution and population as the hard problems. Neither has a metric in the academic frameworks.

## To do

- [ ] Add rows from the S1 search results as they are screened
- [ ] For each framework, note whether any metric has been validated against an outcome (adoption, error rate, query time)
- [ ] Decide the final column set before coding the full set
