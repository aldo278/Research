import csv
import json
import re
from pathlib import Path

FILINGS_DIR = "sec-edgar-filings"
COMPANIES_CSV = "companies.csv"
DOCUMENT_TYPE = "10-K"
FILE_FORMAT = "txt"


def sanitize_folder_name(name):
    """Remove spaces and special characters to match the organized folder names."""
    return re.sub(r"[^a-zA-Z0-9]", "", name)


def load_company_lookup():
    """Map sanitized company folder names to their CSV info (ticker, company)."""
    lookup = {}
    with open(COMPANIES_CSV, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row.get("company"):
                continue
            key = sanitize_folder_name(row["company"]).lower()
            lookup[key] = {
                "ticker": row["ticker"],
                "company": row["company"],
            }
    return lookup


def parse_header(file_path):
    """Extract SEC SGML header fields from the top of a full-submission file."""
    header = {}
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()

            # Stop once the header section ends
            if "</SEC-HEADER>" in stripped or "</IMS-HEADER>" in stripped:
                break

            if "ACCESSION NUMBER:" in stripped:
                m = re.search(r"ACCESSION NUMBER:\s*(\S+)", stripped)
                if m:
                    header["accession"] = m.group(1)
            elif "CONFORMED SUBMISSION TYPE:" in stripped:
                m = re.search(r"CONFORMED SUBMISSION TYPE:\s*(\S+)", stripped)
                if m:
                    header["doc_type"] = m.group(1)
            elif "FILED AS OF DATE:" in stripped:
                m = re.search(r"FILED AS OF DATE:\s*(\d{8})", stripped)
                if m:
                    header["filed_date"] = m.group(1)
            elif "CENTRAL INDEX KEY:" in stripped and "cik" not in header:
                m = re.search(r"CENTRAL INDEX KEY:\s*(\d+)", stripped)
                if m:
                    header["cik"] = m.group(1)

    return header


def format_filing_date(raw_date):
    """Convert YYYYMMDD to YYYY-MM-DD, or return None."""
    if raw_date and len(raw_date) == 8:
        return f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    return None


def build_source_link(cik, accession):
    """Construct the SEC EDGAR filing index URL."""
    if not cik or not accession:
        return None
    accession_nodash = accession.replace("-", "")
    return (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
        f"{accession_nodash}/{accession}-index.htm"
    )


def process_company(company_path, lookup):
    """Create one metadata JSON per filing in the company's FullText folder."""
    full_text_path = company_path / "FullText"
    metadata_path = company_path / "Metadata"

    if not full_text_path.exists():
        print(f"  No FullText folder for {company_path.name}, skipping")
        return

    metadata_path.mkdir(exist_ok=True)

    info = lookup.get(company_path.name.lower(), {})
    ticker = info.get("ticker")
    company_name = info.get("company", company_path.name)

    for txt_file in sorted(full_text_path.glob("full-submission-*.txt")):
        # Year suffix from filename, e.g. full-submission-22.txt -> 22 -> 2022
        m = re.search(r"full-submission-(\d{2})\.txt", txt_file.name)
        if not m:
            continue
        year_2digit = m.group(1)
        filing_year = int(f"20{year_2digit}")

        header = parse_header(txt_file)
        accession = header.get("accession")
        cik = header.get("cik")
        filed_date = format_filing_date(header.get("filed_date"))

        metadata = {
            "companyName": company_name,
            "ticker": ticker,
            "documentType": header.get("doc_type", DOCUMENT_TYPE),
            "filingYear": filing_year,
            "filingDate": filed_date,
            "sourceLink": build_source_link(cik, accession),
            "accessionNumber": accession,
            "fileFormat": FILE_FORMAT,
        }

        output_file = metadata_path / f"{company_path.name}-{filing_year}-metadata.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        print(f"  Saved {output_file.name}")


def generate_all_metadata():
    """Generate metadata JSON files for every company filing."""
    base_path = Path(FILINGS_DIR)
    if not base_path.exists():
        print(f"Directory not found: {base_path}")
        return

    lookup = load_company_lookup()

    for company_path in sorted(base_path.iterdir()):
        if company_path.is_dir():
            print(f"Processing {company_path.name}...")
            process_company(company_path, lookup)

    print("Metadata extraction complete.")


if __name__ == "__main__":
    generate_all_metadata()
