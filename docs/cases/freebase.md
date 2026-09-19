# Case: Freebase

| field | value |
|-------|-------|
| Organization | Metaweb (2007), acquired by Google (2010), shut down 2016 with migration to Wikidata |
| Domain | general knowledge |
| Period | 2007–2016 |
| Scale | tens of millions of topics, on the order of a billion facts at shutdown (check against [11]) |
| Source grade | A |
| Primary sources | Pellissier Tanon et al., WWW 2016 [11] |

## Purpose and users

Open, collaboratively edited knowledge base with a public API; used by Google for the Knowledge Graph and by third-party developers.

## Design method

Schema organized into domains, types and properties, with compound value types (CVTs) for n-ary relations. Each topic could carry multiple types. Contributions from Wikipedia imports, bulk loads, and community edits.

## Quality control

Community editing with reversion; type system constrained what properties a topic could carry. Provenance was per statement but less structured than Wikidata's reference model.

## Known failures or limits

Shutdown and migration. The migration paper documents the schema mismatch between the two systems: Freebase's CVTs versus Wikidata's qualifiers, differing notions of type, and different reference requirements. A large fraction of Freebase facts could not be imported directly because Wikidata required a source per statement that Freebase did not carry. The paper reports the mapping effort and the proportion of facts transferred (check figures against [11]).

## Design patterns observed

- `n-ary-via-reification` (CVTs): a normalization choice that later had no direct equivalent in the target model
- `multi-type-entities`
- `provenance-weak`: per-statement sourcing was optional, which became a hard constraint at migration time
- `platform-dependency`: sustained by a single sponsor; ended when the sponsor's priorities changed

## Relevance to RQ2

The clearest documented case of structural decisions (reification style, provenance model) turning into migration cost years later. Directly motivates the "hard to change after adoption" argument and gives a concrete mapping between normalization style and cost of change.

## To verify against the source

- Proportion of facts migrated vs. dropped
- Exact reasons given for statements that could not be mapped
