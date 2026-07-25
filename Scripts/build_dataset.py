import json
import csv
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

if __name__ == "__main__":
    build_master_dataset()
