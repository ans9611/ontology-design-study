# Ontology Design Study

**Structural design choices in enterprise ontologies and their cost: a literature review, multiple-case study, and controlled experiment.**

Yechan Moon · started September 2026 · status: review screened, experiment run, write-up pending

**Interactive summary: <https://ans9611.github.io/ontology-design-study/>** — metric coverage (RQ1), the eight-case pattern table (RQ2) and the benchmark (RQ3) on one page, built from the tables in this repository.

---

## Abstract

Enterprise ontologies and knowledge graphs are built to give an organization one shared vocabulary over data that lives in many systems. The literature on how to build them is mature [1, 2, 3, 4], and there are several proposals for how to measure their quality [5, 6, 7]. What is largely missing is evidence connecting *structural* design decisions, such as how finely types are split, how relations are reified, and how link cardinality is bounded, to what those decisions cost once the ontology is in use: the number of hops a routine question needs, query latency, memory, and, ultimately, whether people adopt the model or route around it.

This study asks that question in three parts. A systematic literature review establishes what current quality metrics measure and what they leave out. A multiple-case study of eight industry-scale knowledge graphs, including two that were abandoned, codes the design patterns that recur in each outcome. A controlled experiment on the LDBC Social Network Benchmark [8] models one dataset at three normalization depths and measures query cost as a function of scale. The three strands are triangulated in the write-up.

## 1. Motivation

Three observations from practice motivate the work.

**The schema fixes the query pattern.** A relation modeled as `Customer → Order → Product` answers "who bought this" in two hops. The same relation normalized through `OrderLine` and `SKU` needs four. With fan-out $f$ per hop, the difference is $f^2$ versus $f^4$ evaluations, and graph query languages already sit at PSPACE-complete in the worst case [9, 10]. Modeling decisions are therefore performance decisions, but they are rarely made with that in mind.

**Ontologies are hard to change after adoption.** Once applications, permissions and reports depend on a type, renaming or splitting it is an organizational migration, not a schema migration. Freebase's transition to Wikidata documents the cost of reconciling two models of the same world [11]. The window in which structural mistakes are cheap to fix is the design phase.

**Cost surfaces only at scale.** A quadratic materialization (every pair of similar customers stored as a link) is invisible with $10^3$ entities and fatal with $10^7$. Small prototypes cannot reveal this, so the evidence has to come from measurement across scale factors, which is what the experiment provides.

## 2. Related work

**Ontology engineering methodologies.** The field's methods descend from Gruber's definition of an ontology as an explicit specification of a conceptualization [1]. Uschold and Gruninger [2] and METHONTOLOGY [3] formalized the lifecycle; Noy and McGuinness [4] gave the widely used practitioner guide; the NeOn methodology [12] extended it to networked, reused ontologies. OntoClean [13] added formal criteria (rigidity, identity, unity) for checking a taxonomy. These methods are about getting the conceptualization right. None of them treats query cost as a design input.

**Quality evaluation.** OntoQA [5] and OQuaRE [6] define structural and schema-level metrics (depth, breadth, relationship richness, cohesion). Vrandečić [7] surveys evaluation approaches and notes that most are structural or gold-standard based. Paulheim [14] reviews refinement methods for knowledge graphs, focusing on completeness and correctness of instances. Across this literature, the operational cost of a design is not a measured quantity; RQ1 checks this systematically.

**Industry-scale knowledge graphs.** Noy et al. [15] compare the knowledge graphs at Google, Microsoft, Facebook, eBay and IBM and report recurring challenges: entity resolution, schema evolution, and the tension between a rich schema and one that people will actually populate. Wikidata [16] is the largest open case and manages quality through property constraints rather than a formal ontology. Schema.org [17] is the clearest example of a deliberately minimal schema achieving broad adoption. The Gene Ontology [18] has survived for over two decades under an explicit governance process. Cyc [19] is the canonical long-running project with limited adoption. Freebase [11] is the canonical shutdown. These form the case set for RQ2. Hogan et al. [20] provide the general survey used as the frame.

**Graph query cost.** Pérez, Arenas and Gutierrez [9] established the complexity of SPARQL; Angles and Gutierrez [10] survey graph data models; Bonifati et al. [21] cover the evaluation of graph queries in depth. The LDBC Social Network Benchmark [8] is the standard workload used for the experiment, chosen because it ships with a scalable generator and a query set designed to stress joins and path traversals.

