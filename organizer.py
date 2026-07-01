import re
import shutil
from pathlib import Path

FILINGS_DIR = "sec-edgar-filings"


def extract_year(accession_name):
    """Extract the 2-digit year from an accession folder name like 0001193125-22-052682."""
    match = re.match(r"\d+-(\d{2})-\d+", accession_name)
    if match:
        return match.group(1)
    return None


def flatten_filing(filing_dir, full_text_path):
    """Move full-submission.txt out of an accession folder, rename with year, delete folder."""
    source_file = filing_dir / "full-submission.txt"
    year = extract_year(filing_dir.name)

    if source_file.exists() and year:
        target = full_text_path / f"full-submission-{year}.txt"
        if target.exists():
            target.unlink()
        shutil.move(str(source_file), str(target))
        print(f"  Created full-submission-{year}.txt")

    # Remove the now-redundant accession folder
    shutil.rmtree(filing_dir)


def organize_company_folder(company_path):
    """
    For a single company folder:
      - Create FullText, Filtered, RiskFactors, and Metadata subfolders
      - Move the contents of the 10-K folder into FullText
      - Delete the empty 10-K folder
    """
    ten_k_path = company_path / "10-K"
    full_text_path = company_path / "FullText"
    # filtered_path = company_path / "Filtered"  # No longer needed
    risk_factors_path = company_path / "RiskFactors"
    metadata_path = company_path / "Metadata"

    # Create the four subfolders
    full_text_path.mkdir(exist_ok=True)
    # filtered_path.mkdir(exist_ok=True)  # No longer needed
    risk_factors_path.mkdir(exist_ok=True)
    metadata_path.mkdir(exist_ok=True)

    # Move each accession folder from 10-K directly into FullText
    if ten_k_path.exists():
        for item in ten_k_path.iterdir():
            if item.is_dir():
                flatten_filing(item, full_text_path)
        # Remove the now-empty 10-K folder
        shutil.rmtree(ten_k_path)

    # Flatten any accession subfolders already present in FullText
    for item in list(full_text_path.iterdir()):
        if item.is_dir():
            flatten_filing(item, full_text_path)


def organize_all():
    """Organize every company folder under sec-edgar-filings."""
    base_path = Path(FILINGS_DIR)
    if not base_path.exists():
        print(f"Directory not found: {base_path}")
        return

    for company_path in sorted(base_path.iterdir()):
        if company_path.is_dir():
            print(f"Organizing {company_path.name}...")
            organize_company_folder(company_path)

    print("Organization complete.")


if __name__ == "__main__":
    organize_all()
