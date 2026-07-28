import pandas as pd
import matplotlib.pyplot as plt
import re
import os
from pathlib import Path

# Load AI keywords
script_dir = os.path.dirname(os.path.abspath(__file__))
keywords_df = pd.read_csv(os.path.join(script_dir, '..', 'AI_keywords.csv'))
ai_keywords = keywords_df['keyword'].tolist()


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


# Function to extract AI passages from a single filing
def extract_passages_from_file(file_path, keywords):
    """Extract AI passages from a single filing file."""
    pattern_pieces = [rf"\b{re.escape(word)}\b" for word in keywords]
    ai_regex = re.compile("|".join(pattern_pieces), re.IGNORECASE)
    sentence_end_regex = re.compile(r'(?<!\bU\.S)(?<!\bInc)(?<!\bCo)(?<!\bvs)\.\s+(?=[A-Z""])')

    with open(file_path, 'r', encoding="utf-8") as file:
        full_text = file.read().replace('\n', ' ')
        full_text = re.sub(r'\s+', ' ', full_text)
    
    sentences = sentence_end_regex.split(full_text)
    extracted_passages = []
    
    for sentence in sentences:
        clean_sentence = sentence.strip()
        if clean_sentence and not clean_sentence.endswith('.'):
            clean_sentence += '.'

        if ai_regex.search(clean_sentence):
            extracted_passages.append(clean_sentence)
   
    return extracted_passages

# Function to get keywords found in a passage
def get_keywords_in_passage(passage, keywords):
    """Return list of keywords found in the passage."""
    passage_lower = passage.lower()
    found = []
    for keyword in keywords:
        if keyword.lower() in passage_lower:
            found.append(keyword)
    return ', '.join(found)

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
        # Extract AI passages
        passages = extract_passages_from_file(filing_path, ai_keywords)
        
        # Extract keywords found in each passage
        found_keywords = []
        for passage in passages:
            found_keywords.append(get_keywords_in_passage(passage, ai_keywords))
        
        # Assign paragraph IDs (starting at 1)
        para_ids = list(range(1, len(passages) + 1))
        
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

# Convert Paragraph_id to nullable integer (Int64 handles None values)
df['Paragraph_id'] = pd.to_numeric(df['Paragraph_id'], errors='coerce').astype('Int64')

print(df.head())





