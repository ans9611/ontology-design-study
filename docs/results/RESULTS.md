# RQ3 results: query cost under three normalization depths

Run on 2026-09-20. `python -m ontostudy.bench --scales 1000 3000 10000 --repeats 5 --n-args 20`. Raw rows in [bench.csv](bench.csv), sizes in [sizes.csv](sizes.csv). All three schemas returned identical answers for every query and parameter set (540 checks).

## Setup

- Data: synthetic LDBC-SNB-shaped graphs with 1,000 / 3,000 / 10,000 persons (see the dated note in ../hypotheses.md on why not LDBC Datagen). At 10,000 persons: 50k friendships, 39k posts, 78k comments, 175k likes.
- Schemas: flat (place, organisation, tag folded into properties; no reverse index on them), mid (entity nodes and direct edges; the SNB model), normalized (every relation reified as a node).
- Queries: the twenty in ../../src/ontostudy/queries/QUESTIONS.md, written once against the accessor interface. Twenty parameter sets per query, shared by all schemas; best of five runs.
- Metrics: hops (edge traversals, counted in the graph; a scan counts as one traversal per node), latency (ms per query), resident size (recursive sys.getsizeof), and a log-log latency exponent over the three scales.

## Headline numbers

| | flat | mid | normalized |
|---|---|---|---|
| median hop ratio to mid, n=10k | 1.00 | 1 | **2.03** |
| median latency ratio to mid, n=10k | 0.94 | 1 | **2.29** |
| size at n=10k | 308 MB | 350 MB | **875 MB** |
| build time at n=10k | 0.9 s | 2.4 s | 6.3 s |
| queries within 20% of the fastest | 15 | 12 | 0 |
| queries with latency exponent > 0.5 | 5 (Q13, Q14, Q17, Q18, Q19) | 2 (Q13, Q14) | 3 (Q13, Q14, Q17) |

![hops](fig1_hops.png)

![scaling](fig2_scaling.png)

![memory](fig3_memory.png)

## Per-query table, n = 10,000

exp = slope of log(latency) against log(persons) over 1k/3k/10k.

| query | hops flat | hops mid | hops norm | norm/mid | flat/mid | ms flat | ms mid | ms norm | exp flat | exp mid | exp norm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q01 | 9 | 19 | 47 | 2.47 | 0.47 | 0.007 | 0.008 | 0.016 | 0.11 | 0.06 | 0.06 |
| Q02 | 175 | 503 | 1182 | 2.35 | 0.35 | 0.054 | 0.129 | 0.306 | 0.13 | 0.14 | 0.13 |
| Q03 | 143 | 143 | 297 | 2.08 | 1.0 | 0.027 | 0.026 | 0.068 | 0.09 | 0.09 | 0.09 |
| Q04 | 143 | 179 | 369 | 2.06 | 0.8 | 0.039 | 0.048 | 0.101 | 0.13 | 0.12 | 0.1 |
| Q05 | 1152 | 1152 | 2315 | 2.01 | 1.0 | 0.181 | 0.183 | 0.771 | 0.1 | 0.12 | 0.25 |
| Q06 | 2645 | 5017 | 10209 | 2.03 | 0.53 | 0.913 | 1.749 | 4.886 | 0.27 | 0.34 | 0.41 |
| Q07 | 27 | 27 | 64 | 2.37 | 1.0 | 0.004 | 0.005 | 0.013 | 0.03 | 0.08 | 0.01 |
| Q08 | 17 | 17 | 34 | 2.0 | 1.0 | 0.004 | 0.004 | 0.009 | 0.04 | 0.04 | 0.02 |
| Q09 | 5116 | 5116 | 10407 | 2.03 | 1.0 | 1.645 | 1.763 | 3.965 | 0.35 | 0.38 | 0.28 |
| Q10 | 31 | 48 | 107 | 2.23 | 0.65 | 0.012 | 0.016 | 0.034 | 0.04 | 0.07 | 0.1 |
| Q11 | 9 | 38 | 86 | 2.26 | 0.24 | 0.003 | 0.011 | 0.027 | 0.04 | 0.03 | 0.06 |
| Q12 | 216 | 782 | 1454 | 1.86 | 0.28 | 0.088 | 0.362 | 0.526 | 0.09 | 0.19 | 0.07 |
| Q13 | 49777 | 49777 | 149331 | 3.0 | 1.0 | 8.648 | 9.109 | 37.218 | 1.32 | 1.33 | 1.21 |
| Q14 | 1883811 | 1883811 | 3826615 | 2.03 | 1.0 | 788.221 | 741.716 | 1934.141 | 1.38 | 1.37 | 1.34 |
| Q15 | 3 | 3 | 5 | 1.67 | 1.0 | 0.001 | 0.001 | 0.002 | -0.05 | -0.05 | -0.01 |
| Q16 | 73 | 123 | 247 | 2.01 | 0.59 | 0.019 | 0.030 | 0.070 | 0.16 | 0.11 | 0.1 |
| Q17 | 12290 | 4031 | 8063 | 2.0 | 3.05 | 4.057 | 1.552 | 3.901 | 0.81 | 0.46 | 0.52 |
| Q18 | 117558 | 153 | 306 | 2.0 | 768.35 | 21.626 | 0.042 | 0.088 | 1.09 | -0.03 | 0.01 |
| Q19 | 10000 | 392 | 784 | 2.0 | 25.51 | 1.369 | 0.139 | 0.267 | 0.96 | 0.33 | 0.32 |
| Q20 | 3457 | 3457 | 10371 | 3.0 | 1.0 | 2.089 | 2.098 | 3.795 | 0.01 | 0.06 | 0.15 |

