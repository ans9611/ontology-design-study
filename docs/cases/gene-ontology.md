# Case: Gene Ontology (GO)

| field | value |
|-------|-------|
| Organization | Gene Ontology Consortium |
| Domain | molecular function, biological process, cellular component |
| Period | 1998–present |
| Scale | on the order of 40,000+ terms; annotations in the millions across species (check the latest NAR consortium paper for exact counts) |
| Source grade | A |
| Primary sources | Ashburner et al., Nature Genetics 25(1), 2000 [18]; the annual/biennial Gene Ontology Consortium papers in Nucleic Acids Research (add the most recent to references.bib) |

## Purpose and users

A controlled vocabulary for annotating gene products so that annotations from different organism databases can be compared and computed over (enrichment analysis is the dominant use).

## Design method

Three separate directed acyclic graphs, one per aspect. Terms have definitions, synonyms and `is_a` / `part_of` relations; later, additional relation types and logical definitions in OWL. Term requests go through a public tracker and are reviewed by editors.

## Quality control

Editorial review of every term; automated reasoning over logical definitions to catch inconsistencies; obsoletion with replacement pointers rather than deletion; annotation evidence codes per statement.

## Known failures or limits

Term meaning drifts as biology advances, so annotations made under an earlier definition can become misleading; the consortium handles this with versioning and obsoletion but downstream analyses often ignore versions. Depth and branching of the DAG vary a lot between areas, which biases enrichment statistics toward well-studied areas (there is a literature on this; collect from the S1 results).

## Design patterns observed

- `editorial-governance`
- `obsolete-not-delete`
- `evidence-per-annotation`
- `dag-not-tree`
- `logical-definitions-for-qc`

## Relevance to RQ2

Longest-lived sustained domain ontology in the set. Shows that a formal, deep ontology can survive when there is a permanent editorial body and one dominant computational use case that keeps the structure honest.

## To verify against the source

- Term and annotation counts with date
- When logical definitions / OWL were introduced
