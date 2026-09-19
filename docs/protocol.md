# Systematic literature review protocol

Following Kitchenham & Charters, *Guidelines for performing Systematic Literature Reviews in Software Engineering*, EBSE-2007-01.

## Databases

- OpenAlex (API, title-and-abstract search, computer-science field filter) — run by `python -m ontostudy.slr`; covers ACM, IEEE, Springer and Elsevier metadata
- ACM Digital Library and IEEE Xplore — manual runs of the same strings, to check OpenAlex coverage on a sample
- Google Scholar — forward/backward snowballing from the included set only

The automated run is the primary source so that hit counts and candidate lists are reproducible from the repository. The manual runs are a coverage check, not a second candidate source.

## Search strings

| id | string | scope |
|----|--------|-------|
| S1 | (ontology OR "knowledge graph") AND ("quality metric" OR "quality evaluation" OR "ontology evaluation" OR "quality assessment") | RQ1 |
| S2 | ("ontology engineering" OR "knowledge graph construction" OR "enterprise knowledge graph") AND (industry OR enterprise OR "lessons learned") | RQ2 |
| S3 | ("graph database" OR "graph query" OR SPARQL OR Cypher) AND ("query complexity" OR "schema design" OR "data model" OR normalization) | RQ3 |

Revision note, 2026-09-20: a first run with broader strings over OpenAlex full text returned 260k hits for S1, dominated by bioinformatics papers that mention "ontology" in passing. The strings were narrowed to quoted phrases, the search restricted to title and abstract, and the field filter set to computer science. The strings above are the ones in force.

Every run appends a row to [`search-log.csv`](search-log.csv). Candidate lists, sorted by relevance, are in [`slr/`](slr/) with empty `title_screen`, `abstract_screen`, `grade` and `note` columns to be filled during screening (values: include / exclude / maybe).

## Screening record

| string | hits | candidates | after title screen | after abstract screen |
|--------|------|------------|--------------------|-----------------------|
| S1 | 397 | 300 | 95 | 61 |
| S2 | 225 | 225 | 63 | 39 |
| S3 | 449 | 300 | 68 | 29 |
| snowball (>= 3 links to the included set, 104 with >= 5 screened) | 372 | 104 | 67 | 59 |
| **total** | | 929 | 293 | **188** |

Title and abstract screening were done on 2026-09-20 in one pass by a single screener from the candidate CSVs; decisions and per-row notes are in the `title_screen`, `abstract_screen` and `note` columns. Duplicates across strings were removed at the title stage (marked `duplicate of row n`). Snowballing (`python -m ontostudy.snowball`) fetched references and citing works for the 129 papers included from S1-S3 and ranked unseen works by the number of included papers they are linked to; the 104 with at least 5 links were screened, the remaining 268 with 3-4 links are in the file unscreened.

Known limitation: a single screener. A second screener on a 10% sample with Cohen's kappa is planned before the extraction stage.

## Inclusion criteria

- Peer-reviewed venue, or a primary technical report from the organization that built the system
- Describes an ontology or knowledge graph with at least 10^5 instances, or proposes a quality metric with an evaluation
- English

## Exclusion criteria

- Vendor marketing material
- Position papers without evaluation
- Duplicates and extended versions (keep the most complete one)

## Data extraction form

For each included paper: venue, year, domain, scale (types / instances / links), method, quality metrics used, reported failures, source grade (A peer-reviewed, B technical report, C grey).
