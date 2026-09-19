# Case: SNOMED CT

| field | value |
|-------|-------|
| Organization | SNOMED International (formerly IHTSDO) |
| Domain | clinical terminology |
| Period | SNOMED CT formed 2002 from SNOMED RT and Clinical Terms Version 3; ongoing |
| Scale | on the order of 350,000 active concepts, over a million descriptions, and relationships in the millions (check the current release notes) |
| Source grade | B for scale and process (official documentation); A for the description-logic and quality literature (collect from S1: Schulz, Cornet, Rector and others) |
| Primary sources | SNOMED International technical implementation guide and release notes; peer-reviewed audits to be added |

## Purpose and users

Coding of clinical records in electronic health record systems; required or recommended by several national health systems.

## Design method

Concepts with a formal definition in a description logic (EL++ profile), with `is_a` and attribute relationships; a classifier computes the inferred hierarchy from stated definitions. Concepts can have multiple parents. Distributed as a release with stated and inferred views.

## Quality control

Classification on every release; editorial guidelines; national extensions maintained separately; an active academic auditing literature identifying modeling errors.

## Known failures or limits

Size and multiple inheritance make it hard for implementers to use directly; most systems use subsets. Historical inconsistencies inherited from merged sources persist. The full ontology's expressivity is limited (EL) precisely to keep classification tractable, which is a documented complexity trade-off.

## Design patterns observed

- `dl-with-classifier`
- `expressivity-capped-for-tractability`
- `subset-for-use`: consumers work with extracts, not the whole
- `merged-source-legacy`

## Relevance to RQ2

Direct evidence for the theme of this study: the description-logic profile was chosen for computational cost, and the ontology is consumed through subsets because the whole is too large to use. Formal rigor and practical usability pull apart at this scale.

## To verify against the source

- Current concept/description/relationship counts with release date
- Add at least two peer-reviewed audits to references.bib
