import pandas as pd
import matplotlib.pyplot as plt
import re
import os
from pathlib import Path

# Load AI keywords
script_dir = os.path.dirname(os.path.abspath(__file__))
keywords_df = pd.read_csv(os.path.join(script_dir, '..', 'AI_keywords.csv'))
ai_keywords = keywords_df['keyword'].tolist()

def extract_ai_passages(text, keywords):
    """
    Extract sentences containing AI keywords from text.
    Splits text by '. ' (period + space) to identify sentences.
    
    Args:
        text (str): The full text to search
        keywords (list): List of AI keywords to search for
        
    Returns:
        list: List of sentences containing AI keywords
    """
    if not text or pd.isna(text):
        return []
    
    # Split by period + space to get sentences
    sentences = text.split('. ')
    
    # Find sentences containing any keyword (case-insensitive)
    ai_passages = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for keyword in keywords:
            if keyword.lower() in sentence_lower:
                ai_passages.append(sentence.strip())
                break  # Only add sentence once even if multiple keywords match
    
    return ai_passages

def get_filing_path(company_name, year): # we need to get the filings and then extract the risk factor section
    # then apply the function above to extract the AI related passage

    # Map company names to directory names
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
    
    # Get last two digits of year
    year_suffix = str(year)[-2:]
    
    # Construct file path (use absolute path from script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filing_path = os.path.join(script_dir, '..', 'sec-edgar-filings', dir_name, 'RiskFactors', f'{dir_name}_risk_factors_{year_suffix}.txt')
    
    # Check if file exists
    if os.path.exists(filing_path):
        return filing_path
    
    return None

# Load CSV files
companies_df = pd.read_csv(os.path.join(script_dir, '..', 'companies.csv'))
dataset_df = pd.read_csv(os.path.join(script_dir, '..', 'dataset.csv'))

# Merge the dataframes on company name
merged_df = pd.merge(
    dataset_df,
    companies_df,
    left_on='Company',
    right_on='company',
    how='left'
)

# Create the final dataframe with required columns
df = pd.DataFrame({
    'Company': merged_df['Company'],
    'Ticker': merged_df['ticker'],
    'Sector': merged_df['Sector'],
    'Filing_Year': merged_df['Year'],
    'Paragraph_id': None,
    'Passage': None,
    'AI_keywords': None
})

# Iterate through each row and extract AI passages
passages_list = []
keywords_list = []
paragraph_ids = []

for idx, row in df.iterrows():
    company = row['Company']
    year = row['Filing_Year']
    
    # Get filing path
    filing_path = get_filing_path(company, year)
    
    if filing_path:
        # Read filing text
        with open(filing_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Extract AI passages
        passages = extract_ai_passages(text, ai_keywords)
        
        # Extract keywords found in each passage
        found_keywords = []
        for passage in passages:
            passage_keywords = []
            passage_lower = passage.lower()
            for keyword in ai_keywords:
                if keyword.lower() in passage_lower:
                    passage_keywords.append(keyword)
            found_keywords.append(', '.join(passage_keywords))
        
        # Assign paragraph IDs
        para_ids = list(range(len(passages)))
        
        passages_list.append(passages)
        keywords_list.append(found_keywords)
        paragraph_ids.append(para_ids)
    else:
        passages_list.append([])
        keywords_list.append([])
        paragraph_ids.append([])

# Expand the dataframe to have one row per passage
expanded_data = []
for idx, row in df.iterrows():
    passages = passages_list[idx]
    keywords = keywords_list[idx]
    para_ids = paragraph_ids[idx]
    
    if passages:
        for i, passage in enumerate(passages):
            expanded_data.append({
                'Company': row['Company'],
                'Ticker': row['Ticker'],
                'Sector': row['Sector'],
                'Filing_Year': row['Filing_Year'],
                'Paragraph_id': para_ids[i],
                'Passage': passage,
                'AI_keywords': keywords[i]
            })
    else:
        # Add empty row if no passages found
        expanded_data.append({
            'Company': row['Company'],
            'Ticker': row['Ticker'],
            'Sector': row['Sector'],
            'Filing_Year': row['Filing_Year'],
            'Paragraph_id': None,
            'Passage': None,
            'AI_keywords': None
        })

# Create final expanded dataframe
df = pd.DataFrame(expanded_data)

print(df.head())
print(f"\nTotal rows: {len(df)}")

# ===== TEST SECTION - Test single filing before running full script =====
print("\n" + "="*60)
print("TEST: Single filing extraction (Microsoft 2024)")
print("="*60)

test_company = 'Microsoft'
test_year = 2024
test_path = get_filing_path(test_company, test_year)

if test_path:
    print(f"Filing path: {test_path}")
    with open(test_path, 'r', encoding='utf-8') as f:
        test_text = f.read()
    
    print(f"Text length: {len(test_text)} characters")
    
    # DEBUG: Test with known AI sentence
    test_sentence = "We are investing in artificial intelligence (\"AI\") across the entire company and infusing generative AI capabilities into our consumer and commercial offerings."
    print(f"\nDEBUG: Test sentence: {test_sentence}")
    print(f"Contains 'AI': {'ai' in test_sentence.lower()}")
    print(f"Contains 'artificial intelligence': {'artificial intelligence' in test_sentence.lower()}")
    
    # DEBUG: Check first few sentences
    print(f"\nDEBUG: First 5 sentences from split('. '):")
    sentences = test_text.split('. ')
    for i, sent in enumerate(sentences[:5]):
        print(f"{i+1}: {sent[:100]}...")
    
    test_passages = extract_ai_passages(test_text, ai_keywords)
    print(f"\nNumber of AI passages found: {len(test_passages)}")
    
    if test_passages:
        print("\nFirst 3 passages:")
        for i, passage in enumerate(test_passages[:3]):
            print(f"\n--- Passage {i+1} ---")
            print(passage[:200] + "..." if len(passage) > 200 else passage)
            
            # Show keywords found
            passage_lower = passage.lower()
            found = [k for k in ai_keywords if k.lower() in passage_lower]
            print(f"Keywords: {', '.join(found)}")
else:
    print(f"Filing not found for {test_company} {test_year}")
