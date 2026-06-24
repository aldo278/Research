import csv
import re
import shutil
import sys
from pathlib import Path
from sec_edgar_downloader import Downloader

FILINGS_DIR = "sec-edgar-filings"


def sanitize_folder_name(name):
    """Remove spaces and special characters to create a valid folder name."""
    return re.sub(r"[^a-zA-Z0-9]", "", name)


def load_company_info(ticker):
    """Return the company row matching the given ticker, or None if not found."""
    with open("companies.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["ticker"].upper() == ticker.upper():
                return row
    return None


def download_and_format_single_company(ticker):
    """Download and organize 10-K filings for a single company by ticker."""
    row = load_company_info(ticker)
    if row is None:
        print(f"Error: Ticker '{ticker}' is not valid and cannot be found in companies.csv")
        return False

    company = row["company"]
    industry = row["industry"]

    print(f"Downloading 10-K filings for {company} ({ticker}) - {industry}")
    dl = Downloader("sec_data", "antanolopez@linfield.edu")
    try:
        dl.get(
            "10-K",
            ticker,
            after="2022-01-01",
            before="2025-01-01"
        )
    except Exception as e:
        print(f"Error downloading filings for {ticker}: {e}")
        return False

    # Verify the downloader actually created a folder
    base_path = Path(FILINGS_DIR)
    old_folder = base_path / ticker
    if not old_folder.exists():
        print(f"Error: Download completed but no folder was created for {ticker}. "
              f"The ticker/CIK may be invalid or have no filings in the date range.")
        return False

    print(f"Successfully downloaded filings for {ticker}")

    # Organize: rename ticker folder to sanitized company name
    new_folder = base_path / sanitize_folder_name(company)

    if not old_folder.exists():
        print(f"Error: Download folder for {ticker} not found")
        return False

    # On case-insensitive filesystems, UBER and Uber are the same folder
    if str(old_folder.resolve()).lower() == str(new_folder.resolve()).lower():
        print(f"Folder for {ticker} already matches company name {new_folder.name}")
        return True

    if new_folder.exists():
        # Merge contents into the existing company folder
        for item in old_folder.iterdir():
            target = new_folder / item.name
            if target.exists():
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
        shutil.rmtree(old_folder)
        print(f"Merged {ticker} into {new_folder.name}")
    else:
        shutil.move(str(old_folder), str(new_folder))
        print(f"Renamed {ticker} -> {new_folder.name}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python singleDownload.py <TICKER>")
        sys.exit(1)

    ticker = sys.argv[1]
    success = download_and_format_single_company(ticker)
    sys.exit(0 if success else 1)
