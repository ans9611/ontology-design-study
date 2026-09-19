# Case: Google Knowledge Graph and peers (Microsoft, Facebook, eBay, IBM)

| field | value |
|-------|-------|
| Organization | Google, Microsoft (Bing / Satori), Facebook, eBay, IBM (Watson Discovery) |
| Domain | general knowledge, product, social, enterprise documents |
| Period | Google KG launched 2012; the account is from 2019 |
| Scale | Google: on the order of billions of entities and tens of billions of facts (order-of-magnitude figures as given in the paper; check exact numbers against [15]) |
| Source grade | A |
| Primary sources | Noy et al., CACM 62(8), 2019 [15] |

## Purpose and users

Search and question answering (Google, Microsoft), product search and recommendation (eBay), social graph and entity linking (Facebook), enterprise document understanding (IBM). In every case the graph serves applications; it is not maintained as an end in itself.

## Design method

Varies by company. Common elements reported: a schema maintained by a central team; entities sourced from structured feeds, extraction, and human curation in different proportions; a strong emphasis on identifiers and entity resolution across sources. Facebook and eBay describe schemas built around the entities their products act on rather than around a general taxonomy.

## Quality control

Provenance per fact; human review for high-traffic entities; automated consistency checks; feedback loops from the serving application (search clicks, user reports).

## Known failures or limits

The paper lists open challenges rather than failures: disambiguation and entity resolution at scale, keeping the schema in step with new entity types, managing multiple conflicting sources, and making the graph usable by teams that did not build it. It notes explicitly that a schema is only as useful as what people actually populate.

## Design patterns observed

- `action-first`: schemas built around what applications do with entities (eBay, Facebook)
- `entity-resolution-core`: identity across sources treated as the central engineering problem
- `provenance-per-fact`
- `central-schema-team`
- `serving-feedback-qc`: quality signals come from the application, not from the ontology tooling

## Relevance to RQ2

Five sustained corporate graphs with the same short list of hard problems, none of which is taxonomy depth. Supports the hypothesis that population and evolution dominate over structural richness. The paper gives little on query cost, which is a gap RQ3 addresses.

## To verify against the source

- Exact scale figures per company
- Which companies describe their schema process in enough detail to code `central-schema-team`