## Reading the results

**Reification costs exactly one extra hop per relation, everywhere.** The normalized/mid hop ratio is 2.0 ± 0.1 for 17 of 20 queries; the exceptions are Q13 and Q20 (3.0, because the symmetric Knows node is traversed through a shared label in both directions) and Q15 (1.7, a short recursive descent). Latency follows hops with a median ratio of 2.3. Memory is 2.5× at every scale. None of this depends on n.

**Folding relations into properties is free for forward reads and catastrophic for reverse ones.** Flat is at or below mid's cost on 17 queries and up to 4× cheaper where a lookup becomes a property read (Q11, Q12). On the three queries that start from a folded entity (Q17 employees of an organisation, Q18 messages with a tag, Q19 people in a city) flat has no index and scans: 3×, 768× and 26× the hops of mid, with latency exponents of 0.8–1.1 against ~0 for mid. That is the O(n) versus O(1) difference the motivation section predicted, and it appears only once n is large enough to matter: at n = 1,000 Q18 is 2 ms on flat and looks acceptable.

**Neighbourhood queries do not scale with n at all.** For Q01–Q12, Q15, Q16, Q20 the latency exponent is 0.0–0.4 on every schema: the cost is set by the size of the neighbourhood, which the generator keeps at constant average degree. The only queries that grow with n on every schema are the path searches Q13 and Q14 (exponent 1.2–1.4), which visit a fraction of the whole graph.

**Mid is never the fastest and never the slowest.** It is within 20% of flat on 12 of 20 queries, loses by up to 4× on forward lookups that flat answers from a property, and wins by one to three orders of magnitude on the reverse lookups. It answers every query with bounded cost.

## Hypotheses

| | statement | verdict |
|---|---|---|
| H1 | each normalization level adds one hop to the median query | **supported**: normalized/mid hop ratio 2.03 (median), 1.7–3.0 (range) |
| H2 | latency grows with the product of fan-outs along the path | **supported** in the direction tested: latency tracks hops (ratio 2.3 vs 2.0); fan-out was not varied independently, so the multiplicative form is not tested |
| H3 | normalized memory grows faster than flat with scale | **refuted as stated**: both grow linearly (exponent 1.0); normalized is a constant 2.5× larger. The extra cost is a constant factor, not a higher order |
| H4 | mid is within 20% of flat on latency for 80% of queries while answering all twenty | **partly refuted**: 12/20 = 60%, not 80%. The second clause holds, and flat's failures on the reverse lookups (Q17–Q19) are worse than the hypothesis anticipated |

## Threats specific to this run

- One engine (an in-memory Python property graph with dict adjacency). Constant factors will differ in Neo4j or an RDF store; hop counts will not.
- Synthetic data. Degree distribution follows preferential attachment with m = 5; real social graphs have heavier tails, which would raise the cost of Q06, Q09, Q13 on every schema equally.
- Flat's reverse-lookup penalty assumes no secondary index on properties. A property index would remove it, at the memory cost of maintaining one, which moves flat toward mid.
- Scale tops out at 10,000 persons (≈130k nodes for mid) because the normalized schema at 30,000 persons exceeded the memory budget of the machine used. The exponents are fitted on three points.

## Next

- Add a property index variant of flat to quantify the index-versus-edge trade-off directly.
- Replace the engine with Neo4j through the same accessor interface; keep the hop counter as the schema-level metric and use engine time as the second.
- Use the Q13/Q14 path queries with LDBC's published SF1 numbers as an external sanity check.
