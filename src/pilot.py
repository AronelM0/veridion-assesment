"""Run the VAT discovery pilot with Python's standard library and local CSVs."""

import argparse
import csv
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INPUTS = DATA / "local"
MONTH = "2026-09"
PUBLISHED_DAYS = tuple(day for day in range(1, 31) if day != 27)
SAMPLE_SIZE = 30
SEED = 202609
RELEASE = "releases/0"
CONTRACTS_FINDER = "https://cdp-sirsi-production-cfs-471112843276.s3.eu-west-2.amazonaws.com/Harvester-new"
MHRA_REPORTS = {
    "2025-04": "https://www.gov.uk/csv-preview/685abe81db207fc18744d63d/01_MHRA_spending_over__25_000_data_for_April_2025.csv",
    "2026-06": "https://www.gov.uk/csv-preview/6a7aeb0baadaaddf89b6e3d1/03_MHRA_spending_over__25_000_data_for_June_2026.csv",
}
SAMPLE_FIELDS = ("company_number", "company_name", "award_postcode", "category", "release_url")
CANDIDATE_FIELDS = ("company_number", "vat_number", "report_month", "supplier", "postcode", "transaction", "source_url")
WEBSITE_FIELDS = ("company_number", "outcome", "observed_value", "source_url", "note")
CHECK_FIELDS = (
    "company_number", "vat_number", "checked_utc", "hmrc_result", "registered_name",
    "registered_postcode", "verdict", "identity_source", "note",
)
RESULT_FIELDS = ("company_number", "company_name", "status", "confirmed_vat", "source")


def read_csv(path, required_fields):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = set(required_fields) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path.name} is missing columns: {', '.join(sorted(missing))}")
        yield from reader


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fetch_sources():
    sources = {}
    for day in PUBLISHED_DAYS:
        date = f"{MONTH}-{day:02d}"
        sources[INPUTS / "contracts-finder" / f"{date}.csv"] = (
            f"{CONTRACTS_FINDER}/{MONTH}/Contracts%20Finder%20OCDS%20{date}.csv"
        )
    for month, url in MHRA_REPORTS.items():
        sources[INPUTS / f"mhra-{month}.csv"] = url.replace(
            "www.gov.uk/csv-preview/", "assets.publishing.service.gov.uk/media/"
        )
    for path, url in sources.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(url, timeout=30) as response:
            payload = response.read()
        path.write_bytes(payload)
    print(f"Downloaded {len(sources)} source files into {INPUTS.relative_to(ROOT)}")


def sample_companies():
    companies = {}
    award_rows = 0
    for day in PUBLISHED_DAYS:
        date = f"{MONTH}-{day:02d}"
        path = INPUTS / "contracts-finder" / f"{date}.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames or ()
            if not fields:
                continue
            if "uri" not in fields or f"{RELEASE}/tag/0" not in fields:
                raise ValueError(f"{path.name} does not have the Contracts Finder schema")
            party_paths = [
                field.removesuffix("/identifier/scheme")
                for field in fields
                if re.fullmatch(r"releases/0/parties/\d+/identifier/scheme", field)
            ]
            supplier_fields = [
                field for field in fields
                if re.fullmatch(r"releases/0/awards/\d+/suppliers/\d+/id", field)
            ]
            for row in reader:
                if row[f"{RELEASE}/tag/0"] != "award":
                    continue
                award_rows += 1
                award_suppliers = {
                    row[field] for field in supplier_fields
                    if row[field] and row.get(field.split("/suppliers/")[0] + "/status") == "active"
                }
                for party in party_paths:
                    if row[f"{party}/identifier/scheme"] != "GB-COH":
                        continue
                    if row.get(f"{party}/id") not in award_suppliers:
                        continue
                    number = row.get(f"{party}/identifier/id", "").strip().upper()
                    if not re.fullmatch(r"(?:[0-9]{8}|[A-Z]{2}[0-9]{6})", number):
                        continue
                    name = (row.get(f"{party}/identifier/legalName") or row.get(f"{party}/name", "")).strip()
                    if not name:
                        continue
                    companies.setdefault(number, {
                        "company_number": number,
                        "company_name": name,
                        "award_postcode": row.get(f"{party}/address/postalCode", "").strip(),
                        "category": row.get(f"{RELEASE}/tender/mainProcurementCategory", ""),
                        "release_url": row["uri"],
                    })
    selected = random.Random(SEED).sample(sorted(companies), SAMPLE_SIZE)
    write_csv(DATA / "sample.csv", SAMPLE_FIELDS, (companies[number] for number in selected))
    print(f"{award_rows} award releases, {len(companies)} eligible companies, {len(selected)} sampled")


def name_key(name):
    words = re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", name).casefold())
    if words and words[-1] == "limited":
        words[-1] = "ltd"
    return " ".join(words)


def vat_key(value):
    number = re.sub(r"[\s-]", "", value.upper()).removeprefix("GB")
    return number if re.fullmatch(r"[0-9]{9}", number) else ""


