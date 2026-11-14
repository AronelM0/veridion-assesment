# Part 3 — Scaling with Real Resources

## What the customer receives

I would start with the customer's supplier list and return a CSV they can import into their procurement system. Each row keeps the customer's supplier ID. A confirmed row includes the legal name, Companies House number where available, VAT number, verification date and evidence source. Other rows show whether the search yielded no candidate, the association is under review or a candidate was rejected. The VAT field stays blank in those cases.

I sketched five responsibilities before researching the problem. I would keep those responsibilities and define what each team hands off. The most consequential decision is whether a VAT number can safely be linked to the supplier that issued an invoice. [Initial Hypotheses](initial-hypotheses.md)

## How I would organise the teams

### 1. Source evaluation

This team decides which sources the product can use and in what order. For each source, it checks commercial reuse rights, available fields and how recent the information is. It tests the source on the same supplier sample as the alternatives and measures how many **additional confirmed associations** it produces, how many cases need extra evidence and how much work it takes to maintain. Two reports that repeat the same association contribute one confirmation to coverage.

The team hands over a list of approved sources and instructions for using each one. Structured reports can be processed in batches. Company-site searches cover suppliers that still lack a confirmed VAT number. I would consider licensing company or domain data if a trial shows that it finds enough additional firms or saves enough search time to justify the licence. [Part 1 findings](research.md)

### 2. Data collection

For each candidate, this team records the original value, its standardised form, the source, the date and where in the document the value appeared. A format check catches cases like Bhuku, where a company number was labelled as VAT. If two sources propose different VAT numbers for the same supplier, the team keeps both observations with their respective evidence. [Website search log](data/website-search.csv)

The team tracks missing fields and access errors separately. If a report changes its column layout, it pauses that import until the mapping has been checked. Rerunning a batch should produce one copy of each observation. The handoff is a set of candidates with traceable evidence and a list of suppliers for which collection needs to be retried.

### 3. VAT and legal entity verification

This team decides whether a VAT number applies to **the legal entity in the customer's supplier list**. It checks the number with HMRC and compares the returned name and address with the customer's record, Companies House and the source document. If HMRC approves the proposed production use, I would queue requests within the documented limit. Each number needs one HMRC check per batch, while each supplier association needs its own decision. [HMRC API documentation](https://developer.service.hmrc.gov.uk/api-documentation/docs/api/service/vat-registered-companies-api/2.0) · [HMRC rate limits](https://developer.service.hmrc.gov.uk/api-documentation/docs/reference-guide#rate-limiting)

- **Different names.** The team checks whether the names appear under the same Companies House number and which name was in use when the document was issued. It uses the HMRC result and other evidence to assess the current association. The earlier name remains useful when matching historical invoices. [Jumar to TXP name change](research.md#first-case--company-name-changes)
- **A number held by another group entity.** The team identifies the entity returned by HMRC and looks for explicit evidence that the supplier is covered by that VAT registration. A shared address or an ownership link is a reason to investigate. Documented confirmation of VAT group membership from the supplier could resolve the case. Tunstall shows where I would hold the association for review. [Pilot verification log](data/hmrc-checks.csv)
- **Conflicting evidence.** The team compares document dates and looks for a trading name, a different correspondence address or a separate legal entity. If two numbers remain plausible, an analyst records which evidence is missing. A temporary HMRC error puts the case back in the verification queue.

The team hands off a verdict, a verification date and the reason for the decision. That gives the integration team enough information to publish a result or ask the client or supplier for a specific piece of evidence.

### 4. Delivery and integration

This team checks that every input supplier ID has an outcome and prepares a CSV with a stable set of fields. Later deliveries include a change file showing newly confirmed, corrected and withdrawn associations. Reimporting the same batch updates the same supplier IDs. When a proposed VAT differs from one already held by the customer, the team sends the conflict for review before overwriting the record.

When two verified suppliers share a group VAT number, the export keeps both rows and flags the shared number. The customer may also need the legal name or address on the invoice before it can match the invoice automatically to one supplier.

### 5. Maintenance and quality

This team schedules rechecks based on the age of the evidence. A verified name change, a new source record or a customer report of a mismatched invoice can trigger an earlier review. A verified name change updates the current name and preserves the previous one. If a recheck confirms that an association is no longer valid, the team withdraws it from the current export and sends the customer a correction. If the checker is temporarily unavailable, the team retains the last verification date and queues the row for another check.

I would monitor confirmed coverage by source, the age of the last check, the review backlog and the errors found through audit. The team would audit samples of delivered associations and of suppliers with no result. Where the customer can share invoices, the team can use them as independent evidence to look for incorrect links and missed candidates.

## Rollout, capacity and cost

I would start with a batch drawn from several supplier categories in the customer's list. I would add sources one at a time on the same batch, measuring additional confirmations and auditing the associations each source adds. This would show which sources increase coverage at an acceptable level of review effort. In the pilot, 28 of 30 suppliers needed a company-site search. Two of the seven associations checked at HMRC remained inconclusive. I expect evidence discovery and entity review to constrain throughput first, and would test that on the customer batch. [Part 2 results](proof-of-concept.md)

My initial sketch proposed at least two people per team. I would now allocate people by the workload measured in the customer batch, starting with structured source integration and review of ambiguous associations. I would time discovery, verification and manual review separately, then calculate cost per company processed from actual staff time, infrastructure and licence costs. The pilot logged the number of searches and checks. A timed customer batch is needed to put a price on the manual work.
