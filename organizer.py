import shutil
from pathlib import Path

FILINGS_DIR = "sec-edgar-filings"


def organize_company_folder(company_path):
    """
    For a single company folder:
      - Create FullText, Filtered, and RiskFactors subfolders
      - Move the contents of the 10-K folder into FullText
      - Delete the empty 10-K folder
    """
    ten_k_path = company_path / "10-K"
    full_text_path = company_path / "FullText"
    filtered_path = company_path / "Filtered"
    risk_factors_path = company_path / "RiskFactors"

    # Create the three subfolders
    full_text_path.mkdir(exist_ok=True)
    filtered_path.mkdir(exist_ok=True)
    risk_factors_path.mkdir(exist_ok=True)

    if not ten_k_path.exists():
        return

    # Move each accession folder from 10-K into FullText
    for item in ten_k_path.iterdir():
        target = full_text_path / item.name
        if target.exists():
            # If the accession folder already exists in FullText, merge contents
            if target.is_dir() and item.is_dir():
                for subitem in item.iterdir():
                    subtarget = target / subitem.name
                    if subtarget.exists():
                        if subtarget.is_dir():
                            shutil.rmtree(subtarget)
                        else:
                            subtarget.unlink()
                    shutil.move(str(subitem), str(subtarget))
                shutil.rmtree(item)
            else:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                shutil.move(str(item), str(target))
        else:
            shutil.move(str(item), str(target))

    # Remove the now-empty 10-K folder
    shutil.rmtree(ten_k_path)


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
