import json
import csv
import pandas as pd
import re
import os
from pathlib import Path

def build_master_dataset():
    """
    Build a master dataset CSV from all metadata files.
    """
    base_dir = Path("sec-edgar-filings")
    
    if not base_dir.exists():
        print(f"Directory {base_dir} not found")
        return
    
    # Define the CSV fields
    fieldnames = ['Company', 'Sector', 'Year', 'Words', 'Ai_mentions']
    
    # Collect all data
    dataset = []
    
    print("Building master dataset from metadata files...")
    
    # Process each company
    for company_path in sorted(base_dir.iterdir()):
        if not company_path.is_dir():
            continue
        
        company_name = company_path.name
        metadata_path = company_path / "Metadata"
        
        if not metadata_path.exists():
            print(f"  No Metadata folder for {company_name}")
            continue
        
        # Process each metadata file
        for metadata_file in sorted(metadata_path.glob("*-metadata.json")):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Extract required fields
                company = metadata.get('companyName', company_name)
                sector = metadata.get('sector', 'Unknown')
                year = metadata.get('filingYear', 'Unknown')
                words = metadata.get('words_in_1a', 0)
                ai_mentions = metadata.get('ai_mentions', 0)
                
                # Add to dataset
                dataset.append({
                    'Company': company,
                    'Sector': sector,
                    'Year': year,
                    'Words': words,
                    'Ai_mentions': ai_mentions
                })
                
                print(f"  Added {company} {year}: {ai_mentions} AI mentions, {words} words")
                
            except Exception as e:
                print(f"  Error reading {metadata_file}: {e}")
    
    # Sort dataset by company and year
    dataset.sort(key=lambda x: (x['Company'], x['Year']))
    
    # Write to CSV
    output_file = 'dataset.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)
    
    print(f"\nMaster dataset created: {output_file}")
    print(f"Total records: {len(dataset)}")
    
    # Print summary by sector
    sector_summary = {}
    for record in dataset:
        sector = record['Sector'] if record['Sector'] else 'Unknown'
        if sector not in sector_summary:
            sector_summary[sector] = {'count': 0, 'total_ai': 0, 'total_words': 0}
        sector_summary[sector]['count'] += 1
        sector_summary[sector]['total_ai'] += record['Ai_mentions']
        sector_summary[sector]['total_words'] += record['Words']
    
    print("\nSummary by sector:")
    for sector, data in sorted(sector_summary.items()):
        avg_ai = data['total_ai'] / data['count'] if data['count'] > 0 else 0
        avg_words = data['total_words'] / data['count'] if data['count'] > 0 else 0
        print(f"  {sector}: {data['count']} records, avg AI: {avg_ai:.1f}, avg words: {avg_words:.0f}")


def get_filing_path(company_name, year):
    """
    Get the path to the filing file for a given company and year.
    """
    company_dir_map = {
        'Abbott Labs': 'AbbottLabs',
        'Airbnb': 'Airbnb',
        'Alphabet': 'Alphabet',
        'Apple': 'Apple',
        'CVS Health': 'CVSHealth',
        'Costco': 'Costco',
        'Deere & Co': 'DeereCo',
        'Delta Air Lines': 'DeltaAirLines',
        'Eli Lilly': 'EliLilly',
        'General Electric': 'GeneralElectric',
        'Goldman Sachs': 'GoldmanSachs',
        'Home Depot': 'HomeDepot',
        'Honeywell': 'Honeywell',
        'JPMorgan': 'JPMorgan',
        'Mastercard': 'Mastercard',
        'Microsoft': 'Microsoft',
        'NVIDIA': 'NVIDIA',
        'Netflix': 'Netflix',
        'NextEra Energy': 'NextEraEnergy',
        'Nike': 'Nike',
        'Occidental': 'Occidental',
        'Schlumberger': 'Schlumberger',
        'UBER': 'UBER',
        'Warner Bros': 'WarnerBros'
    }
    
    dir_name = company_dir_map.get(company_name)
    if not dir_name:
        return None
    
    year_suffix = str(year)[-2:]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filing_path = os.path.join(script_dir, '..', 'sec-edgar-filings', dir_name, 'RiskFactors', f'{dir_name}_risk_factors_{year_suffix}.txt')
    
    if os.path.exists(filing_path):
        return filing_path
    return None

def update_ai_mention_counts():
    """
    Update AI mention counts in dataset.csv by recounting from actual filing files.
    """
    # Load AI keywords
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_df = pd.read_csv(os.path.join(script_dir, '..', 'AI_keywords.csv'))
    ai_keywords = keywords_df['keyword'].tolist()
    
    # Build regex pattern
    pattern_pieces = [rf"\b{re.escape(word)}\b" for word in ai_keywords]
    ai_regex = re.compile("|".join(pattern_pieces), re.IGNORECASE)
    
    # Load dataset
    dataset_df = pd.read_csv(os.path.join(script_dir, '..', 'dataset.csv'))
    
    print("Updating AI mention counts from actual filings...")
    
    # Update each row
    for index, row in dataset_df.iterrows():
        company = row['Company']
        year = row['Year']
        
        filing_path = get_filing_path(company, year)
        
        if filing_path:
            ai_count = 0
            with open(filing_path, 'r', encoding="utf-8") as file:
                full_text = file.read()
                matches = ai_regex.findall(full_text)
                ai_count = len(matches)
            
            dataset_df.at[index, 'Ai_mentions'] = ai_count
            print(f"  {company} {year}: {ai_count} AI mentions")
        else:
            print(f"  {company} {year}: Filing not found")
    
    # Save updated dataset
    output_file = os.path.join(script_dir, '..', 'dataset.csv')
    dataset_df.to_csv(output_file, index=False)
    print(f"\nUpdated dataset saved to: {output_file}")

    



if __name__ == "__main__":
    # Uncomment to rebuild dataset from metadata
    # build_master_dataset()
    
    # Update AI mention counts from actual filings
    update_ai_mention_counts()
