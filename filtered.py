import re
from pathlib import Path
from bs4 import BeautifulSoup

FILINGS_DIR = "sec-edgar-filings"


def clean_html_text(raw_html):
    """Strip HTML tags and return formatted plain text."""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(" ", strip=True)

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)

    # Split into lines, remove standalone page numbers and empty lines
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = [
        line for line in lines
        if line and not re.match(r"^\d+$", line)
    ]

    return "\n\n".join(cleaned_lines).strip()


def filter_company(company_path):
    """Clean every full-submission.txt in FullText and save to Filtered."""
    full_text_path = company_path / "FullText"
    filtered_path = company_path / "Filtered"
    filtered_path.mkdir(exist_ok=True)

    if not full_text_path.exists():
        print(f"  FullText folder not found for {company_path.name}, skipping")
        return

    for filing_dir in sorted(full_text_path.iterdir()):
        if not filing_dir.is_dir():
            continue

        source_file = filing_dir / "full-submission.txt"
        if not source_file.exists():
            print(f"  full-submission.txt not found in {filing_dir.name}, skipping")
            continue

        accession = filing_dir.name
        output_file = filtered_path / f"{accession}.txt"

        with open(source_file, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()

        cleaned_text = clean_html_text(raw_html)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"  Cleaned {company_path.name}/{accession}")


def filter_all():
    """Process every company folder under sec-edgar-filings."""
    base_path = Path(FILINGS_DIR)
    if not base_path.exists():
        print(f"Directory not found: {base_path}")
        return

    for company_path in sorted(base_path.iterdir()):
        if company_path.is_dir():
            print(f"Processing {company_path.name}...")
            filter_company(company_path)

    print("Filtered files created.")


if __name__ == "__main__":
    filter_all()
