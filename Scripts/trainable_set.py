import pandas as pd
import matplotlib.pyplot as plt

# Load CSV files
companies_df = pd.read_csv('companies.csv')
dataset_df = pd.read_csv('dataset.csv')

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

print(df.head())