# RQ3 results: query cost under three normalization depths

Main run on 2026-09-20: `python -m ontostudy.bench --scales 1000 2000 3000 5000 10000 20000 --repeats 5 --n-args 20`. Raw rows in [bench.csv](bench.csv), sizes in [sizes.csv](sizes.csv). All three schemas returned identical answers for every query and parameter set. Every table in this file is generated from the CSVs by `python -m ontostudy.report`; the prose is written by hand and cites the tables.

Four follow-up runs answer objections to the main run and are reported in their own section below: flat with reverse indexes, heavy-tailed fan-in, a second engine, and the write path. They were run after the hypotheses were registered and are not used to score them.

## Setup

- Data: synthetic LDBC-SNB-shaped graphs (see the dated note in ../hypotheses.md on why not LDBC Datagen). At 10,000 persons: 50k friendships, 39k posts, 78k comments, 175k likes. Entity fan-in is uniform in the main run: about 100 persons per city, 200 per company, 160 messages per tag.
- Schemas: flat (place, organisation, tag folded into properties; no reverse index on them), mid (entity nodes and direct edges; the SNB model), normalized (every relation reified as a node).
- Queries: the twenty in ../../src/ontostudy/queries/QUESTIONS.md, written once against the accessor interface. Twenty parameter sets per query, shared by all schemas; best of five runs, all five recorded.
- Metrics: hops (records touched: edge traversals and index hits, plus one per node for a full scan of a type; the scan part is recorded separately as `scans`), latency (ms per query), resident size (recursive sys.getsizeof), and a log-log latency exponent fitted over the six scales with two standard errors reported. Headline numbers are reported at 10,000 persons, the one scale every run shares, with a 95% bootstrap interval over the twenty queries.
- Machine: Apple M4 Pro, 25.8 GB RAM, macOS, Python 3.9.6, Kùzu 0.11.3, one process, nothing else running during a timed run.

## Headline numbers

<!-- table:headline -->
| | flat | mid | normalized |
|---|---|---|---|
| median hop ratio to mid, n=10,000 [95% CI over queries] | 1.00 [0.62, 1.00] | 1.00 [1.00, 1.00] | 2.03 [2.00, 2.25] |
| median latency ratio to mid, n=10,000 [95% CI] | 0.97 [0.73, 1.01] | 1.00 [1.00, 1.00] | 2.29 [1.95, 2.66] |
| size at n=10,000 | 308 MB | 350 MB | 875 MB |
| build time at n=10,000 | 1.7 s | 3.2 s | 7.6 s |
| queries within 20% of the fastest | 17 | 12 | 0 |
| queries with latency exponent > 0.5 | 5 (Q13, Q14, Q17, Q18, Q19) | 2 (Q13, Q14) | 2 (Q13, Q14) |
<!-- /table -->

![hops](fig1_hops.png)

![scaling](fig2_scaling.png)

![memory](fig3_memory.png)

## Per-query table, reference scale 10,000

<!-- table:per-query -->
exp = slope of log(latency) against log(persons) over 1,000 / 2,000 / 3,000 / 5,000 / 10,000 / 20,000; ± is two standard errors of the fit.