**Research methods.** The review follows Kitchenham and Charters [22]. The case study follows Yin [23] and the software-engineering adaptation by Runeson and Höst [24].

## 3. Research questions

| | question | strand |
|---|---|---|
| RQ1 | What do existing ontology and knowledge-graph quality metrics measure, and which operational properties do they omit? | literature review |
| RQ2 | Which structural design patterns recur across industry-scale knowledge graphs that were sustained, and across those that were abandoned? | multiple-case study |
| RQ3 | When the same data is modeled at three normalization depths, how do query hop count, latency and memory scale with data size? | controlled experiment |

## 4. Method

### 4.1 Systematic literature review

Protocol in [`docs/protocol.md`](docs/protocol.md): five databases, three search strings mapped to the three research questions, explicit inclusion and exclusion criteria, and a data extraction form. Every search run is logged with date, database, string and hit count. Papers are graded A (peer-reviewed), B (primary technical report from the organization that built the system) or C (grey literature); grade C sources are used as evidence of practice, never of effect.

### 4.2 Multiple-case study

Eight cases, one file each in [`docs/cases/`](docs/cases/), all filled from the same template: organization, domain, period, scale, design method, quality control, known failures, and observed design patterns tagged with a shared code list. Cases were selected for variation in outcome (sustained vs. abandoned), governance (corporate vs. community vs. consortium) and domain (web, commerce, biomedicine, general knowledge). Cross-case analysis follows Yin's pattern-matching logic [23].

| case | outcome | governance | primary source |
|---|---|---|---|
| Google Knowledge Graph and peers | sustained | corporate | [15] |
| Amazon Product Graph | sustained | corporate | Dong, KDD 2018 keynote (grade B) |
| Wikidata | sustained | community | [16] |
| Freebase | abandoned | corporate, then community | [11] |
| Schema.org | sustained | consortium | [17] |
| Gene Ontology | sustained | consortium | [18] |
| SNOMED CT | sustained | consortium | official documentation (grade B) |
| Cyc | limited adoption | corporate | [19] |

### 4.3 Controlled experiment

One dataset, LDBC SNB [8], modeled three ways:

- **flat**: entities with attributes, few link types, no reification
- **mid**: the entities users act on, links only where cardinality is bounded
- **normalized**: every relation reified as its own node

Twenty benchmark questions are fixed before the schemas are written. Each question is expressed once per schema. At six scales (1,000 to 20,000 persons) the harness records static hop count, latency and resident size (same engine, same machine, five runs recorded, minimum reported, log-log slope with standard error). Hypotheses H1–H4 are pre-registered in [`docs/hypotheses.md`](docs/hypotheses.md) and not edited after the first run.

Four follow-up runs, added after the verdicts and reported separately in [`docs/results/RESULTS.md`](docs/results/RESULTS.md), answer the objections a reviewer would raise first: flat with reverse indexes (is the penalty the layout or the missing index?), Zipf fan-in (what does a supernode do?), the six diagnostic queries on a second engine, Kùzu, in Cypher (do the constants transfer?), and a write-path benchmark (what does denormalisation cost when the world changes?). The three RQ3 schemas are also checked against Neo4j's modeling checklist in [`docs/schema-review.md`](docs/schema-review.md).