def find_mhra_candidates():
    sample = list(read_csv(DATA / "sample.csv", SAMPLE_FIELDS))
    fields = ("Supplier", "Supplier VAT registration number", "Postcode", "Transaction number")
    by_name = {}
    for month, url in MHRA_REPORTS.items():
        for row in read_csv(INPUTS / f"mhra-{month}.csv", fields):
            by_name.setdefault(name_key(row["Supplier"]), []).append((month, url, row))

    candidates = {}
    for company in sample:
        number = company["company_number"]
        for month, url, row in by_name.get(name_key(company["company_name"]), ()):
            vat = vat_key(row["Supplier VAT registration number"])
            if vat:
                candidates.setdefault((number, vat, month), {
                    "company_number": number,
                    "vat_number": vat,
                    "report_month": month,
                    "supplier": row["Supplier"].strip(),
                    "postcode": row["Postcode"].strip(),
                    "transaction": row["Transaction number"].strip(),
                    "source_url": url,
                })
    write_csv(DATA / "mhra-candidates.csv", CANDIDATE_FIELDS, candidates.values())
    print(f"{len(candidates)} candidate rows for {len({key[0] for key in candidates})} sampled companies")


def report_results():
    sample = {
        row["company_number"]: row["company_name"]
        for row in read_csv(DATA / "sample.csv", SAMPLE_FIELDS)
    }
    if len(sample) != SAMPLE_SIZE:
        raise ValueError(f"Expected {SAMPLE_SIZE} distinct companies")

    sources = defaultdict(set)
    for row in read_csv(DATA / "mhra-candidates.csv", CANDIDATE_FIELDS):
        number, vat = row["company_number"], row["vat_number"]
        if number not in sample or not vat or vat_key(vat) != vat:
            raise ValueError(f"Invalid MHRA candidate for {number}")
        sources[(number, vat)].add("MHRA")

    website_outcomes = {}
    for row in read_csv(DATA / "website-search.csv", WEBSITE_FIELDS):
        number = row["company_number"]
        if number not in sample or number in website_outcomes:
            raise ValueError(f"Unexpected or duplicate website review for {number}")
        outcome = row["outcome"]
        if outcome not in {"candidate", "no_candidate", "no_identified_site", "source_unavailable", "format_rejected"}:
            raise ValueError(f"Unrecognized website outcome for {number}: {outcome}")
        website_outcomes[number] = outcome
        if outcome == "candidate":
            vat = vat_key(row["observed_value"])
            if not vat or not row["source_url"]:
                raise ValueError(f"Missing VAT number or website evidence for {number}")
            sources[(number, vat)].add("company website")

    checks = {}
    for row in read_csv(DATA / "hmrc-checks.csv", CHECK_FIELDS):
        key = (row["company_number"], row["vat_number"])
        verdict = row["verdict"]
        if key not in sources or key in checks:
            raise ValueError(f"Unexpected or duplicate HMRC check for {key}")
        if verdict not in {"confirmed", "rejected", "inconclusive"} or not row["checked_utc"] or not row["note"]:
            raise ValueError(f"Missing HMRC evidence for {key}")
        if verdict == "confirmed" and (
            row["hmrc_result"] != "valid" or not row["registered_name"] or not row["identity_source"]
        ):
            raise ValueError(f"A confirmed link needs a valid number and identity evidence for {key}")
        checks[key] = verdict

    if set(checks) != set(sources):
        raise ValueError("Each unique company–VAT candidate needs an HMRC check")
    verdicts_by_company = defaultdict(dict)
    mhra_confirmed = set()
    for (number, vat), verdict in checks.items():
        verdicts_by_company[number][vat] = verdict
        if verdict == "confirmed" and "MHRA" in sources[(number, vat)]:
            mhra_confirmed.add(number)
    if (set(sample) - mhra_confirmed) - set(website_outcomes):
        raise ValueError("A website search is required for every company without a confirmed MHRA match")

    rows = []
    for number, name in sample.items():
        verdicts = verdicts_by_company[number]
        confirmed = [vat for vat, verdict in verdicts.items() if verdict == "confirmed"]
        vat = ""
        source = ""
        if len(confirmed) == 1 and "inconclusive" not in verdicts.values():
            status = "confirmed"
            vat = confirmed[0]
            source = " + ".join(sorted(sources[(number, vat)]))
        elif confirmed or "inconclusive" in verdicts.values():
            status = "inconclusive"
        else:
            status = "rejected" if verdicts else "no_candidate"
        rows.append({
            "company_number": number, "company_name": name, "status": status,
            "confirmed_vat": vat, "source": source,
        })

    write_csv(DATA / "results.csv", RESULT_FIELDS, rows)
    company_counts = Counter(row["status"] for row in rows)
    check_counts = Counter(checks.values())
    resolved = check_counts["confirmed"] + check_counts["rejected"]
    print(f"Verified coverage: {company_counts['confirmed']}/{len(sample)}")
    print(f"Confirmed by MHRA / company website: "
          f"{sum('MHRA' in row['source'] for row in rows)}/"
          f"{sum(row['source'] == 'company website' for row in rows)}")
    print(f"Candidate links checked: {len(checks)}")
    print(f"Rejected share among conclusive checks: {check_counts['rejected']}/{resolved}")
    print(f"Inconclusive links: {check_counts['inconclusive']}")
    print(f"Companies without a candidate sent to HMRC: {company_counts['no_candidate']}")
    print(f"Website reviews: {len(website_outcomes)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    steps = {
        "fetch": fetch_sources,
        "sample": sample_companies,
        "discover": find_mhra_candidates,
        "report": report_results,
    }
    parser.add_argument("step", choices=steps)
    step = parser.parse_args().step
    csv.field_size_limit(16 * 1024 * 1024)
    steps[step]()


if __name__ == "__main__":
    main()
