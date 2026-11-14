# Initial Hypotheses & System-Level Thinking

*The following ideas represent my initial perspective on the problem, formulated before conducting any research or experiments. My goal at this stage is to approach the challenge from a system-level perspective, establish an initial framework, and later compare these assumptions with real-world findings. I expect some of these ideas to evolve as I investigate the available data sources, technical limitations, and practical costs.*

## 1. Initial Observations

Before considering any implementation, I believe the problem should be divided into several distinct stages, each addressing a specific responsibility.

1. **Auxiliary Database:** I would establish an auxiliary database to collect raw data from different sources, regardless of whether the information has already been verified.

2. **Official Database:** A separate, final database would contain only information that has passed the necessary validation checks and can be considered sufficiently reliable.

3. **Automated Verification:** The process of checking VAT registration numbers through HMRC should be automated to reduce repetitive manual work and support larger-scale operations.

4. **Limitations of Brute Force:** Since companies register, deregister, and change over time, generating VAT numbers and checking their existence may not be an efficient starting point. Even if this method could identify registered entities, it could require substantial computational and operational resources. I would initially treat brute force as a lower-priority approach, potentially worth reconsidering for maintenance or supplementary discovery.

5. **The Ideal Data Source:** In an ideal scenario, HMRC itself would provide and continuously update an authoritative database connecting VAT registrations to their respective businesses. Such a source would significantly reduce the uncertainty involved in discovering VAT identifiers.

However, I believe complete coverage is unlikely to be achievable through publicly accessible information alone.

Not every company is VAT-registered, some registered businesses may not publicly disclose their VAT numbers, and certain businesses may operate for relatively short periods.

This creates an important distinction between a VAT number that does not exist and one that simply cannot be discovered.

In my initial view, only an authoritative institution such as HMRC would be in a position to provide a sufficiently complete and continuously updated picture of registered businesses. An independently constructed dataset would therefore need to acknowledge its coverage limitations.

## 2. Proposed Data Acquisition Process

My initial approach would follow a structured pipeline:

**Stage 1 — Source Ranking**

After identifying potential sources, such as company websites, public documents, VAT-related declarations, or other discovery methods, I would classify them according to their reliability.

The objective would be to prioritize sources that are most likely to provide accurate VAT information.

**Stage 2 — Data Extraction and Cost Evaluation**

Data would be extracted from the most reliable sources first, gradually expanding toward lower-ranked sources when resources permit.

However, source reliability would not be the only consideration. The time, computational effort, and financial costs associated with extraction should also influence prioritization.

A source providing more VAT numbers may not necessarily be preferable if obtaining those numbers requires disproportionately greater resources.

**Stage 3 — Raw Data Storage**

All collected information would first be stored in the auxiliary database, preserving it for subsequent processing and verification.

**Stage 4 — HMRC Verification**

The collected VAT numbers would be checked through HMRC.

Records that pass the required validation process would then be forwarded for integration into the official database.

**Stage 5 — Database Maintenance**

A continuous maintenance process would monitor changes in company information and update the official database when necessary.

The purpose of this stage would be to avoid treating the dataset as a one-time collection and instead maintain it as an evolving information asset.

## 3. Initial Proposal for Scaling with Real Resources

Assuming that sufficient resources were available, I would initially divide the responsibilities described above among five specialized teams, each consisting of at least two people.

The purpose of this structure would be to allow different stages of the pipeline to operate in parallel while maintaining clear responsibilities.

### Team 1 — Source Discovery and Reliability Assessment

I would divide this team into two subgroups.

The first subgroup would focus on discovering potential sources of VAT information.

The second would document where the information originated and continuously evaluate the reliability of each source based on the accuracy of the data obtained.

This would allow source rankings to evolve as more evidence becomes available.

### Team 2 — Data Extraction and Resource Optimization

This team would also be divided into two subgroups.

One subgroup would focus on extracting data according to the source rankings established earlier.

The other would measure the resources required for extraction, including execution time, technical difficulty, computational requirements, and financial costs.

The objective would be to evaluate the trade-offs between different sources.

For example, one source might provide substantially more VAT numbers but require several days of processing, while another might produce fewer results at a significantly lower cost.

These differences would help determine which sources are worth prioritizing.

### Team 3 — Automated VAT Verification

This team would focus on developing and maintaining the automated verification process using HMRC.

Its responsibility would be to process candidate VAT numbers, perform the required checks, and forward validated records for integration into the official database.

### Team 4 — Data Integrity and Database Integration

This team would receive the validated records and ensure that they are correctly transferred and integrated into the official database.

An important concern would be preventing accidental data modifications during the process.

For example, integrity-checking mechanisms such as CRC could be considered for detecting accidental differences between transferred data and their original representation.

The purpose would not be to establish whether a VAT number belongs to a particular company, but to ensure that already validated information remains unchanged during transfer and storage.

### Team 5 — Supervision and Continuous Maintenance

The fifth team would supervise the overall process and develop mechanisms to avoid repeatedly processing unchanged records.

If a company or its VAT registration information had not changed, unnecessary repeated work should be minimized.

When relevant changes are detected, the corresponding information would be re-evaluated and the official database updated accordingly.

This would allow the system to focus resources on new or modified information rather than continuously repeating the entire discovery process.

## 4. Long-Term Perspective

I believe the overall structure described above could potentially be adapted to other countries.

Although each country may have different registration systems, verification procedures, and legal requirements, the general stages of source discovery, data extraction, validation, integration, and maintenance could remain relevant.

The exact implementation would depend on the availability and characteristics of each country's business identifiers.

Another potential advantage of this organizational model is specialization.

By repeatedly working on the same stages, team members could develop deeper expertise in their respective areas, potentially improving operational efficiency over time.

At the same time, dividing the process into specialized responsibilities could allow several stages to run in parallel, subject to the available infrastructure and resources.

## 5. Initial Conclusion

At this stage, I see the challenge as more than a technical data extraction problem.

Building a useful VAT dataset would require identifying trustworthy sources, evaluating the economic feasibility of collecting their information, maintaining data integrity, and continuously adapting to changes in the underlying business population.

These are initial hypotheses rather than validated conclusions.

The next step is to investigate whether the required VAT information is sufficiently discoverable from public sources and whether the proposed approach can be supported by real evidence.

I intend to revisit these assumptions after completing the research and proof-of-concept stages, identifying which ideas remain valid, which need adjustment, and which may not be practical.