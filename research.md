# Part 1 — Research

## Research Objective

The objective of this research is to determine whether UK companies' VAT numbers can actually be obtained from publicly available sources.

I focused on identifying available sources, their limitations, and the challenges that could arise during data collection and verification.

## 1. First Surprise — Commercial Usage Restrictions

My first surprise came when I discovered that some sources, despite being free and easily accessible, cannot necessarily be used for commercial purposes.

My initial assumption was simple: find a source, extract the available information, and integrate it into the final database.

In reality, the process is more complicated. Free access to information does not automatically grant permission to reuse it commercially.

One example is **OpenCorporates**, a platform that provides company information. After reviewing its terms of use, I found that automated scraping for this purpose is prohibited and commercial access generally requires a separate agreement. [OpenCorporates Terms of Use](https://opencorporates.com/terms-of-use/)

This made me realize that, beyond technical challenges, there may also be legal restrictions or additional costs related to data access and processing.

## 2. HMRC — Automation Possibilities

After reviewing the HMRC API documentation, I confirmed that VAT number verification can be automated. [HMRC Check a UK VAT number API](https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/vat-registered-companies-api/2.0)

The documented standard rate limit of **3 requests per second per application** was an unexpected limitation. [HMRC rate limits](https://developer.service.hmrc.gov.uk/api-documentation/docs/reference-guide#rate-limiting)

Therefore, the service cannot be used excessively without considering this restriction, which could affect the efficiency of the process at scale.

## 3. VAT Number Ambiguity

Things became increasingly complicated as my research progressed.

Initially, I assumed that each company had its own unique VAT number. However, I discovered two distinct situations in which the same VAT number can appear under different company names.

### First Case — Company Name Changes

One example is **Jumar Technology Limited**, which appeared in an MHRA report from April 2025 with VAT number `318799157`. [MHRA spending report, April 2025](https://www.gov.uk/csv-preview/685abe81db207fc18744d63d/01_MHRA_spending_over__25_000_data_for_April_2025.csv)

In another MHRA report from June 2026, the same VAT number was associated with **TXP Technology Limited**. [MHRA spending report, June 2026](https://www.gov.uk/csv-preview/6a7aeb0baadaaddf89b6e3d1/03_MHRA_spending_over__25_000_data_for_June_2026.csv)

Checking the company's history in Companies House confirmed that it changed its name on August 22, 2025, while maintaining the same legal identity (company number `11786401`). [Companies House company history](https://find-and-update.company-information.service.gov.uk/company/11786401)

### Second Case — VAT Groups

Multiple legally distinct companies can share the same VAT number if they belong to a VAT Group. [HMRC guidance on group registration](https://www.gov.uk/guidance/vat-registration-for-groups-divisions-and-joint-ventures)

When two different company names are associated with the same VAT number, we cannot determine from that information alone whether a company has changed its name or whether the companies belong to the same VAT Group.

**Is there a publicly available indicator that can reliably identify whether a company belongs to a VAT Group?**

## 4. Companies House and MHRA — Useful Sources for Identification and Discovery

I identified two resources that could help address the challenges described above.

**Companies House** provides free company information, including legal names, unique registration numbers, status, addresses, and name histories.

However, after examining its company profile data structure, I found that VAT numbers are not included as a standard field. [Companies House company profile schema](https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/resources/companyprofile?v=latest)

This means Companies House cannot directly solve the VAT discovery problem, although it can help determine whether two names refer to the same legal entity, as demonstrated by the Jumar Technology and TXP Technology case.

**MHRA and other government institutions** publish reports detailing payments made to suppliers, some of which also include VAT numbers.

I found the following supplier entries in the June 2026 report. [MHRA spending report, June 2026](https://www.gov.uk/csv-preview/6a7aeb0baadaaddf89b6e3d1/03_MHRA_spending_over__25_000_data_for_June_2026.csv)

- Accenture (UK) Limited — `788629066`
- CDW Limited — `902194939`
- Bechtle Direct Ltd (UK) — `699374267`

The main advantage is the existence of a **source independent of the company's own website**, since VAT numbers can also be discovered in documents published by its customers.

Furthermore, a single report may contain information about numerous suppliers, potentially reducing the effort required for data collection.

However, the same report also contains missing values. For example, **Clinton Health Access Initiative** appears with its VAT number marked as `Not set`.

This shows that even a useful, structured source cannot be assumed to provide complete coverage.

## 5. Data Volatility

Another important factor is the high annual turnover of VAT registrations.

HMRC reported approximately **234,000 new VAT registrations and 218,000 deregistrations** for the 2024–2025 financial year. [HMRC annual UK VAT statistics](https://www.gov.uk/government/statistics/value-added-tax-vat-annual-statistics/annual-uk-vat-statistics-2023-to-2024-commentary)

This indicates that a database built only once can quickly become outdated.

Therefore, continuous data updates are necessary.

## 6. What the Discovery Paths Returned

- **MHRA.** Running `python src/pilot.py discover` against the April 2025 and June 2026 reports produced three candidate rows for two companies in the 30-company sample. Both company–VAT associations were later confirmed. The second Phoenix Software row repeated the same association in a different month. This gave me a source that worked, with a limited reach on the sample. [Candidate rows](data/mhra-candidates.csv) · [Verification log](data/hmrc-checks.csv)
- **Company websites.** Integrity360's contracting-entity table looked promising because it had a dedicated VAT column and identified the exact UK company number, `03538529`. The UK VAT cell was blank, while several other countries had a number. That path yielded no UK candidate for this supplier. [Integrity360 entity table](https://www.integrity360.com/entitytable) · [Website search log](data/website-search.csv)

## 7. Conclusion

My research confirmed that VAT numbers can be discovered through publicly available sources, but the process is more complicated than I initially expected.

The main challenges identified are commercial usage restrictions, automated verification limitations, ambiguity between companies, and the need for continuous data updates.

I identified sources that could contribute both to VAT number discovery and company identity verification. However, it remains unclear how efficiently this approach could be applied at scale.

The proof of concept put the discovery paths to the test on an independently drawn supplier sample and used HMRC checks to establish which associations could be confirmed. [Part 2 — Proof of Concept](proof-of-concept.md)