| query | hops flat | hops mid | hops normalized | ms flat | ms mid | ms normalized | exp flat | exp mid | exp normalized |
|---|---|---|---|---|---|---|---|---|---|
| Q01 | 9 | 19 | 47 | 0.006 | 0.008 | 0.015 | 0.00 ± 0.09 | 0.01 ± 0.09 | 0.02 ± 0.10 |
| Q02 | 175 | 503 | 1,182 | 0.054 | 0.124 | 0.296 | 0.13 ± 0.07 | 0.13 ± 0.06 | 0.12 ± 0.07 |
| Q03 | 143 | 143 | 297 | 0.027 | 0.027 | 0.068 | 0.08 ± 0.08 | 0.08 ± 0.08 | 0.06 ± 0.08 |
| Q04 | 143 | 179 | 369 | 0.039 | 0.048 | 0.101 | 0.09 ± 0.08 | 0.10 ± 0.08 | 0.08 ± 0.08 |
| Q05 | 1,152 | 1,152 | 2,315 | 0.166 | 0.175 | 0.565 | 0.06 ± 0.09 | 0.07 ± 0.10 | 0.11 ± 0.09 |
| Q06 | 2,645 | 5,017 | 10,209 | 0.775 | 1.383 | 3.888 | 0.29 ± 0.07 | 0.29 ± 0.06 | 0.34 ± 0.08 |
| Q07 | 27 | 27 | 64 | 0.005 | 0.005 | 0.014 | -0.00 ± 0.08 | -0.00 ± 0.08 | 0.02 ± 0.08 |
| Q08 | 17 | 17 | 34 | 0.005 | 0.004 | 0.009 | 0.02 ± 0.08 | 0.01 ± 0.08 | 0.03 ± 0.07 |
| Q09 | 5,116 | 5,116 | 10,407 | 1.352 | 1.307 | 3.634 | 0.26 ± 0.07 | 0.27 ± 0.07 | 0.31 ± 0.08 |
| Q10 | 31 | 48 | 107 | 0.013 | 0.018 | 0.034 | 0.04 ± 0.09 | 0.07 ± 0.10 | 0.07 ± 0.08 |
| Q11 | 9 | 38 | 86 | 0.003 | 0.012 | 0.027 | 0.00 ± 0.08 | 0.01 ± 0.12 | 0.02 ± 0.12 |
| Q12 | 216 | 782 | 1,454 | 0.084 | 0.259 | 0.485 | 0.06 ± 0.11 | 0.04 ± 0.11 | 0.04 ± 0.11 |
| Q13 | 49,777 | 49,777 | 149,331 | 7.463 | 7.524 | 31.269 | 1.30 ± 0.04 | 1.30 ± 0.05 | 1.20 ± 0.08 |
| Q14 | 1,883,811 | 1,883,811 | 3,826,615 | 640.521 | 670.042 | 1765.335 | 1.34 ± 0.10 | 1.37 ± 0.09 | 1.32 ± 0.13 |
| Q15 | 3 | 3 | 5 | 0.001 | 0.001 | 0.002 | -0.03 ± 0.10 | -0.04 ± 0.07 | -0.01 ± 0.08 |
| Q16 | 73 | 123 | 247 | 0.019 | 0.030 | 0.069 | 0.09 ± 0.09 | 0.07 ± 0.08 | 0.06 ± 0.08 |
| Q17 | 12,290 | 4,031 | 8,063 | 3.973 | 1.393 | 3.701 | 0.78 ± 0.07 | 0.32 ± 0.19 | 0.37 ± 0.22 |
| Q18 | 117,558 | 153 | 306 | 22.187 | 0.046 | 0.089 | 1.09 ± 0.02 | 0.02 ± 0.02 | 0.02 ± 0.03 |
| Q19 | 10,000 | 392 | 784 | 1.397 | 0.136 | 0.269 | 0.94 ± 0.02 | 0.20 ± 0.22 | 0.20 ± 0.22 |
| Q20 | 3,457 | 3,457 | 10,371 | 1.999 | 2.029 | 3.558 | 0.06 ± 0.06 | 0.07 ± 0.05 | 0.15 ± 0.06 |
<!-- /table -->

## Resident size by scale

<!-- table:sizes -->
| persons | flat MB | mid MB | normalized MB |
|---|---|---|---|
| 1,000 | 29.9 | 34.7 | 86.1 |
| 2,000 | 62.0 | 70.4 | 173.4 |
| 3,000 | 91.2 | 106.4 | 255.1 |
| 5,000 | 154.1 | 174.9 | 437.6 |
| 10,000 | 307.8 | 349.5 | 874.8 |
| 20,000 | 617.7 | 701.1 | 1,754.8 |
<!-- /table -->

## Reading the results

**Reification costs one extra hop per relation, everywhere.** At 20,000 persons the normalized/mid hop ratio is between 1.9 and 2.6 on 17 of 20 queries (median 2.03); the exceptions are Q13 and Q20 (3.0, because the symmetric Knows node is traversed through a shared label in both directions) and Q15 (1.7, a short recursive descent). Latency follows hops with a median ratio of 2.3; memory is 2.4–2.5× at every one of the six scales. None of this depends on n. The hop ratio is true by construction (a node was inserted into every relation); what the measurement adds is that the cost is a constant factor, not a higher order (H3), and the size of the constant in this engine.

