# Case: Wikidata

| field | value |
|-------|-------|
| Organization | Wikimedia Deutschland / Wikimedia Foundation, community edited |
| Domain | general knowledge |
| Period | 2012–present |
| Scale | on the order of 10^8 items and 10^9 statements at time of writing (check current figures on the Wikidata statistics page and cite the date) |
| Source grade | A |
| Primary sources | Vrandečić & Krötzsch, CACM 57(10), 2014 [16] |

## Purpose and users

Structured data backing for Wikipedia infoboxes and interlanguage links; a public knowledge base queried through SPARQL by researchers, developers and other Wikimedia projects.

## Design method

No formal ontology. Items carry statements; each statement is a property–value pair with optional qualifiers and references. Properties are created by community proposal. The class hierarchy (P31 instance of, P279 subclass of) is itself community data and is not enforced by the software. Ranks (preferred / normal / deprecated) handle conflicting values instead of deleting them.

## Quality control

Property constraints (value type, single value, inverse, format, etc.) are declared on properties and checked continuously by bots and a constraint-report tool; violations are surfaced, not blocked. References are expected per statement. WikiProjects curate domains.

## Known failures or limits

Because the class hierarchy is unenforced data, it contains cycles and inconsistent subclass chains; several published audits of P279 exist and should be cited from the S1 results. Query cost on the public SPARQL endpoint is bounded by a timeout, which shapes what questions people can ask; deep property paths regularly time out.

## Design patterns observed

- `constraint-based-qc`: quality as continuously checked soft constraints, not schema enforcement
- `n-ary-via-qualifiers`: qualifiers on a statement instead of reified nodes
- `provenance-per-statement`
- `community-schema`: the schema is editable data
- `ranked-conflicts`: contradictory values kept with ranks

## Relevance to RQ2

The counter-example to top-down ontology engineering: no formal ontology, yet sustained at the largest open scale. The comparison with Freebase on the n-ary modeling choice (qualifiers vs. CVTs) is a direct structural contrast between a sustained and an abandoned system.

## To verify against the source

- Current item/statement counts with date
- Which constraint types existed in 2014 vs. now
