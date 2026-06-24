import os
import shutil
import csv

def rename_and_restructure():
    """
    Rename ticker folders to company names and move files from 10-K subfolders
    """
    
    # Read company names from CSV
    company_map = {}
    with open('companies.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            company_map[row['ticker']] = row['company']
    
    # Base directory for filings
    base_dir = 'sec-edgar-filings'
    
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} not found")
        return
    
    print("Starting renaming and restructuring...")
    
    # Process each ticker folder
    for ticker in os.listdir(base_dir):
        ticker_path = os.path.join(base_dir, ticker)
        
        # Skip if not a directory
        if not os.path.isdir(ticker_path):
            continue
        
        # Get company name
        if ticker not in company_map:
            print(f"Warning: No company name found for ticker {ticker}")
            continue
        
        company_name = company_map[ticker]
        new_folder_path = os.path.join(base_dir, company_name)
        
        print(f"Processing {ticker} -> {company_name}")
        
        # Check if there's a 10-K subfolder
        ten_k_folder = os.path.join(ticker_path, '10-K')
        
        if os.path.exists(ten_k_folder):
            print(f"Found 10-K folder, moving contents...")
            
            # Move contents from 10-K folder to ticker folder
            for item in os.listdir(ten_k_folder):
                item_path = os.path.join(ten_k_folder, item)
                new_item_path = os.path.join(ticker_path, item)
                
                if os.path.isdir(item_path):
                    shutil.move(item_path, new_item_path)
                else:
                    shutil.move(item_path, new_item_path)
            
            # Remove the now-empty 10-K folder
            os.rmdir(ten_k_folder)
            print(f"Removed 10-K folder for {ticker}")
        
        # Rename ticker folder to company name
        try:
            shutil.move(ticker_path, new_folder_path)
            print(f"Renamed {ticker} to {company_name}")
        except Exception as e:
            print(f"Error renaming {ticker}: {e}")
    
    print("Renaming and restructuring completed!")

if __name__ == "__main__":
    rename_and_restructure()