**An entity without a node or an index is a scan.** Flat is at or below mid's cost on 17 queries and about 3× cheaper where a lookup becomes a property read (Q11, Q12). On the three queries that start from a folded entity (Q17 employees of an organisation, Q18 messages with a tag, Q19 people in a city) flat has no index and scans: 3×, 768× and 26× the hops of mid at 10,000 persons and 5×, 1,502× and 50× at 20,000, with latency exponents of 0.78–1.09 (± 0.02–0.07) against 0.02–0.32 for mid, indistinguishable from zero on Q18 and within two standard errors of it on Q17 and Q19. The follow-up with reverse indexes shows that this is the cost of the missing index, not of the flat layout: three dictionaries costing 2 MB remove it entirely. The earlier wording of this paragraph, "flat is catastrophic", was wrong; "unindexed is catastrophic" is what the data says.

**Under uniform fan-in, neighbourhood queries do not scale with n; under heavy-tailed fan-in, reverse lookups do on every schema.** In the main run, Q01–Q12, Q15, Q16, Q20 have latency exponents within ± 0.3 of zero on every schema (two standard errors are about 0.1) because the generator keeps average degree constant, and only the path searches Q13 and Q14 grow with n (1.20–1.37 ± 0.04–0.13). The skewed follow-up shows that this is a property of the generator: once a few cities and tags hold most of the persons and messages, Q17–Q19 grow with n on mid and normalized too (exponents 0.75–1.0), because the result set grows with n. The schema then changes the constant (mid needs 27× fewer hops than flat on Q18), not the exponent.

**Mid is never the fastest and never the slowest, until an index is allowed.** Mid is within 20% of the best schema on 12 of 20 queries, loses by up to 3.3× on forward lookups that flat answers from a property (Q11, Q12), and wins by one to three orders of magnitude on unindexed reverse lookups. With indexes, flat is within 20% of the best on all twenty and mid is never the best. The write-path follow-up gives the other side of that trade.

## Hypotheses

| | statement | verdict |
|---|---|---|
| H1 | each normalization level adds one hop to the median query | **supported**: normalized/mid hop ratio 2.03 (median), 1.7–3.0 (range) |
| H2 | latency grows with the product of fan-outs along the path | **supported** in the direction tested: latency tracks hops (ratio 2.3 vs 2.0); fan-out was not varied independently, so the multiplicative form is not tested |
| H3 | normalized memory grows faster than flat with scale | **refuted as stated**: both grow linearly (exponent 1.0); normalized is a constant 2.5× larger. The extra cost is a constant factor, not a higher order |
| H4 | mid is within 20% of flat on latency for 80% of queries while answering all twenty | **partly refuted**: 12/20 = 60%, not 80%. The second clause holds, and flat's failures on the reverse lookups (Q17–Q19) are worse than the hypothesis anticipated. The indexed follow-up shows the premise was mis-framed: the relevant comparison is indexed against unindexed, not mid against flat |

## Follow-up runs

### Flat with reverse indexes

`python -m ontostudy.bench --schemas flat flat_indexed mid --out docs/results/bench_indexed.csv`. `flat_indexed` is the flat schema plus three dictionaries (city → persons, employer → persons, tag → messages) built after load; an index lookup is charged one hop per result, as a reverse edge is. Raw rows in [bench_indexed.csv](bench_indexed.csv).

<!-- table:indexed-headline -->
| | flat | flat_indexed | mid |
|---|---|---|---|
| median hop ratio to mid, n=10,000 [95% CI over queries] | 1.00 [0.62, 1.00] | 0.90 [0.56, 1.00] | 1.00 [1.00, 1.00] |
| median latency ratio to mid, n=10,000 [95% CI] | 0.98 [0.76, 1.02] | 0.86 [0.66, 0.97] | 1.00 [1.00, 1.00] |
| size at n=10,000 | 308 MB | 310 MB | 350 MB |
| build time at n=10,000 | 0.8 s | 1.9 s | 3.7 s |
| queries within 20% of the fastest | 17 | 20 | 10 |
| queries with latency exponent > 0.5 | 5 (Q13, Q14, Q17, Q18, Q19) | 2 (Q13, Q14) | 2 (Q13, Q14) |
<!-- /table -->

