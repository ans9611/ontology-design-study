# Case: Schema.org

| field | value |
|-------|-------|
| Organization | founded by Google, Microsoft, Yahoo, Yandex (2011); W3C community group |
| Domain | web page markup: organizations, products, events, recipes, articles, etc. |
| Period | 2011–present |
| Scale | hundreds of types and over a thousand properties in the vocabulary; adoption measured in the share of crawled pages carrying markup (figures in [17]; check for a current Web Data Commons number) |
| Source grade | A |
| Primary sources | Guha, Brickley & Macbeth, CACM 59(2), 2016 [17] |

## Purpose and users

Give webmasters one vocabulary that all major search engines consume. The user is a webmaster who will spend minutes, not days, on markup.

## Design method

Deliberately shallow and permissive. A flat-ish type hierarchy rooted at `Thing`; properties have expected types but values of other types are tolerated. Extensions are added by proposal and reviewed for usage, not for logical rigor. The authors describe choosing usability by non-experts over formal precision.

## Quality control

Almost none on the data side; consumers (search engines) clean up. On the vocabulary side, changes are reviewed in public and versioned.

## Known failures or limits

Markup on the web is often incomplete or wrong, and the paper acknowledges that consumers must be tolerant. The vocabulary cannot express much beyond what search engines want to show; it is not a general ontology.

## Design patterns observed

- `minimal-schema`
- `tolerant-consumption`: quality handled by the reader, not the writer
- `usage-driven-extension`
- `single-consumer-purpose`: the schema exists for a specific set of consumers

## Relevance to RQ2

The strongest evidence that adoption scales inversely with the burden the schema places on the writer. Contrast with Cyc and with OWL-based domain ontologies.

## To verify against the source

- Adoption figures and the year they refer to
- Whether the paper gives the type/property count at publication
