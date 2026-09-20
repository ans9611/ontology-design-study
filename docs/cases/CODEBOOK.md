# Codebook for the cross-case pattern table

Purpose: let a second coder fill [README.md](README.md) independently from the primary sources, so that agreement (Cohen's κ per code, target ≥ 0.7) can be reported. The first coding was done by one person; until a second coding exists, the table is a single-coder draft and RQ2 findings are reported as such.

## Coding rules

1. Code from the primary source named in the case file's header, not from the case file's prose. Grade C sources may support a code only when no A/B source contradicts it.
2. A code is 1 when the source describes the practice as characteristic of the system, not as an experiment or a proposal. Absence of mention is 0, not missing.
3. Code the system as it was in the period the source describes. Freebase is coded as of [11]; Wikidata as of [16].
4. One code per row; synonyms in the "also written as" column are folded into the canonical code.
5. Record a one-line quote or page reference for every 1 in `docs/cases/<case>.md` under "Design patterns observed".

## Canonical codes

| code | definition (code 1 when the source says…) | also written as |
|---|---|---|
| `action-first` | the schema is organised around what applications do with entities, rather than around a general taxonomy | `single-consumer-purpose` |
| `entity-resolution-core` | identity across sources is treated as the central engineering problem, with dedicated infrastructure | |
| `provenance-per-statement` | every statement (fact, annotation) carries a source or evidence record as a first-class element | `provenance-per-fact`, `evidence-per-annotation` |
| `provenance-weak` | sourcing per statement is optional or unstructured | |
| `constraint-based-qc` | quality is checked by declared constraints that run continuously and report violations without blocking writes | `logical-definitions-for-qc` (when the reasoner is used to flag, not to block) |
| `editorial-governance` | a named editorial body reviews changes to the schema or vocabulary before release | `central-schema-team` |
| `community-schema` | the schema itself is editable data, changed by community proposal | |
| `minimal-schema` | the schema is deliberately shallow and permissive, trading precision for uptake | `tolerant-consumption` when it refers to the schema side |
| `n-ary-via-reification` | n-ary relations are stored as their own nodes (compound value types, relation nodes) | |
| `n-ary-via-qualifiers` | n-ary relations are stored as qualifiers attached to a binary statement | |
| `dl-with-classifier` | concepts have formal description-logic definitions and a classifier computes the hierarchy | |
| `expressivity-capped-for-tractability` | the logic is restricted (for example to EL) explicitly to keep reasoning tractable | |
| `high-expressivity` | the representation language is more expressive than first-order or description logic, by design | |
| `upper-ontology-first` | development started from a general upper ontology before any application | |
| `schema-discovered-not-designed` | types and attributes are learned from data rather than designed in advance | |
| `subset-for-use` | consumers are expected to work with extracts rather than the whole | |
| `platform-dependency` | the system's continuation depended on a single sponsor or platform | |
| `obsolete-not-delete` | retired terms are kept with a replacement pointer rather than removed | |

## Codes used in case files but not yet in the table

These appear in individual case files and need a decision before the second coding: promote to the table with a definition, fold into a canonical code, or drop.

`serving-feedback-qc`, `ranked-conflicts`, `usage-driven-extension`, `multi-type-entities`, `merged-source-legacy`, `long-tail-attributes`, `extraction-quality-as-graph-quality`, `expert-entry-only`, `dag-not-tree`, `context-partitioning`.

## Outcome coding

| outcome | rule |
|---|---|
| sustained | in production use and maintained at the time of the most recent A/B source |
| sustained (internal) | as above, but only internal use is documented (no public artefact) |
| limited adoption | maintained, but the sources describe adoption as small relative to the investment |
| abandoned | shut down or migrated away, documented in an A/B source |

Outcome is coded from a different source than the patterns where possible, so that the same passage does not supply both.

## A measurable outcome, for later

"Sustained / abandoned" is coded from published accounts and is confounded by sponsorship and by what gets published. An observable proxy exists for most cases: schema churn, the number of types or properties added and deprecated per year, readable from Wikidata's property-proposal archive, Schema.org's release notes and GitHub issues, Gene Ontology and SNOMED CT release notes, and the Freebase schema history. Coding churn for the eight cases would give RQ2 a dependent variable that is a number rather than a label; it has not been done.
