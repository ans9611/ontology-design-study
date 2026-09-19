# The twenty benchmark questions

Fixed before any schema is written (see docs/hypotheses.md). Each question is later expressed once per schema (flat / mid / normalized). The domain is LDBC SNB: persons, posts, comments, forums, tags, organisations, places.

The hop count column is the minimum number of relationship traversals in the normalized schema; it is filled in when the schemas exist.

| id | question | kind | expected hops (flat / mid / norm) |
|----|----------|------|-----------------------------------|
| Q01 | Given a person, list their friends' names and cities | 2-hop lookup | |
| Q02 | Given a person, list friends of friends who live in the same country | 3-hop with filter | |
| Q03 | Given a person, the 10 most recent posts by their friends | neighborhood + sort | |
| Q04 | Given a person and a date range, the tags most used in their friends' posts | aggregation over neighborhood | |
| Q05 | Given a person, the forums their friends joined after a date, ranked by number of posts from those friends | join-heavy | |
| Q06 | Given a person and a tag, other tags that co-occur on posts by friends-of-friends | 4-hop co-occurrence | |
| Q07 | Given a person, who liked their posts recently and whether they are a friend | reverse edge + membership test | |
| Q08 | Given a person, the latest comments replying to their posts | reverse 2-hop | |
| Q09 | Given a person, recent messages by friends-of-friends before a date | 3-hop with filter | |
| Q10 | Given a person, friends with a birthday in a month, scored by common interests | scoring over neighborhood | |
| Q11 | Given a person and a country, friends who work at companies in that country | 3-hop across entity types | |
| Q12 | Given a person and a tag class, friends who commented on posts about that class | hierarchy traversal + 3-hop | |
| Q13 | Shortest path length between two persons | variable-length path | |
| Q14 | Weighted shortest paths between two persons where weight depends on reply counts | variable-length with computed weights | |
| Q15 | For a given post, its full comment thread | recursive descent | |
| Q16 | For a given forum, members grouped by country with post counts | group-by over 2 hops | |
| Q17 | For a given organisation, the tag distribution of posts by its employees | 3-hop aggregation | |
| Q18 | For a given tag, the number of posts per month over the last year | time-bucketed count | |
| Q19 | For a given place, the people located there and their employers | 2-hop across types | |
| Q20 | For a given person, the ego network to depth 2 with PPR scores (uses `PPRMatrix`) | centrality over neighborhood | |

Q01–Q14 correspond in spirit to LDBC SNB Interactive complex reads 1–14 [8] so results can be compared with published numbers; Q15–Q20 are added to cover recursion, aggregation and centrality.
