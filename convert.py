import shutil
from pathlib import Path

FILINGS_DIR = "sec-edgar-filings"


def convert_company(company_path):
    """Copy each full-submission-YY.txt to full-submission-YY.html in the same FullText folder."""
    full_text_path = company_path / "FullText"

    if not full_text_path.exists():
        print(f"  No FullText folder for {company_path.name}, skipping")
        return

    converted = 0
    for txt_file in sorted(full_text_path.glob("full-submission-*.txt")):
        html_file = txt_file.with_suffix(".html")
        shutil.copyfile(txt_file, html_file)
        print(f"  {txt_file.name} -> {html_file.name}")
        converted += 1

    if converted == 0:
        print(f"  No full-submission txt files found for {company_path.name}")


def convert_all():
    """Create HTML copies of all full-submission txt files across every company."""
    base_path = Path(FILINGS_DIR)
    if not base_path.exists():
        print(f"Directory not found: {base_path}")
        return

    for company_path in sorted(base_path.iterdir()):
        if company_path.is_dir():
            print(f"Converting {company_path.name}...")
            convert_company(company_path)

    print("Conversion complete.")


if __name__ == "__main__":
    convert_all()