<!-- table:indexed-diagnostic -->
| query | hops flat | hops flat_indexed | hops mid | exp flat | exp flat_indexed | exp mid |
|---|---|---|---|---|---|---|
| Q02 | 175 | 175 | 503 | 0.12 | 0.11 | 0.11 |
| Q11 | 9 | 9 | 38 | -0.01 | 0.04 | 0.04 |
| Q13 | 49,777 | 49,777 | 49,777 | 1.26 | 1.24 | 1.24 |
| Q17 | 12,290 | 2,483 | 4,031 | 0.79 | 0.44 | 0.43 |
| Q18 | 117,558 | 153 | 153 | 1.08 | 0.02 | 0.01 |
| Q19 | 10,000 | 98 | 392 | 0.94 | 0.35 | 0.34 |
<!-- /table -->

The three indexes cost 2 MB on top of flat's 308 MB (mid: 350 MB). With them, flat is within 20% of the best schema on all twenty queries and mid on ten; Q18 falls from 117,558 hops to 153, the same as mid, and Q19 to 98 against mid's 392, because flat reads employers from a property where mid traverses. Flat_indexed is a read-optimised, denormalised design: it copies city, country and employer names onto every person, and the write-path run below measures what that costs.

### Heavy-tailed fan-in

`python -m ontostudy.bench --skew 1 --schemas flat flat_indexed mid normalized --out docs/results/bench_skew.csv`. Cities, employers and tags are drawn from a Zipf distribution with exponent 1 (at 10,000 persons the largest city holds 1,950 persons against 130 under uniform draw, the most used tag is on 19,691 messages against 200), and query parameters are drawn in proportion to population so the head is asked about as often as it is populated. Raw rows in [bench_skew.csv](bench_skew.csv).

<!-- table:skew-headline -->
| | flat | flat_indexed | mid | normalized |
|---|---|---|---|---|
| median hop ratio to mid, n=10,000 [95% CI over queries] | 1.00 [0.61, 1.00] | 0.90 [0.55, 1.00] | 1.00 [1.00, 1.00] | 2.04 [2.00, 2.23] |
| median latency ratio to mid, n=10,000 [95% CI] | 0.92 [0.73, 1.01] | 0.82 [0.62, 0.98] | 1.00 [1.00, 1.00] | 2.28 [2.05, 2.54] |
| size at n=10,000 | 307 MB | 309 MB | 349 MB | 874 MB |
| build time at n=10,000 | 2.2 s | 4.5 s | 3.2 s | 10.2 s |
| queries within 20% of the fastest | 16 | 20 | 10 | 0 |
| queries with latency exponent > 0.5 | 5 (Q13, Q14, Q17, Q18, Q19) | 6 (Q09, Q13, Q14, Q17, Q18, Q19) | 6 (Q09, Q13, Q14, Q17, Q18, Q19) | 6 (Q05, Q13, Q14, Q17, Q18, Q19) |
<!-- /table -->

<!-- table:skew-diagnostic -->
| query | hops flat | hops flat_indexed | hops mid | hops normalized | exp flat | exp flat_indexed | exp mid | exp normalized |
|---|---|---|---|---|---|---|---|---|
| Q02 | 226 | 226 | 648 | 1,523 | 0.29 | 0.30 | 0.29 | 0.32 |
| Q11 | 10 | 10 | 42 | 94 | 0.19 | 0.18 | 0.24 | 0.24 |
| Q13 | 59,890 | 59,890 | 59,890 | 179,672 | 1.20 | 1.20 | 1.20 | 1.08 |
| Q17 | 22,174 | 13,211 | 21,389 | 42,779 | 0.94 | 0.91 | 0.91 | 0.93 |
| Q18 | 117,323 | 4,419 | 4,419 | 8,838 | 1.01 | 0.93 | 0.99 | 1.10 |
| Q19 | 10,000 | 665 | 2,652 | 5,305 | 0.94 | 0.77 | 0.75 | 0.78 |
<!-- /table -->

Under skew the reverse lookups grow with n on every schema, including mid and normalized (Q17–Q19 exponents 0.75–1.0), because the answer set grows with n. The schema still sets the constant: on Q18, mid and flat_indexed need 4,419 hops where unindexed flat needs 117,323. The main run's "slope about 0 for mid" on these queries was therefore a property of uniform fan-in, not of the schema. The ratios between schemas (normalized 2.0× mid; flat_indexed within 20% of best on 20 of 20) are unchanged by skew.

