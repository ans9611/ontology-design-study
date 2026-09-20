# Pre-registered hypotheses for RQ3

Written before any experiment is run. Do not edit after the first benchmark; add a dated note instead.

**H1.** Each additional level of normalization adds one hop to the median benchmark query.

**H2.** Query latency grows with the product of fan-outs along the path, so a link with fan-out f multiplies cost by about f per hop.

**H3.** Memory of the normalized schema grows faster than the flat schema with scale factor, because intermediate nodes are materialized.

**H4.** The mid-level schema is within 20% of the flat schema on latency for 80% of queries while keeping the normalized schema's ability to answer all 20 questions.

## Measurement

- 20 benchmark questions, fixed before schema design
- 3 schemas: flat, mid, normalized
- LDBC SNB scale factors 0.1, 1, 3
- Same engine, same machine, 5 runs, minimum reported
- Metrics: hop count (static), latency (ms), peak memory (MB), answer correctness against the normalized schema

## Notes

(dated entries only)

**2026-09-20.** LDBC Datagen requires a Spark/Hadoop installation and produces multi-GB outputs; instead a deterministic generator with the same entity and relation types and the same degree shape was written (`ontostudy.synth`). The twenty questions were kept as specified. Scale factors are expressed as persons (1,000 / 3,000 / 10,000) rather than LDBC SF 0.1 / 1 / 3. Engine is an in-memory property graph with a hop counter rather than a database server. None of the four hypotheses was changed.

**2026-09-20, after the run.** Verdicts recorded in results/RESULTS.md: H1 supported, H2 supported in the direction tested, H3 refuted as stated (constant factor, not higher order), H4 partly refuted (60%, not 80%).

**2026-09-20, follow-up runs.** Four runs were added after the verdicts above and are not used to score H1–H4: flat with reverse indexes, Zipf fan-in, the six diagnostic queries on Kùzu, and a write-path benchmark. They change the reading of H4 (the premise compared the wrong pair: indexed against unindexed, not mid against flat) and of the "mid does not scale on reverse lookups" claim (true only under uniform fan-in). The main run was also re-run at six scales (1k–20k) with every repeat recorded, so the per-query table now carries a standard error on each exponent. Hop counts are unchanged by the re-run; latencies moved within run-to-run noise.
