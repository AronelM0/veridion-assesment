# Pilot data

| File | Contents |
| --- | --- |
| [sample.csv](sample.csv) | The 30 sampled companies, Companies House numbers and source award releases |
| [mhra-candidates.csv](mhra-candidates.csv) | Candidate numbers with report, supplier name and source transaction |
| [website-search.csv](website-search.csv) | Search queries, reviewed pages, candidate numbers and unsuccessful searches |
| [hmrc-checks.csv](hmrc-checks.csv) | Timestamp, registered name and postcode, identity evidence and verdict for each check |
| [results.csv](results.csv) | One outcome per sampled company, with a VAT number only when confirmed |

The original files can be downloaded to the Git-ignored `data/local/` directory with the [fetch command](../src/README.md). The source files were the [September 2026 Contracts Finder snapshot](https://www.data.gov.uk/dataset/38fbd6d7-af09-4a4e-8308-24bda1aec205/contracts-finder-notices-09-20261) and the MHRA spending reports for [April 2025](https://www.gov.uk/csv-preview/685abe81db207fc18744d63d/01_MHRA_spending_over__25_000_data_for_April_2025.csv) and [June 2026](https://www.gov.uk/csv-preview/6a7aeb0baadaaddf89b6e3d1/03_MHRA_spending_over__25_000_data_for_June_2026.csv).
