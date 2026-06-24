import re
from bs4 import BeautifulSoup
from pathlib import Path


def clean_html_to_text(raw_html):
    """Strip HTML tags and normalize whitespace from a raw SEC filing."""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(" ", strip=True)
    # Collapse excessive whitespace and normalize line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def find_risk_factors(plain_text):
    """
    Extract the Item 1A Risk Factors section from a plain-text 10-K filing.
    Returns the cleaned text or None if the section cannot be located.
    """
    # Common SEC heading patterns for Item 1A (case-insensitive)
    start_patterns = [
        r"Item\s+1A\.?\s+Risk\s+Factors",
        r"ITEM\s+1A\.?\s+RISK\s+FACTORS",
        r"Item\s+1A\.?\s*Risk\s*Factors",
        r"ITEM\s+1A\.?\s*RISK\s*FACTORS",
    ]

    # End of Item 1A is typically the next item heading
    end_patterns = [
        r"Item\s+1B\.?\s+Unresolved\s+Staff\s+Comments",
        r"ITEM\s+1B\.?\s+UNRESOLVED\s+STAFF\s+COMMENTS",
        r"Item\s+1B\.?",
        r"ITEM\s+1B\.?",
        r"Item\s+2\.?\s+Properties",
        r"ITEM\s+2\.?\s+PROPERTIES",
        r"Item\s+2\.?",
        r"ITEM\s+2\.?",
        r"Item\s+3\.?\s+Legal\s+Proceedings",
        r"ITEM\s+3\.?\s+LEGAL\s+PROCEEDINGS",
    ]

    start_match = None
    for pattern in start_patterns:
        match = re.search(pattern, plain_text, re.IGNORECASE)
        if match:
            start_match = match
            break

    if not start_match:
        return None

    # Slice the text from the start of the heading
    text_after_start = plain_text[start_match.start():]

    end_match = None
    for pattern in end_patterns:
        match = re.search(pattern, text_after_start, re.IGNORECASE)
        if match:
            end_match = match
            break

    if end_match:
        section = text_after_start[:end_match.start()]
    else:
        # If no end marker is found, take everything after the heading
        section = text_after_start

    return section.strip()


def process_filing(filing_path, output_path):
    """Read a single filing, extract Item 1A, and save the cleaned text."""
    try:
        with open(filing_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()
    except Exception as e:
        print(f"  Error reading {filing_path}: {e}")
        return False

    plain_text = clean_html_to_text(raw_html)
    risk_factors = find_risk_factors(plain_text)

    if risk_factors:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(risk_factors)
        print(f"  Saved: {output_path}")
        return True
    else:
        print(f"  Item 1A not found in {filing_path}")
        return False


def filter_all_filings():
    """
    Process every downloaded 10-K filing and save cleaned Item 1A
    Risk Factors sections to a separate output directory.
    """
    base_dir = Path("sec-edgar-filings")
    output_dir = Path("filtered_risk_factors")

    if not base_dir.exists():
        print(f"Filing directory not found: {base_dir}")
        return

    total = 0
    extracted = 0

    for filing_path in sorted(base_dir.rglob("full-submission.txt")):
        total += 1
        # Company is the top-level folder under sec-edgar-filings
        company = filing_path.relative_to(base_dir).parts[0]
        # Accession is the folder containing full-submission.txt
        accession = filing_path.parent.name
        output_file = output_dir / f"{company}_{accession}_item1a.txt"

        print(f"Processing {company} ({accession})...")
        if process_filing(filing_path, output_file):
            extracted += 1

    print("\n" + "=" * 50)
    print(f"Total filings scanned: {total}")
    print(f"Risk Factors extracted: {extracted}")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    filter_all_filings()
