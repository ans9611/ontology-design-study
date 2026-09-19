# Case: Cyc

| field | value |
|-------|-------|
| Organization | MCC (1984), then Cycorp (1994–) |
| Domain | common-sense knowledge |
| Period | 1984–present; OpenCyc released 2002, discontinued 2017 |
| Scale | reported in the millions of assertions and hundreds of thousands of concepts (figures vary by year and source; take them from [19] and Cycorp's own statements, graded B) |
| Source grade | A for [19]; B/C for later scale figures |
| Primary sources | Lenat, CACM 38(11), 1995 [19] |

## Purpose and users

A hand-built knowledge base of common-sense facts and rules with an inference engine, intended as infrastructure for many applications.

## Design method

Expert knowledge engineers writing assertions in CycL, a higher-order logic, organized into microtheories (contexts) to manage inconsistency. Top-down: a large upper ontology first, applications later.

## Quality control

Internal review by knowledge engineers; consistency within microtheories; inference used to detect contradictions.

## Known failures or limits

Limited adoption relative to the investment. Commonly cited reasons in the secondary literature: high cost of expert entry, expressivity that made inference expensive and results hard to predict, and an upper ontology that applications did not need. OpenCyc, the open subset, was discontinued. These reasons must be sourced from peer-reviewed retrospectives, not repeated from folklore; collect from S2.

## Design patterns observed

- `expert-entry-only`
- `upper-ontology-first`
- `high-expressivity`
- `context-partitioning` (microtheories)

## Relevance to RQ2

The limited-adoption case with the highest formal rigor. Together with Schema.org it brackets the expressivity-adoption axis; together with SNOMED it shows what happens when expressivity is not capped.

## To verify against the source

- All scale figures
- A peer-reviewed retrospective on Cyc's adoption to cite instead of secondary claims