The centrality analysis reuses `PPRMatrix` from [PageRank_Empirical_Analysis](https://github.com/ans9611/PageRank_Empirical_Analysis), where the same measurement discipline (vary $n$, fit a log-log slope, report the minimum of repeated runs) was developed.

## 5. Expected contributions

1. A metric matrix showing which properties current ontology quality measures cover, with operational cost identified as a gap (RQ1).
2. A coded set of design patterns with their association to sustained versus abandoned outcomes across eight cases (RQ2).
3. Measured scaling exponents for query cost under three normalization depths, with the pre-registered hypotheses confirmed or refuted (RQ3).
4. A reproducible harness: schemas, queries and benchmark code in this repository.
5. Design guidelines for practitioners, each tied to the strand and strength of its evidence ([guidelines](docs/guidelines.md)).

## 6. Threats to validity

- *Construct*: "adoption" is inferred from published accounts, not measured directly. Mitigated by using only grade A and B sources for outcome claims.
- *Internal*: the experiment varies schema depth on one dataset and one engine. Results are about that combination; the write-up will not generalize beyond it without replication.
- *External*: eight cases are a purposive, not random, sample. Patterns are reported as associations, not causes.
- *Reliability*: search strings, extraction forms, schemas, queries and raw timings are all committed here.

## 7. Repository layout

```
docs/
    site/             static site for GitHub Pages; data.json is generated, index.html is hand-written
    guidelines.md     twelve design guidelines, each tied to its evidence and strength
    schema-review.md  the three schemas checked against Neo4j's modeling checklist, finding by finding
    results/          RQ3 results, figures and raw CSVs
    protocol.md       SLR protocol
    search-log.csv    every search run, dated
    slr/              candidate lists per string, with screening columns
    metrics-matrix.md RQ1 working table
    hypotheses.md     pre-registered hypotheses for RQ3
    cases/            one file per case, shared template; CODEBOOK.md for a second coder
references/
    references.bib    references with DOI
src/ontostudy/
    slr.py            OpenAlex search runner for the review protocol
    check_refs.py     Crossref check of references.bib
    synth.py          LDBC-SNB-shaped synthetic data generator
    graph.py          in-memory property graph with a hop counter
    schemas/          flat / mid / normalized builders behind one accessor interface
    queries/          the twenty questions, written once against the interface
    bench.py          hop count, latency, memory per query, schema and scale (--schemas, --skew for the follow-ups)
    writes.py         records touched and time per update, per schema
    engine_kuzu.py    the six diagnostic queries in Cypher on Kùzu, per schema
    report.py         regenerates every table in docs/results/RESULTS.md from the CSVs
    figures.py        regenerates docs/results/fig*.png from the CSVs
    site.py           collects the RQ1/RQ2/RQ3 tables, and each schema as a graph, into docs/site/data.json
notebooks/
tests/
```

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest

python -m ontostudy.slr          # run the protocol's searches against OpenAlex, log hits, write candidates
python -m ontostudy.screen ...   # record screening decisions into a candidate CSV
python -m ontostudy.snowball     # backward/forward snowballing from the included set
python -m ontostudy.check_refs   # verify every DOI in references.bib against Crossref
python -m ontostudy.bench        # RQ3 main run: three schemas x twenty queries x six scales
python -m ontostudy.bench --schemas flat flat_indexed mid --out docs/results/bench_indexed.csv
python -m ontostudy.bench --skew 1 --schemas flat flat_indexed mid normalized --out docs/results/bench_skew.csv
python -m ontostudy.writes       # write path
pip install -e ".[engine]" && python -m ontostudy.engine_kuzu   # second engine
python -m ontostudy.report       # regenerate the tables in RESULTS.md
python -m ontostudy.figures      # regenerate the figures
python -m ontostudy.site         # rebuild docs/site/data.json after any table changes
```

## 8. Timeline

| weeks | deliverable | status |
|---|---|---|
| 1–2 | search log, screening, metric matrix | done: 929 candidates screened, 188 included ([protocol](docs/protocol.md), [matrix](docs/metrics-matrix.md)) |
| 3–5 | eight case files, cross-case pattern table | drafted, figures to verify against sources ([cases](docs/cases/)) |
| 6–8 | generator, three schemas, twenty queries, harness | done ([src](src/ontostudy/)) |
| 9–10 | runs at six scales, statistics, four follow-up runs | done: [results](docs/results/RESULTS.md) |
| 11–12 | write-up, triangulation | pending; data extraction from the 188 included papers is the next step |

## References

[1] T. R. Gruber. A translation approach to portable ontology specifications. *Knowledge Acquisition*, 5(2):199–220, 1993. doi:10.1006/knac.1993.1008

[2] M. Uschold and M. Gruninger. Ontologies: principles, methods and applications. *The Knowledge Engineering Review*, 11(2):93–136, 1996. doi:10.1017/S0269888900007797

[3] M. Fernández-López, A. Gómez-Pérez, and N. Juristo. METHONTOLOGY: From ontological art towards ontological engineering. *AAAI Spring Symposium on Ontological Engineering*, 1997.

[4] N. F. Noy and D. L. McGuinness. Ontology Development 101: A guide to creating your first ontology. Stanford KSL Technical Report KSL-01-05, 2001.

[5] S. Tartir, I. B. Arpinar, M. Moore, A. P. Sheth, and B. Aleman-Meza. OntoQA: Metric-based ontology quality analysis. *IEEE Workshop on Knowledge Acquisition from Distributed, Autonomous, Semantically Heterogeneous Data and Knowledge Sources*, 2005.

[6] A. Duque-Ramos, J. T. Fernández-Breis, R. Stevens, and N. Aussenac-Gilles. OQuaRE: A SQuaRE-based approach for evaluating the quality of ontologies. *Journal of Research and Practice in Information Technology*, 43(2):159–176, 2011.

[7] D. Vrandečić. Ontology evaluation. In S. Staab and R. Studer (eds.), *Handbook on Ontologies*, 2nd ed., Springer, 2009. doi:10.1007/978-3-540-92673-3_13

[8] O. Erling et al. The LDBC Social Network Benchmark: Interactive workload. *Proc. ACM SIGMOD*, 619–630, 2015. doi:10.1145/2723372.2742786

[9] J. Pérez, M. Arenas, and C. Gutierrez. Semantics and complexity of SPARQL. *ACM Transactions on Database Systems*, 34(3):1–45, 2009. doi:10.1145/1567274.1567278

[10] R. Angles and C. Gutierrez. Survey of graph database models. *ACM Computing Surveys*, 40(1):1–39, 2008. doi:10.1145/1322432.1322433

[11] T. Pellissier Tanon, D. Vrandečić, S. Schaffert, T. Steiner, and L. Pintscher. From Freebase to Wikidata: The great migration. *Proc. WWW*, 1419–1428, 2016. doi:10.1145/2872427.2874809

[12] M. C. Suárez-Figueroa, A. Gómez-Pérez, E. Motta, and A. Gangemi (eds.). *Ontology Engineering in a Networked World*. Springer, 2012. doi:10.1007/978-3-642-24794-1

[13] N. Guarino and C. A. Welty. An overview of OntoClean. In *Handbook on Ontologies*, Springer, 151–171, 2004. doi:10.1007/978-3-540-24750-0_8

[14] H. Paulheim. Knowledge graph refinement: A survey of approaches and evaluation methods. *Semantic Web*, 8(3):489–508, 2017. doi:10.3233/SW-160218

[15] N. Noy, Y. Gao, A. Jain, A. Narayanan, A. Patterson, and J. Taylor. Industry-scale knowledge graphs: Lessons and challenges. *Communications of the ACM*, 62(8):36–43, 2019. doi:10.1145/3331166

[16] D. Vrandečić and M. Krötzsch. Wikidata: A free collaborative knowledgebase. *Communications of the ACM*, 57(10):78–85, 2014. doi:10.1145/2629489

[17] R. V. Guha, D. Brickley, and S. Macbeth. Schema.org: Evolution of structured data on the web. *Communications of the ACM*, 59(2):44–51, 2016. doi:10.1145/2844544

[18] M. Ashburner et al. Gene Ontology: Tool for the unification of biology. *Nature Genetics*, 25(1):25–29, 2000. doi:10.1038/75556

[19] D. B. Lenat. CYC: A large-scale investment in knowledge infrastructure. *Communications of the ACM*, 38(11):33–38, 1995. doi:10.1145/219717.219745

[20] A. Hogan et al. Knowledge graphs. *ACM Computing Surveys*, 54(4):1–37, 2021. doi:10.1145/3447772

[21] A. Bonifati, G. Fletcher, H. Voigt, and N. Yakovets. *Querying Graphs*. Morgan & Claypool, 2018. doi:10.2200/S00873ED1V01Y201808DTM051

[22] B. Kitchenham and S. Charters. Guidelines for performing systematic literature reviews in software engineering. EBSE Technical Report EBSE-2007-01, 2007.

[23] R. K. Yin. *Case Study Research and Applications: Design and Methods*, 6th ed. SAGE, 2018.

[24] P. Runeson and M. Höst. Guidelines for conducting and reporting case study research in software engineering. *Empirical Software Engineering*, 14(2):131–164, 2009. doi:10.1007/s10664-008-9102-8
