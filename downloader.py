# Download 10-K filings for all companies in the CSV file

import csv
from sec_edgar_downloader import Downloader

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

