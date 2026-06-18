from sec_edgar_downloader import Downloader
import re
import os
from bs4 import BeautifulSoup

def extract_clean_risk_factors(filing_path):
    """
    Extract clean Item 1A Risk Factors section from SEC filing
    """
    with open(filing_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Find the line with "Our operations and financial results are subject to various risks"
    start_line = None
    for i, line in enumerate(lines):
        if "Our operations and financial results are subject to various risks" in line:
            start_line = i
            break
    
    if start_line is None:
        print("Risk Factors section start not found")
        return None
    
    # Find the line with "Item 1B, 2, 3, 4" which marks the end
    end_line = None
    for i in range(start_line, len(lines)):
        if "Item 1B, 2, 3, 4" in lines[i]:
            end_line = i
            break
    
    if end_line is None:
        print("Risk Factors section end not found")
        return None
    
    # Extract the section
    risk_factors_html = ''.join(lines[start_line:end_line])
    
    # Parse HTML and extract clean text
    soup = BeautifulSoup(risk_factors_html, 'html.parser')
    
    # Remove all HTML tags but keep text content
    text = soup.get_text()
    
    # Clean up whitespace and format nicely
    lines = (line.strip() for line in text.splitlines())
    # Remove empty lines and join with proper spacing
    clean_lines = []
    for line in lines:
        if line and not line.isdigit():  # Skip page numbers
            clean_lines.append(line)
    
    return '\n\n'.join(clean_lines)

def download_and_extract_risk_factors():
    """
    Download Microsoft 10-K and extract clean Risk Factors section
    """
    # Download the filing
    dl = Downloader("sec_data", "aantanolopez@linfield.edu")
    
    dl.get(
        "10-K",
        "MSFT",
        after="2022-01-01",
        before="2024-01-01"
    )
    
    # Find the most recent filing
    filing_dir = "sec-edgar-filings/MSFT/10-K"
    if not os.path.exists(filing_dir):
        print("No filings directory found")
        return
    
    # Get all subdirectories (filings)
    filings = [d for d in os.listdir(filing_dir) if os.path.isdir(os.path.join(filing_dir, d))]
    if not filings:
        print("No filings found")
        return
    
    # Use the most recent filing (last in list)
    latest_filing = sorted(filings)[-1]
    filing_path = os.path.join(filing_dir, latest_filing, "full-submission.txt")
    
    if not os.path.exists(filing_path):
        print(f"Filing file not found: {filing_path}")
        return
    
    print(f"Extracting Risk Factors from: {latest_filing}")
    
    # Extract Risk Factors
    risk_factors = extract_clean_risk_factors(filing_path)
    
    if risk_factors:
        # Save clean version
        output_file = "MSFT_Risk_Factors_2023.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(risk_factors)
        
        print(f"Clean Risk Factors saved to: {output_file}")
        print(f"Length: {len(risk_factors)} characters")
        print(f"Lines: {len(risk_factors.splitlines())}")
        
        # Show first few lines
        print("\nFirst 500 characters:")
        print(risk_factors[:500])
        
    else:
        print("Failed to extract Risk Factors")

if __name__ == "__main__":
    download_and_extract_risk_factors()