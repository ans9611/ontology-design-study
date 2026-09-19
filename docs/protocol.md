# Systematic literature review protocol

Following Kitchenham & Charters, *Guidelines for performing Systematic Literature Reviews in Software Engineering*, EBSE-2007-01.

## Databases

- ACM Digital Library
- IEEE Xplore
- Scopus
- Semantic Web Journal (open archive)
- Google Scholar (forward/backward snowballing only)

## Search strings

| id | string | scope |
|----|--------|-------|
| S1 | ("ontology" OR "knowledge graph") AND ("quality" OR "evaluation" OR "metric") | RQ1 |
| S2 | ("ontology engineering" OR "knowledge graph construction") AND ("industry" OR "enterprise" OR "lessons") | RQ2 |
| S3 | ("graph query" OR "SPARQL" OR "Cypher") AND ("complexity" OR "schema design" OR "normalization") | RQ3 |

Record for every run: database, date, string, hit count.

| date | db | string | hits | after title screen | after abstract screen |
|------|----|--------|------|--------------------|-----------------------|
| | | | | | |

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
