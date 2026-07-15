import os
import json
import re
from pathlib import Path
from collections import defaultdict

def count_ai_mentions(text):
    """
    Count the number of times AI is mentioned in the text.
    Look for various AI-related terms and patterns.
    """
    if not text:
        return 0
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # AI-related terms and patterns
    ai_patterns = [
        r'\bai\b',  # standalone "ai"
        r'\bartificial intelligence\b',
        r'\bmachine learning\b',
        r'\bml\b',  # standalone "ml" (machine learning)
        r'\bdeep learning\b',
        r'\bneural network\b',
        r'\bgenerative ai\b',
        r'\bgpt\b',
        r'\bchatgpt\b',
        r'\bllm\b',  # large language model
        r'\blarge language model\b',
        r'\bai-powered\b',
        r'\bai-driven\b',
        r'\bai-enabled\b'
    ]
    
    total_mentions = 0
    
    for pattern in ai_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            total_mentions += len(matches)
    
    return total_mentions

def count_words(text):
    """
    Count the number of words in the text.
    """
    if not text:
        return 0
    
    # Remove extra whitespace and split by whitespace
    words = text.strip().split()
    return len(words)

def get_risk_factors_content(company_name, year):
    """
    Get the content of the risk factors file for a specific company and year.
    """
    risk_factors_file = Path(f"sec-edgar-filings/{company_name}/RiskFactors/{company_name}_risk_factors_{year}.txt")
    
    if not risk_factors_file.exists():
        return None
    
    try:
        with open(risk_factors_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"  Error reading risk factors for {company_name} {year}: {e}")
        return None

def update_metadata_file(metadata_file_path, company_name, year):
    """
    Update a single metadata file with AI analysis data.
    """
    try:
        # Read existing metadata
        with open(metadata_file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Get risk factors content
        risk_factors_content = get_risk_factors_content(company_name, year)
        
        if risk_factors_content is None:
            print(f"  No risk factors file found for {company_name} {year}")
            return False
        
        # Calculate AI analysis
        ai_mentions = count_ai_mentions(risk_factors_content)
        word_count = count_words(risk_factors_content)
        
        # Add new fields to metadata
        metadata['ai_mentions'] = ai_mentions
        metadata['words_in_1a'] = word_count
        metadata['ai_analysis_date'] = '2026-07-14'
        
        # Save updated metadata
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
        
        print(f"  Updated {metadata_file_path.name}: {ai_mentions} AI mentions, {word_count} words")
        return True
        
    except Exception as e:
        print(f"  Error updating {metadata_file_path}: {e}")
        return False

def calculate_ai_increases():
    """
    Calculate year-over-year AI mentions increases and update metadata files.
    """
    base_dir = Path("sec-edgar-filings")
    
    # Collect all metadata data by company
    company_data = defaultdict(dict)
    
    # First pass: collect all AI mentions data
    for company_path in sorted(base_dir.iterdir()):
        if not company_path.is_dir():
            continue
        
        company_name = company_path.name
        metadata_path = company_path / "Metadata"
        
        if not metadata_path.exists():
            continue
        
        for metadata_file in sorted(metadata_path.glob("*-metadata.json")):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                if 'ai_mentions' in metadata and 'filingYear' in metadata:
                    year = metadata['filingYear']
                    ai_mentions = metadata['ai_mentions']
                    company_data[company_name][year] = {
                        'ai_mentions': ai_mentions,
                        'file_path': metadata_file
                    }
                    
            except Exception as e:
                print(f"  Error reading {metadata_file}: {e}")
    
    # Second pass: calculate increases and update files
    for company_name, years_data in company_data.items():
        sorted_years = sorted(years_data.keys())
        
        for i, year in enumerate(sorted_years):
            if i == 0:
                # First year has no previous year to compare to
                increase = 0
            else:
                prev_year = sorted_years[i-1]
                current_mentions = years_data[year]['ai_mentions']
                prev_mentions = years_data[prev_year]['ai_mentions']
                increase = current_mentions - prev_mentions
            
            # Update the metadata file with the increase
            metadata_file = years_data[year]['file_path']
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata['ai_mentions_increase'] = increase
                
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=4)
                
                print(f"  Added AI increase for {company_name} {year}: {increase}")
                
            except Exception as e:
                print(f"  Error updating AI increase for {company_name} {year}: {e}")