### Second engine: Kùzu

`python -m ontostudy.engine_kuzu --scales 1000 3000 10000 --out docs/results/bench_kuzu.csv`. The same data loaded three ways into Kùzu 0.11 (embedded, Cypher), the six diagnostic queries (Q02, Q11, Q13, Q17, Q18, Q19) written in Cypher once per schema, engine execution time best of five over the same twenty parameter sets, answers compared across schemas. Kùzu has no secondary property indexes, so flat's reverse lookups scan here as in the Python engine. Raw rows in [bench_kuzu.csv](bench_kuzu.csv).

<!-- table:kuzu-diagnostic -->
| query | ms flat | ms mid | ms normalized | exp flat | exp mid | exp normalized |
|---|---|---|---|---|---|---|
| Q02 | 1.434 | 1.638 | 9.346 | 0.32 | 0.26 | 0.56 |
| Q11 | 0.970 | 0.702 | 4.825 | 0.41 | 0.15 | 0.60 |
| Q13 | 1.030 | 1.002 | 2.037 | 0.33 | 0.35 | 0.34 |
| Q17 | 9.151 | 5.132 | 17.386 | 0.84 | 0.57 | 0.75 |
| Q18 | 6.931 | 1.362 | 2.650 | 0.92 | 0.36 | 0.58 |
| Q19 | 0.718 | 2.328 | 4.978 | 0.56 | 0.41 | 0.60 |
<!-- /table -->

<!-- table:kuzu-sizes -->
| persons | flat MB | mid MB | normalized MB |
|---|---|---|---|
| 1,000 | 8.0 | 15.3 | 36.5 |
| 3,000 | 9.8 | 18.5 | 45.4 |
| 10,000 | 16.4 | 27.9 | 71.1 |
<!-- /table -->

Two of the Python engine's numbers transfer and one does not.

- **Storage ratio transfers.** On disk at 10,000 persons: flat 16 MB, mid 28 MB, normalized 71 MB. Normalized over mid is 2.5×, the same ratio as the Python engine's resident size.
- **Hop counts transfer, latency ratios do not.** In Kùzu every extra hop is a join, and reification costs more than 2× on the multi-hop questions: normalized over mid is 5.7× on Q02 and 6.9× on Q11 (Python: 2.3 and 2.3), 1.9–3.4× on the rest. The direction is the same; the constant is engine-specific and larger here.
- **Unindexed scans are cheap on a columnar engine.** Flat's Q18 (messages with a tag, a `list_contains` scan over 117k messages) is 5.1× mid in Kùzu against about 500× in Python, and flat's Q19 (persons in a city) is 3.2× *faster* than mid, because a vectorised scan of 10,000 rows beats a join. The Python engine's "768× hops" is a true count of the work; how much that work costs depends entirely on the engine.
- **Fixed per-query overhead.** Kùzu's floor is about 1 ms per query (planning and pipeline setup), so on the cheap questions Python's dict lookups are 10–30× faster in absolute terms while Kùzu's BFS (Q13) is about 9× faster than the Python one. Absolute times across the two engines are not comparable; ratios within an engine are.

The practical reading: which schema costs more is engine-independent; how much more is not, and the constant for reification was larger on the database than on the toy engine, while the constant for scanning was much smaller.

### The write path

`python -m ontostudy.writes --scales 1000 3000 10000 --out docs/results/writes.csv`. Four updates applied to every schema; the count is the number of node property writes plus edge insertions and deletions the update needs. Raw rows in [writes.csv](writes.csv).

<!-- table:writes -->
Records touched per update and microseconds per update, n = 10,000, best of k.

| update | flat records | mid records | normalized records | flat_indexed records | flat µs | mid µs | normalized µs | flat_indexed µs |
|---|---|---|---|---|---|---|---|---|
| rename_city | 95 | 1 | 1 | 96 | 629.6 | 0.7 | 0.7 | 21.3 |
| move_person | 2 | 4 | 4 | 3 | 2.0 | 8.8 | 9.6 | 4.1 |
| change_employer | 1 | 4 | 10 | 2 | 5.3 | 23.4 | 32.0 | 9.7 |
| rename_tag | 153 | 1 | 1 | 154 | 23563.0 | 0.7 | 0.7 | 67.9 |
<!-- /table -->

