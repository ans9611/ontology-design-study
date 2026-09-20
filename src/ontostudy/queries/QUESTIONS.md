# The twenty benchmark questions

Fixed before any schema is written (see docs/hypotheses.md). Each question is later expressed once per schema (flat / mid / normalized). The domain is LDBC SNB: persons, posts, comments, forums, tags, organisations, places.

The hop column is the measured mean number of edge traversals per query at n = 10,000 persons (docs/results/bench.csv), flat / mid / normalized.

| id | question | kind | expected hops (flat / mid / norm) |
|----|----------|------|-----------------------------------|
| Q01 | Given a person, list their friends' names and cities | 2-hop lookup | 9 / 19 / 47 |
| Q02 | Given a person, list friends of friends who live in the same country | 3-hop with filter | 175 / 503 / 1182 |
| Q03 | Given a person, the 10 most recent posts by their friends | neighborhood + sort | 143 / 143 / 297 |
| Q04 | Given a person and a date range, the tags most used in their friends' posts | aggregation over neighborhood | 143 / 179 / 369 |
| Q05 | Given a person, the forums their friends joined after a date, ranked by number of posts from those friends | join-heavy | 1152 / 1152 / 2315 |
| Q06 | Given a person and a tag, other tags that co-occur on posts by friends-of-friends | 4-hop co-occurrence | 2645 / 5017 / 10209 |
| Q07 | Given a person, who liked their posts recently and whether they are a friend | reverse edge + membership test | 27 / 27 / 64 |
| Q08 | Given a person, the latest comments replying to their posts | reverse 2-hop | 17 / 17 / 34 |
| Q09 | Given a person, recent messages by friends-of-friends before a date | 3-hop with filter | 5116 / 5116 / 10407 |
| Q10 | Given a person, friends with a birthday in a month, scored by common interests | scoring over neighborhood | 31 / 48 / 107 |
| Q11 | Given a person and a country, friends who work at companies in that country | 3-hop across entity types | 9 / 38 / 86 |
| Q12 | Given a person and a tag class, friends who commented on posts about that class | hierarchy traversal + 3-hop | 216 / 782 / 1454 |
| Q13 | Shortest path length between two persons | variable-length path | 49777 / 49777 / 149331 |
| Q14 | Weighted shortest paths between two persons where weight depends on reply counts | variable-length with computed weights | 1883811 / 1883811 / 3826615 |
| Q15 | For a given post, its full comment thread | recursive descent | 3 / 3 / 5 |
| Q16 | For a given forum, members grouped by country with post counts | group-by over 2 hops | 73 / 123 / 247 |
| Q17 | For a given organisation, the tag distribution of posts by its employees | 3-hop aggregation | 12290 / 4031 / 8063 |
| Q18 | For a given tag, the number of posts per month over the last year | time-bucketed count | 117558 / 153 / 306 |
| Q19 | For a given place, the people located there and their employers | 2-hop across types | 10000 / 392 / 784 |
| Q20 | For a given person, the ego network to depth 2 with PPR scores (uses `PPRMatrix`) | centrality over neighborhood | 3457 / 3457 / 10371 |
Q01–Q14 correspond in spirit to LDBC SNB Interactive complex reads 1–14 [8] so results can be compared with published numbers; Q15–Q20 are added to cover recursion, aggregation and centrality.
