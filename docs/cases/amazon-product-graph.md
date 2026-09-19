# Case: Amazon Product Graph

| field | value |
|-------|-------|
| Organization | Amazon |
| Domain | products, attributes, brands, categories |
| Period | account from 2018 |
| Scale | not published precisely; described as billions of products across thousands of categories |
| Source grade | B (keynote abstract and slides; no peer-reviewed system paper) |
| Primary sources | X. L. Dong, "Challenges and innovations in building a product knowledge graph," KDD 2018 keynote; related peer-reviewed papers on attribute extraction from the same group (collect from S2) |

## Purpose and users

Product search, question answering, recommendation. Internal.

## Design method

Described as bottom-up: the schema (which attributes matter for which product type) cannot be designed in advance because product types and attributes change continuously; attributes and their values are extracted from product text and then organized. Schema discovery is treated as a learning problem.

## Quality control

Extraction precision measured against human labels; the account emphasizes that the graph is only as good as extraction quality.

## Known failures or limits

The keynote frames the difficulty as: no fixed schema, extreme heterogeneity, and the cost of keeping extraction accurate. No sustained-vs-abandoned outcome can be assessed from public sources; treat as "sustained, internal".

## Design patterns observed

- `schema-discovered-not-designed`
- `extraction-quality-as-graph-quality`
- `long-tail-attributes`

## Relevance to RQ2

Represents the regime where a fixed ontology is impossible. Useful as a boundary case for what "ontology design" even means; findings from it are grade B and must be reported as such.

## To verify against the source

- Locate the keynote abstract in the KDD 2018 proceedings for a citable entry
- Identify two peer-reviewed papers from the same group to ground the extraction claims
