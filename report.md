# VAT Identifier Discovery

Can a UK supplier VAT dataset be built from public sources? This report documents the research, a pilot that confirmed five associations among 30 sampled suppliers, and a proposed production service. The starting design is available separately. [Initial Hypotheses](initial-hypotheses.md)

## Part 1 Research

### Research Objective

The objective of this research is to determine whether UK companies' VAT numbers can actually be obtained from publicly available sources.

I focused on identifying available sources, their limitations, and the challenges that could arise during data collection and verification.

### 1. First Surprise — Commercial Usage Restrictions

My first surprise came when I discovered that some sources, despite being free and easily accessible, cannot necessarily be used for commercial purposes.

My initial assumption was simple: find a source, extract the available information, and integrate it into the final database.

In reality, the process is more complicated. Free access to information does not automatically grant permission to reuse it commercially.

One example is **OpenCorporates**, a platform that provides company information. After reviewing its terms of use, I found that automated scraping for this purpose is prohibited and commercial access generally requires a separate agreement. [OpenCorporates Terms of Use](https://opencorporates.com/terms-of-use/)

This made me realize that, beyond technical challenges, there may also be legal restrictions or additional costs related to data access and processing.

### 2. HMRC — Automation Possibilities

After reviewing the HMRC API documentation, I confirmed that VAT number verification can be automated. [HMRC Check a UK VAT number API](https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/vat-registered-companies-api/2.0)

The documented standard rate limit of **3 requests per second per application** was an unexpected limitation. [HMRC rate limits](https://developer.service.hmrc.gov.uk/api-documentation/docs/reference-guide#rate-limiting)

Therefore, the service cannot be used excessively without considering this restriction, which could affect the efficiency of the process at scale.

### 3. VAT Number Ambiguity

Things became increasingly complicated as my research progressed.

Initially, I assumed that each company had its own unique VAT number. However, I discovered two distinct situations in which the same VAT number can appear under different company names.

#### First Case — Company Name Changes

One example is **Jumar Technology Limited**, which appeared in an MHRA report from April 2025 with VAT number `318799157`. [MHRA spending report, April 2025](https://www.gov.uk/csv-preview/685abe81db207fc18744d63d/01_MHRA_spending_over__25_000_data_for_April_2025.csv)

In another MHRA report from June 2026, the same VAT number was associated with **TXP Technology Limited**. [MHRA spending report, June 2026](https://www.gov.uk/csv-preview/6a7aeb0baadaaddf89b6e3d1/03_MHRA_spending_over__25_000_data_for_June_2026.csv)

Checking the company's history in Companies House confirmed that it changed its name on August 22, 2025, while maintaining the same legal identity (company number `11786401`). [Companies House company history](https://find-and-update.company-information.service.gov.uk/company/11786401)

#### Second Case — VAT Groups

Multiple legally distinct companies can share the same VAT number if they belong to a VAT Group. [HMRC guidance on group registration](https://www.gov.uk/guidance/vat-registration-for-groups-divisions-and-joint-ventures)

When two different company names are associated with the same VAT number, we cannot determine from that information alone whether a company has changed its name or whether the companies belong to the same VAT Group.

**Is there a publicly available indicator that can reliably identify whether a company belongs to a VAT Group?**

### 4. Companies House and MHRA — Useful Sources for Identification and Discovery

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

### 5. Data Volatility

Another important factor is the high annual turnover of VAT registrations.

HMRC reported approximately **234,000 new VAT registrations and 218,000 deregistrations** for the 2024–2025 financial year. [HMRC annual UK VAT statistics](https://www.gov.uk/government/statistics/value-added-tax-vat-annual-statistics/annual-uk-vat-statistics-2023-to-2024-commentary)

This indicates that a database built only once can quickly become outdated.

Therefore, continuous data updates are necessary.

### 6. What the Discovery Paths Returned

- **MHRA.** Running `python src/pilot.py discover` against the April 2025 and June 2026 reports produced three candidate rows for two companies in the 30-company sample. Both company–VAT associations were later confirmed. The second Phoenix Software row repeated the same association in a different month. This gave me a source that worked, with a limited reach on the sample. [Candidate rows](data/mhra-candidates.csv) · [Verification log](data/hmrc-checks.csv)
- **Company websites.** Integrity360's contracting-entity table looked promising because it had a dedicated VAT column and identified the exact UK company number, `03538529`. The UK VAT cell was blank, while several other countries had a number. That path yielded no UK candidate for this supplier. [Integrity360 entity table](https://www.integrity360.com/entitytable) · [Website search log](data/website-search.csv)

### 7. Conclusion

My research confirmed that VAT numbers can be discovered through publicly available sources, but the process is more complicated than I initially expected.

The main challenges identified are commercial usage restrictions, automated verification limitations, ambiguity between companies, and the need for continuous data updates.

I identified sources that could contribute both to VAT number discovery and company identity verification. However, it remains unclear how efficiently this approach could be applied at scale.

The proof of concept put the discovery paths to the test on an independently drawn supplier sample and used HMRC checks to establish which associations could be confirmed. [Part 2 — Proof of Concept](#part-2-proof-of-concept)

## Part 2 Proof of Concept

### Sample and method

The pilot drew a sample from the September 2026 Contracts Finder snapshot before looking up VAT numbers for those suppliers. The 29 published daily files contained 2,716 award releases. The script kept suppliers on active awards with a usable Companies House number, deduplicated by that number, and randomly selected 30 from 599 eligible identifiers with seed `202609`. The sample contained 23 service suppliers and seven goods suppliers. It covers identifiable public-contract suppliers in the selected month, with a tilt toward services. [Contracts Finder snapshot](https://www.data.gov.uk/dataset/38fbd6d7-af09-4a4e-8308-24bda1aec205/contracts-finder-notices-09-20261) · [Sample](data/sample.csv)

The Python script matched supplier names against the two MHRA reports identified in [Part 1](#part-1-research). It ignored case and punctuation and treated `Limited` and `Ltd` alike. It accepted nine-digit candidates after removing spaces, hyphens and an optional `GB` prefix. The website search covered the remaining firms, with targeted follow-ups when the first results did not identify the right entity. The search log records the pages and unsuccessful searches. [MHRA candidate rows](data/mhra-candidates.csv) · [Website search log](data/website-search.csv)

Every distinct candidate went through HMRC's public checker on 12 November 2026. The verification log compares the returned legal name and postcode with Companies House and the source that published the number. A confirmed link requires a valid VAT number and evidence tying it to the sampled legal entity. [HMRC checker](https://www.gov.uk/check-uk-vat-number) · [Verification log](data/hmrc-checks.csv)

### Results

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

### Where the checks mattered

- **Tunstall and Gleeds.** Tunstall Healthcare (UK) published a number that HMRC returned under Tunstall Group Ltd. Companies House corroborated corporate control. Gleeds' site published the number of Gleeds LLP, while the sampled firm was Gleeds Cost Management Limited. Both links remain inconclusive because the evidence did not establish shared VAT registration. [Tunstall terms](https://shop.tunstall.co.uk/terms) · [Tunstall ownership record](https://find-and-update.company-information.service.gov.uk/company/01332249/persons-with-significant-control) · [Gleeds terms](https://www.gleeds.com/en/terms-and-conditions/)
- **Bhuku and Allotrope.** Bhuku's site labelled its eight-digit Companies House number as VAT, so the value failed the format check. Allotrope stated it was VAT-registered and did not publish a number on the page reviewed. [Bhuku terms](https://ma-mix.com/terms-of-use/) · [Bhuku Companies House profile](https://find-and-update.company-information.service.gov.uk/company/15547198) · [Allotrope Scientific](https://www.allotrope.tech/about)

The local sampling, MHRA matching and reporting commands took about 1.44 seconds combined in one run with the source files already downloaded. The pilot required website searches for 28 suppliers and seven HMRC checks. Manual time per company was not logged. Part 3 uses the counts to identify where to measure labour in the next batch. [Part 3 — Scaling with Real Resources](#part-3-scaling-with-real-resources)

### Reproduction

Run `python src/pilot.py report` to recompute the results from the recorded evidence. The [run instructions](src/README.md) also show how to regenerate the sample and MHRA candidates.

## Part 3 Scaling with Real Resources

### What the customer receives

I would start with the customer's supplier list and return a CSV they can import into their procurement system. Each row keeps the customer's supplier ID. A confirmed row includes the legal name, Companies House number where available, VAT number, verification date and evidence source. Other rows show whether the search yielded no candidate, the association is under review or a candidate was rejected. The VAT field stays blank in those cases.

I sketched five responsibilities before researching the problem. I would keep those responsibilities and define what each team hands off. The most consequential decision is whether a VAT number can safely be linked to the supplier that issued an invoice. [Initial Hypotheses](initial-hypotheses.md)

### How I would organise the teams

#### 1. Source evaluation

This team decides which sources the product can use and in what order. For each source, it checks commercial reuse rights, available fields and how recent the information is. It tests the source on the same supplier sample as the alternatives and measures how many **additional confirmed associations** it produces, how many cases need extra evidence and how much work it takes to maintain. Two reports that repeat the same association contribute one confirmation to coverage.

The team hands over a list of approved sources and instructions for using each one. Structured reports can be processed in batches. Company-site searches cover suppliers that still lack a confirmed VAT number. I would consider licensing company or domain data if a trial shows that it finds enough additional firms or saves enough search time to justify the licence. [Part 1 findings](#part-1-research)

#### 2. Data collection

For each candidate, this team records the original value, its standardised form, the source, the date and where in the document the value appeared. A format check catches cases like Bhuku, where a company number was labelled as VAT. If two sources propose different VAT numbers for the same supplier, the team keeps both observations with their respective evidence. [Website search log](data/website-search.csv)

The team tracks missing fields and access errors separately. If a report changes its column layout, it pauses that import until the mapping has been checked. Rerunning a batch should produce one copy of each observation. The handoff is a set of candidates with traceable evidence and a list of suppliers for which collection needs to be retried.

#### 3. VAT and legal entity verification

This team decides whether a VAT number applies to **the legal entity in the customer's supplier list**. It checks the number with HMRC and compares the returned name and address with the customer's record, Companies House and the source document. If HMRC approves the proposed production use, I would queue requests within the documented limit. Each number needs one HMRC check per batch, while each supplier association needs its own decision. [HMRC API documentation](https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/vat-registered-companies-api/2.0) · [HMRC rate limits](https://developer.service.hmrc.gov.uk/api-documentation/docs/reference-guide#rate-limiting)

- **Different names.** The team checks whether the names appear under the same Companies House number and which name was in use when the document was issued. It uses the HMRC result and other evidence to assess the current association. The earlier name remains useful when matching historical invoices. [Jumar to TXP name change](#first-case--company-name-changes)
- **A number held by another group entity.** The team identifies the entity returned by HMRC and looks for explicit evidence that the supplier is covered by that VAT registration. A shared address or an ownership link is a reason to investigate. Documented confirmation of VAT group membership from the supplier could resolve the case. Tunstall shows where I would hold the association for review. [Pilot verification log](data/hmrc-checks.csv)
- **Conflicting evidence.** The team compares document dates and looks for a trading name, a different correspondence address or a separate legal entity. If two numbers remain plausible, an analyst records which evidence is missing. A temporary HMRC error puts the case back in the verification queue.

The team hands off a verdict, a verification date and the reason for the decision. That gives the integration team enough information to publish a result or ask the client or supplier for a specific piece of evidence.

#### 4. Delivery and integration

This team checks that every input supplier ID has an outcome and prepares a CSV with a stable set of fields. Later deliveries include a change file showing newly confirmed, corrected and withdrawn associations. Reimporting the same batch updates the same supplier IDs. When a proposed VAT differs from one already held by the customer, the team sends the conflict for review before overwriting the record.

When two verified suppliers share a group VAT number, the export keeps both rows and flags the shared number. The customer may also need the legal name or address on the invoice before it can match the invoice automatically to one supplier.

#### 5. Maintenance and quality

This team schedules rechecks based on the age of the evidence. A verified name change, a new source record or a customer report of a mismatched invoice can trigger an earlier review. A verified name change updates the current name and preserves the previous one. If a recheck confirms that an association is no longer valid, the team withdraws it from the current export and sends the customer a correction. If the checker is temporarily unavailable, the team retains the last verification date and queues the row for another check.

I would monitor confirmed coverage by source, the age of the last check, the review backlog and the errors found through audit. The team would audit samples of delivered associations and of suppliers with no result. Where the customer can share invoices, the team can use them as independent evidence to look for incorrect links and missed candidates.

### Rollout, capacity and cost

I would start with a batch drawn from several supplier categories in the customer's list. I would add sources one at a time on the same batch, measuring additional confirmations and auditing the associations each source adds. This would show which sources increase coverage at an acceptable level of review effort. In the pilot, 28 of 30 suppliers needed a company-site search. Two of the seven associations checked at HMRC remained inconclusive. I expect evidence discovery and entity review to constrain throughput first, and would test that on the customer batch. [Part 2 results](#part-2-proof-of-concept)

My initial sketch proposed at least two people per team. I would now allocate people by the workload measured in the customer batch, starting with structured source integration and review of ambiguous associations. I would time discovery, verification and manual review separately, then calculate cost per company processed from actual staff time, infrastructure and licence costs. The pilot logged the number of searches and checks. A timed customer batch is needed to put a price on the manual work.

## Beyond the UK

### A common workflow for different markets

In my initial sketch I proposed a process I would also use in other countries. I would select sources, collect candidate numbers and their evidence, verify the link to the legal entity, deliver confirmed associations and keep them current. This can serve as a **universal working template**. For each market, I would adapt the sources, the identifiers and the evidence required before release. The customer would receive the same kind of result, including the verification date and the reason an association was confirmed or held for review. [Initial Hypotheses](initial-hypotheses.md) · [Part 3](#part-3-scaling-with-real-resources)

### Germany compared with the UK

**Where to look.** For German suppliers I would start with the official website's *Impressum*, or legal notice. Section 5 of the German Digital Services Act lists disclosures for providers in scope, including register details and specified tax identifiers when held. The UK also requires disclosures for online services in scope. The advantage I would test in Germany is whether a predictably named legal notice makes the relevant information easier to find together. SAP's German notice, for example, lists the register details and VAT number under **SAP Deutschland SE & Co. KG** and names **SAP SE** separately as its general partner. The page needs to be read at legal entity level. [Germany's Digital Services Act, Section 5](https://www.gesetze-im-internet.de/ddg/__5.html) · [UK regulation 6](https://www.legislation.gov.uk/uksi/2002/2013/regulation/6) · [SAP's German legal notice](https://www.sap.com/germany/about/legal/impressum.html)

**What to extract.** I would look for the label `USt-IdNr.` and store the domestic tax number (`Steuernummer`) and business identification number (`W-IdNr.`) separately if needed. To resolve the company, I would check the legal name and the German commercial register details, including the court, register type and registration number. [BZSt VAT identification number](https://bzst.de/DE/Unternehmen/Identifikationsnummern/Umsatzsteuer-Identifikationsnummer/umsatzsteuer-identifikationsnummer_node.html) · [BZSt business identification number](https://bzst.de/DE/Unternehmen/Identifikationsnummern/Wirtschafts-Identifikationsnummer/FAQ/faq_widnr.html) · [German Company Register](https://www.unternehmensregister.de/en/howto/register-information)

**What verification proves.** The UK checker returns the registered business name and address for a valid number. VIES checks registration for intra-EU transactions, and the identity details available depend on the member state. If the response provides only validity, I would use the legal notice or a supplier document to substantiate the link to the company separately. A negative VIES result can also mean the number has not been activated for intra-EU transactions. I would record the VIES result and the identity evidence as distinct facts. [HMRC checker](https://www.gov.uk/check-uk-vat-number) · [European Commission VIES guidance](https://europa.eu/youreurope/business/finance-and-tax/vat/check-vat-number-vies/index_en.htm) · [Eurostat manual](https://ec.europa.eu/eurostat/documents/3859598/22913847/KS-01-26-006-EN-N.pdf/160372c2-0c82-7bb8-7558-70b11572cce9?t=1769182372314&version=1.0)

### Estonia as a direct lookup example

The Estonian Business Register's downloadable data includes the legal name, registry code and VAT number where available. The tax authority also accepts the registry code as a search input and can return the VAT number and registration and deletion dates. I would start with the company registry code and reserve website searches for exceptions. The official sources do much of the discovery and identity matching work. [Estonian Business Register open data](https://avaandmed.ariregister.rik.ee/en/downloading-open-data) · [Estonian Tax and Customs Board VAT lookup](https://www.emta.ee/en/business-client/taxes-and-payment/value-added-tax/registration-vat-payer/vat-number-validation)

### Market priorities

For the UK, I would treat discovery as the main obstacle. In Germany, the legal notice gives the search a predictable starting point. The harder cases involve distinguishing similar identifiers or proving that a valid number applies to the exact supplier. I would test a German sample to see how often a useful legal notice is available and how many associations require additional evidence.

If customer demand were comparable, I would start with a market such as Estonia where official data already links companies to available VAT registrations. For Germany, the rollout would depend on the customer's supplier volume and how many associations a pilot confirms with the available sources and review capacity.
