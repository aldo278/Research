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


# attempting to make the function myself because AI cant
def get_AI_passage():
    # for now, I am going to read only one filing, the 2024 microsoft risk factors
    # directory is incredibly long so im going to make it a constant
    DIR = r"z:\Devin\Research\sec-edgar-filings\Microsoft\RiskFactors\Microsoft_risk_factors_24.txt" 
    ai_count = 0

    pattern_pieces = [rf"\b{re.escape(word)}\b" for word in ai_keywords] # using the keywords from the ai_keywords list
    ai_regex = re.compile("|".join(pattern_pieces), re.IGNORECASE) # combining the keywords into a single regex pattern

    # creating the ending of the sentence that contains a keyword
    sentence_end_regex = re.compile(r'(?<!\bU\.S)(?<!\bInc)(?<!\bCo)(?<!\bvs)\.\s+(?=[A-Z"“])')

    with open(DIR, 'r', encoding="utf-8") as file:
        full_text = file.read().replace('\n', ' ')
        full_text = re.sub(r'\s+', ' ', full_text) # multiple spaces to one
    
    sentences = sentence_end_regex.split(full_text)
    extracted_passages = [] # keep track of the passages that contain AI keywords
    
    for sentence in sentences:
        clean_sentence = sentence.strip()
        if clean_sentence and not clean_sentence.endswith('.'):
            clean_sentence += '.'

        if ai_regex.search(clean_sentence):
            extracted_passages.append(clean_sentence)
   
    return extracted_passages

passages = get_AI_passage()

for num, passage in enumerate(passages):
    print(f"\nPassage {num + 1}: {passage}\n")