def update_all_metadata():
    """
    Update all metadata files with AI analysis data.
    """
    base_dir = Path("sec-edgar-filings")
    
    if not base_dir.exists():
        print(f"Directory {base_dir} not found")
        return
    
    print("Adding AI analysis to existing metadata files...")
    
    updated_count = 0
    
    # Process each company
    for company_path in sorted(base_dir.iterdir()):
        if not company_path.is_dir():
            continue
        
        company_name = company_path.name
        metadata_path = company_path / "Metadata"
        
        if not metadata_path.exists():
            print(f"  No Metadata folder for {company_name}")
            continue
        
        print(f"\nProcessing {company_name}...")
        
        # Process each metadata file
        for metadata_file in sorted(metadata_path.glob("*-metadata.json")):
            # Extract year from filename
            match = re.search(r'-(\d{4})-metadata\.json', metadata_file.name)
            if match:
                year = match.group(1)
                year_2digit = year[2:]  # Convert 2022 -> 22
                
                if update_metadata_file(metadata_file, company_name, year_2digit):
                    updated_count += 1
    
    print(f"\nUpdated {updated_count} metadata files with AI analysis")
    
    # Calculate year-over-year increases
    print("\nCalculating AI mentions increases...")
    calculate_ai_increases()
    
    print("\nAI analysis complete!")

def generate_summary_report():
    """
    Generate a summary report of AI mentions across all companies.
    """
    base_dir = Path("sec-edgar-filings")
    summary = {
        'total_companies': 0,
        'companies': {},
        'yearly_totals': defaultdict(lambda: {'total_ai_mentions': 0, 'total_companies': 0}),
        'analysis_date': '2026-07-14'
    }
    
    for company_path in sorted(base_dir.iterdir()):
        if not company_path.is_dir():
            continue
        
        company_name = company_path.name
        metadata_path = company_path / "Metadata"
        
        if not metadata_path.exists():
            continue
        
        company_data = {}
        has_data = False
        
        # Check for metadata files
        for metadata_file in sorted(metadata_path.glob("*-metadata.json")):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                if 'ai_mentions' in metadata and 'filingYear' in metadata:
                    year = metadata['filingYear']
                    company_data[str(year)] = {
                        'ai_mentions': metadata['ai_mentions'],
                        'ai_mentions_increase': metadata.get('ai_mentions_increase', 0),
                        'words_in_1a': metadata['words_in_1a']
                    }
                    
                    # Add to yearly totals
                    summary['yearly_totals'][str(year)]['total_ai_mentions'] += metadata['ai_mentions']
                    summary['yearly_totals'][str(year)]['total_companies'] += 1
                    has_data = True
                    
            except Exception as e:
                print(f"Error reading {metadata_file}: {e}")
        
        if has_data:
            summary['companies'][company_name] = company_data
            summary['total_companies'] += 1
    
    # Save summary report
    with open('ai_mentions_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary report saved to ai_mentions_summary.json")
    print(f"Analyzed {summary['total_companies']} companies")
    
    # Print brief summary
    for year in sorted(summary['yearly_totals'].keys()):
        totals = summary['yearly_totals'][year]
        avg_mentions = totals['total_ai_mentions'] / totals['total_companies'] if totals['total_companies'] > 0 else 0
        print(f"Year {year}: {totals['total_ai_mentions']} total AI mentions across {totals['total_companies']} companies (avg: {avg_mentions:.1f})")

if __name__ == "__main__":
    update_all_metadata()
    generate_summary_report()
