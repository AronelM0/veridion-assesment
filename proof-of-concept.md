# Part 2 — Proof of Concept

## Sample and method

The pilot drew a sample from the September 2026 Contracts Finder snapshot before looking up VAT numbers for those suppliers. The 29 published daily files contained 2,716 award releases. The script kept suppliers on active awards with a usable Companies House number, deduplicated by that number, and randomly selected 30 from 599 eligible identifiers with seed `202609`. The sample contained 23 service suppliers and seven goods suppliers. It covers identifiable public-contract suppliers in the selected month, with a tilt toward services. [Contracts Finder snapshot](https://www.data.gov.uk/dataset/38fbd6d7-af09-4a4e-8308-24bda1aec205/contracts-finder-notices-09-20261) · [Sample](data/sample.csv)

The Python script matched supplier names against the two MHRA reports identified in [Part 1](research.md). It ignored case and punctuation and treated `Limited` and `Ltd` alike. It accepted nine-digit candidates after removing spaces, hyphens and an optional `GB` prefix. The website search covered the remaining firms, with targeted follow-ups when the first results did not identify the right entity. The search log records the pages and unsuccessful searches. [MHRA candidate rows](data/mhra-candidates.csv) · [Website search log](data/website-search.csv)

Every distinct candidate went through HMRC's public checker on 12 November 2026. The verification log compares the returned legal name and postcode with Companies House and the source that published the number. A confirmed link requires a valid VAT number and evidence tying it to the sampled legal entity. [HMRC checker](https://www.gov.uk/check-uk-vat-number) · [Verification log](data/hmrc-checks.csv)

## Results

| Measure | Observed result |
| --- | ---: |
| Companies with a confirmed VAT association | **5 / 30 (16.7%)** |
| Confirmed via MHRA | 2 |
| Additional confirmations via company websites | 3 |
| Distinct candidate associations checked at HMRC | 7 |
| Inconclusive associations | 2 |
| Firms with no candidate sent to HMRC | 23 |
| False positives among conclusively checked associations | **0 / 5 (0%)** |

The false-positive measure counts invalid numbers or clearly mismatched entities among candidate associations with a conclusive verdict. Its denominator was five. Two valid numbers had unresolved entity links and are recorded separately. Coverage measures what this search recovered in the sample. The VAT registration status of the remaining firms is unknown. [Company-level results](data/results.csv)

## Where the checks mattered

- **Tunstall and Gleeds.** Tunstall Healthcare (UK) published a number that HMRC returned under Tunstall Group Ltd. Companies House corroborated corporate control. Gleeds' site published the number of Gleeds LLP, while the sampled firm was Gleeds Cost Management Limited. Both links remain inconclusive because the evidence did not establish shared VAT registration. [Tunstall terms](https://shop.tunstall.co.uk/terms) · [Tunstall ownership record](https://find-and-update.company-information.service.gov.uk/company/01332249/persons-with-significant-control) · [Gleeds terms](https://www.gleeds.com/en/terms-and-conditions/)
- **Bhuku and Allotrope.** Bhuku's site labelled its eight-digit Companies House number as VAT, so the value failed the format check. Allotrope stated it was VAT-registered and did not publish a number on the page reviewed. [Bhuku terms](https://ma-mix.com/terms-of-use/) · [Bhuku Companies House profile](https://find-and-update.company-information.service.gov.uk/company/15547198) · [Allotrope Scientific](https://www.allotrope.tech/about)

The local sampling, MHRA matching and reporting commands took about 1.44 seconds combined in one run with the source files already downloaded. The pilot required website searches for 28 suppliers and seven HMRC checks. Manual time per company was not logged. Part 3 uses the counts to identify where to measure labour in the next batch. [Part 3 — Scaling with Real Resources](scaling.md)

## Reproduction

Run `python src/pilot.py report` to recompute the results from the recorded evidence. The [run instructions](src/README.md) also show how to regenerate the sample and MHRA candidates.