Flat pays on writes for what it saved on reads, in proportion to fan-in. At 10,000 persons a renamed city is rewritten on 95 person records in flat and on one node in mid or normalized; a renamed tag on 153 messages against one. Unindexed flat also has to *find* those records by scanning (0.6 ms for a city, 24 ms for a tag), while flat_indexed finds them through the same index that made its reads fast (21 µs and 68 µs). The per-entity updates go the other way: moving a person or changing an employer touches 2–3 records on flat and 4–10 on mid and normalized, because flat rewrites a property where the others delete and insert edges (and normalized also retires a relation node). Under the skewed fan-in of the second follow-up the largest tag sits on 19,691 messages, so the rename cost of a denormalised design scales with the head of the distribution. None of this measures concurrency, transactions or permission checks.

## What a hop costs, per engine

The hop count is a count of work, not a cost: the Kùzu run above shows the same 117k-record scan costing about 500× mid on the Python engine and 5× on Kùzu. Splitting the count into its two kinds of work makes it a cost model. Every hop is either a random access (an edge traversal or an index hit, pointer chasing) or one record of a sequential scan of a whole type; the bench records the scan part separately, and the model below fits each engine's time to the two counts.

<!-- table:cost-model -->
Fit of log(ms per query) = a·log(1 + random accesses) + b·log(1 + scanned records) + c. Random accesses are edge traversals and index hits (pointer chasing); scanned records are nodes visited by a full scan of a type. Counts are the schema's, taken from the Python engine; each engine contributes its own times.

| engine | a: random access | b: sequential scan | c: fixed (log ms) | R² | rows |
|---|---|---|---|---|---|
| python | 0.93 | 0.70 | -7.78 | 0.93 | 360 |
| kuzu | 0.15 | 0.08 | -0.66 | 0.17 | 54 |
<!-- /table -->

On the in-memory engine the two counts are a cost model: R² 0.93 over all 360 rows, with a random access costing close to linear (doubling them multiplies time by 1.9) and a scanned record less (1.6), which is why the earlier "768×" overstated the scan even on this engine. On Kùzu they are not: R² 0.17 on the 54 shared rows, and removing a fixed floor does not help. Kùzu's times on these questions lie between 0.2 and 17 ms and are set by planning, pipeline setup and join strategy, not by how many records the schema makes a query touch. The result is stronger than the caveat it replaces: a schema-level count predicts an engine that chases pointers one record at a time, and predicts very little about a database with a planner at this scale. Pricing a schema on a database needs the database's own operator counts (its profile output), fitted the same way; that is the next run, not a footnote.

## Threats specific to these runs

- One engine for the full twenty queries (an in-memory Python property graph with dict adjacency); the second engine covers six. Hop counts transfer to other engines; constant factors do not, and the Kùzu section reports how far they moved.
- Synthetic data. The main run's uniform fan-in has no supernodes (highest degree at 10,000 persons is a person with 570 edges); the skewed run adds them by construction, not from a measured real distribution. Neither is LDBC Datagen or a real graph.
- Read-only workload in the main run; the write path is measured separately with four update types and no concurrency.
- Exponents are fitted on six scales in the main run and three in the follow-ups; the ± in the per-query table is two standard errors of the fit (about 0.05–0.2). A run that overlapped other work on the machine moved these exponents by up to 0.15; the committed run was made with nothing else running.
- Hand-written accessors, not a query planner. The Kùzu run lets a planner choose the join order for six queries; the other fourteen have not been checked that way.
- Flat's reverse-lookup penalty assumes no secondary index on properties, which the indexed follow-up then removes; the threat is now stated as a result rather than a caveat.

## Next

- Replace the synthetic generator with LDBC Datagen SF1 or a real graph, and compare the Q13/Q14 numbers with LDBC's published results as an external check.
- Extend the Kùzu run to all twenty queries.
- Whether an LLM writes correct Cypher against each schema (Text2Cypher accuracy per schema) is a natural fourth question; it is out of scope here because the study does not use an LLM API.
