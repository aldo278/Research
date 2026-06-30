import re
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

FILINGS_DIR = "sec-edgar-filings"


def extract_primary_document(raw):
    """
    Pull the main 10-K HTML document out of the SGML full submission.
    A full-submission file contains multiple <DOCUMENT> blocks (HTML, XBRL,
    and binary graphics). Isolating the 10-K document avoids feeding embedded
    binary content to the HTML parser, which can crash it.
    """
    documents = re.findall(r"<DOCUMENT>(.*?)</DOCUMENT>", raw, re.DOTALL | re.IGNORECASE)

    # Prefer the document explicitly typed as 10-K
    for doc in documents:
        type_match = re.search(r"<TYPE>([^\s<]+)", doc, re.IGNORECASE)
        if type_match and type_match.group(1).upper() == "10-K":
            text_match = re.search(r"<TEXT>(.*?)</TEXT>", doc, re.DOTALL | re.IGNORECASE)
            return text_match.group(1) if text_match else doc

    # Fallback: the first document's text body
    if documents:
        text_match = re.search(r"<TEXT>(.*?)</TEXT>", documents[0], re.DOTALL | re.IGNORECASE)
        if text_match:
            return text_match.group(1)

    return raw


def clean_html_to_text(raw_html):
    """Strip HTML tags and normalize whitespace from a raw SEC filing."""
    document_html = extract_primary_document(raw_html)

    soup = None
    try:
        soup = BeautifulSoup(document_html, "html.parser")
    except Exception:
        # Remove SGML marked sections / DOCTYPE that can break html.parser, then retry
        sanitized = re.sub(r"<!\[.*?\]>", "", document_html, flags=re.DOTALL)
        sanitized = re.sub(r"<!DOCTYPE[^>]*>", "", sanitized, flags=re.IGNORECASE)
        try:
            soup = BeautifulSoup(sanitized, "html.parser")
        except Exception:
            # Last resort: strip tags with a regex
            text = re.sub(r"<[^>]+>", " ", document_html)
            text = re.sub(r"[ \t]+", " ", text)
            return text.strip()

    text = soup.get_text(" ", strip=True)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def find_risk_factors(plain_text):
    """
    Extract the Item 1A Risk Factors section from a plain-text 10-K filing.
    Returns the section text or None if it cannot be located.
    """
    start_patterns = [
        r"Item\s+1A\.?\s+Risk\s+Factors",
        r"ITEM\s+1A\.?\s+RISK\s+FACTORS",
        r"Item\s+1A\.?\s*Risk\s*Factors",
        r"ITEM\s+1A\.?\s*RISK\s*FACTORS",
    ]

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

    # Find the last occurrence of the start heading (skips the table-of-contents entry)
    start_match = None
    for pattern in start_patterns:
        matches = list(re.finditer(pattern, plain_text, re.IGNORECASE))
        if matches:
            start_match = matches[-1]
            break

    if not start_match:
        return None

    text_after_start = plain_text[start_match.start():]

    end_match = None
    for pattern in end_patterns:
        match = re.search(pattern, text_after_start[10:], re.IGNORECASE)
        if match:
            end_match = match
            break

    if end_match:
        section = text_after_start[: end_match.start() + 10]
    else:
        section = text_after_start

    return section.strip()


def make_html_copies(full_text_path):
    """Copy each full-submission-YY.txt to a matching .html file in the same folder."""
    for txt_file in sorted(full_text_path.glob("full-submission-*.txt")):
        html_file = txt_file.with_suffix(".html")
        shutil.copyfile(txt_file, html_file)
        print(f"  Copied {txt_file.name} -> {html_file.name}")


def extract_company(company_path):
    """Create HTML copies and extract Item 1A Risk Factors for one company."""
    full_text_path = company_path / "FullText"
    risk_factors_path = company_path / "RiskFactors"

    if not full_text_path.exists():
        print(f"  No FullText folder for {company_path.name}, skipping")
        return

    risk_factors_path.mkdir(exist_ok=True)

    # Step 1: make .html copies of the .txt files
    make_html_copies(full_text_path)

    # Step 2: extract Item 1A from each html copy
    for html_file in sorted(full_text_path.glob("full-submission-*.html")):
        m = re.search(r"full-submission-(\d{2})\.html", html_file.name)
        if not m:
            continue
        filing_year = int(f"20{m.group(1)}")

        output_file = risk_factors_path / f"{company_path.name}-{filing_year}-riskfactors.txt"

        try:
            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                raw_html = f.read()

            plain_text = clean_html_to_text(raw_html)
            risk_factors = find_risk_factors(plain_text)
        except Exception as e:
            print(f"  Error processing {html_file.name}: {e}")
            continue

        if risk_factors:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(risk_factors)
            print(f"  Saved {output_file.name}")
        else:
            print(f"  Item 1A not found in {html_file.name}")


def extract_all():
    """Process every company folder under sec-edgar-filings."""
    base_path = Path(FILINGS_DIR)
    if not base_path.exists():
        print(f"Directory not found: {base_path}")
        return

    for company_path in sorted(base_path.iterdir()):
        if company_path.is_dir():
            print(f"Processing {company_path.name}...")
            extract_company(company_path)

    print("Risk factor extraction complete.")


if __name__ == "__main__":
    extract_all()
