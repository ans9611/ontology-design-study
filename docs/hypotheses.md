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
