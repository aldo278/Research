# Download 10-K filings for all companies in the CSV file 

import csv
import re
import shutil
from pathlib import Path
from sec_edgar_downloader import Downloader

FILINGS_DIR = "sec-edgar-filings"


def sanitize_folder_name(name):
    """Remove spaces and special characters to create a valid folder name."""
    return re.sub(r"[^a-zA-Z0-9]", "", name)


def organize_folders():
    """Rename downloaded folders from ticker symbols to company names."""
    base_path = Path(FILINGS_DIR)
    if not base_path.exists():
        print("No filings directory found to organize.")
        return

    with open("companies.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ticker = row["ticker"]
            company = row["company"]
            old_folder = base_path / ticker
            new_folder = base_path / sanitize_folder_name(company)

            if not old_folder.exists():
                print(f"Folder for {ticker} not found, skipping.")
                continue

            # On Windows (case-insensitive filesystem), UBER and Uber are the same folder.
            # Trying to merge a folder into itself causes file-lock errors, so skip it.
            if str(old_folder.resolve()).lower() == str(new_folder.resolve()).lower():
                print(f"Folder for {ticker} already matches company name {new_folder.name}, skipping.")
                continue

            if new_folder.exists():
                # Merge contents into the existing company folder
                for item in old_folder.iterdir():
                    target = new_folder / item.name
                    if target.exists():
                        if target.is_dir() and item.is_dir():
                            # Move subitems individually to avoid copytree lock issues
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

def download_all_filings():
    # Initialize the downloader
    dl = Downloader("sec_data", "antanolopez@linfield.edu")
    
    # Read companies from CSV file
    with open('companies.csv', 'r') as file:
        reader = csv.DictReader(file)
        
        # Iterate through each company and download their 10-K filings
        for row in reader:
            ticker = row['ticker']
            company = row['company']
            industry = row['industry']
            
            print(f"Downloading 10-K filings for {company} ({ticker}) - {industry}")
            
            try:
                dl.get(
                    "10-K",
                    ticker,
                    after="2022-01-01",
                    before="2025-01-01"
                )
                print(f"Successfully downloaded filings for {ticker}")
            except Exception as e:
                print(f"Error downloading filings for {ticker}: {e}")
            
            print("-" * 50)

if __name__ == "__main__":
    download_all_filings()
    print("\nOrganizing folders...")
    organize_folders()

