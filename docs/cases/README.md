# Cross-case pattern table

Filled as cases are verified. A cell is 1 if the pattern is observed in that case.

| pattern | google-kg | amazon | wikidata | freebase | schema-org | gene-ontology | snomed-ct | cyc |
|---|---|---|---|---|---|---|---|---|
| action-first | 1 | | | | 1 | | | |
| entity-resolution-core | 1 | | | | | | | |
| provenance-per-statement | 1 | | 1 | | | 1 | | |
| provenance-weak | | | | 1 | | | | |
| constraint-based-qc | | | 1 | | | | | |
| editorial-governance | 1 | | | | | 1 | 1 | 1 |
| community-schema | | | 1 | | 1 | | | |
| minimal-schema | | | | | 1 | | | |
| n-ary-via-reification | | | | 1 | | | | |
| n-ary-via-qualifiers | | | 1 | | | | | |
| dl-with-classifier | | | | | | 1 | 1 | |
| expressivity-capped-for-tractability | | | | | | | 1 | |
| high-expressivity | | | | | | | | 1 |
| upper-ontology-first | | | | | | | | 1 |
| schema-discovered-not-designed | | 1 | | | | | | |
| subset-for-use | | | | | | | 1 | |
| platform-dependency | | | | 1 | | | | |
| obsolete-not-delete | | | | | | 1 | | |

| outcome | sustained | sustained (internal) | sustained | abandoned | sustained | sustained | sustained | limited adoption |
|---|---|---|---|---|---|---|---|---|

Read column-wise for what each case does; read row-wise, against the outcome row, for RQ2.
