# Ontology Design Study

How structural design choices in enterprise ontologies (type granularity, link
cardinality, normalization depth) affect query cost and adoption.

## Research questions

- **RQ1 (literature)** What do existing ontology quality metrics measure, and what do they miss?
- **RQ2 (cases)** Which design patterns recur across industry-scale knowledge graphs that succeeded, and across those that were abandoned?
- **RQ3 (experiment)** When the same domain is modeled at three normalization depths, how do query hop count, latency and memory change with scale?

## Method

1. Systematic literature review following Kitchenham & Charters (2007). Protocol in [`docs/protocol.md`](docs/protocol.md).
2. Multiple-case study following Yin (2018) and Runeson & Höst (2009). One template per case in [`docs/cases/`](docs/cases/).
3. Controlled experiment on a public graph benchmark (LDBC SNB). Hypotheses are written down before running anything: [`docs/hypotheses.md`](docs/hypotheses.md).

## Layout

```
docs/
    protocol.md       search strings, databases, inclusion/exclusion criteria
    hypotheses.md     pre-registered hypotheses for RQ3
    cases/            one file per case, same template
references/
    references.bib    verified references only, with DOI
src/ontostudy/
    schemas/          flat / mid / normalized models of the same data
    queries/          the 20 benchmark questions, one version per schema
    loader.py         LDBC SNB loader
    bench.py          hop count, latency, memory per query and scale factor
notebooks/
tests/
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

The centrality analysis reuses the `pagerank` package from
[PageRank_Empirical_Analysis](https://github.com/ans9611/PageRank_Empirical_Analysis).

## Status

- [ ] Week 1-2: protocol, screening, metric matrix
- [ ] Week 3-5: eight cases coded
- [ ] Week 6-8: pipeline, three schemas, twenty queries
- [ ] Week 9-10: runs and statistics
- [ ] Week 11-12: write-up, triangulation
