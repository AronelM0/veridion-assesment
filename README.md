# VAT Identifier Discovery

A Veridion internship challenge on discovering UK company VAT numbers from public sources and assessing how reliably those numbers can be linked to the right legal entities.

## Start here

**[Read Initial Hypotheses first](initial-hypotheses.md)**

This is my first sketch of the workflow, from selecting sources to keeping the register current. I wrote it before investigating the available sources. Part 3 revisits that design in light of the research and pilot.

## Project report

The full report contains the three challenge parts and the optional comparison beyond the UK. [Read the full report](report.md)

- [Part 1 — Research](report.md#part-1-research)
- [Part 2 — Proof of Concept](report.md#part-2-proof-of-concept)
- [Part 3 — Scaling with Real Resources](report.md#part-3-scaling-with-real-resources)
- [Beyond the UK](report.md#beyond-the-uk)

The Python script and the recorded evidence reproduce the pilot results. [Run instructions](src/README.md) · [Pilot data](data/README.md)

## Debate topics

### 1. Would I enumerate checksum-valid numbers and check them with HMRC?

I would use the checksum locally to filter candidates found in source documents. Enumerating numbers that pass the checksum and querying HMRC would likely find some active registrations, including firms outside the customer's list. The checker starts with a number. The customer starts with a supplier and needs evidence linking the two.

My initial sketch left enumeration open as a possible route for discovery or maintenance. I would now make targeted checks for both. Each request would check a candidate backed by evidence from a supplier or a source document. The API's documented purpose and rate limit are further reasons to avoid enumeration. [Initial Hypotheses](initial-hypotheses.md) · [HMRC checker](https://www.gov.uk/check-uk-vat-number) · [HMRC API documentation](https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/vat-registered-companies-api/2.0) · [HMRC rate limits](https://developer.service.hmrc.gov.uk/api-documentation/docs/reference-guide#rate-limiting)

### 2. How would I keep the dataset current?

For each association I would retain the source, the last verification date and its change history. A Companies House name change, a new source document or a discrepancy reported by the customer would trigger a review. I would also schedule rechecks, prioritising older evidence and frequently used suppliers. VAT status can change while the legal name stays the same. HMRC reported approximately 234,000 new registrations and 218,000 deregistrations in the 2024–2025 financial year. [Part 1 research](report.md#part-1-research) · [HMRC annual VAT statistics](https://www.gov.uk/government/statistics/value-added-tax-vat-annual-statistics/annual-uk-vat-statistics-2023-to-2024-commentary)

If a recheck confirms that an association is no longer valid, I would withdraw it from the current export and notify the customer. If the checker is temporarily unavailable, I would retain the last verification date and queue the record for another check. [Maintenance in Part 3](report.md#part-3-scaling-with-real-resources)

### 3. How would I detect errors at scale?

I would regularly audit a random sample of published associations and track results by source. Where available, I would use independent evidence, such as an invoice shared by the customer, to verify that the VAT number applies to the legal entity on the invoice. I would also sample suppliers with no result to look for missed evidence.

In the pilot, zero of five conclusively checked associations were rejected and two remained inconclusive. In production I would report both the error share among resolved audit cases and the share of audits left unresolved. If errors concentrate in one source, I would review the matching rule and revisit the associations already published from that source. [Part 2 results](report.md#part-2-proof-of-concept) · [Part 3 audit plan](report.md#part-3-scaling-with-real-resources)

### 4. Which sources would I exclude or limit in a commercial product?

I would exclude automated extraction from the public OpenCorporates website. I would consider licensed access under an agreement that explicitly permits the intended use and delivery to the customer. [OpenCorporates terms](https://opencorporates.com/terms-of-use/) · [Part 1 research](report.md#part-1-research)

I would use MHRA spending reports and company websites for candidate discovery. A spending report describes transactions in a specific period, and a group website may publish another entity's VAT number, as the Gleeds case showed. I would release an association only after checking the number and its link to the supplier. [Part 2 examples](report.md#part-2-proof-of-concept)
