import pandas as pd

def fix_paragraph_ids():
    """
    Fix the paragraph_id column in annotation_dataset_completed.csv.
    - Only assign paragraph IDs to rows with non-empty passages
    - Make paragraph IDs unique and sequential starting from 1
    """
    # Read the CSV file
    df = pd.read_csv('../annotation_dataset_completed.csv')
    
    print(f"Original shape: {df.shape}")
    print(f"Original paragraph_id column:\n{df['Paragraph_id'].head(20)}")
    
    # Reset paragraph_id to None for all rows
    df['Paragraph_id'] = None
    
    # Assign sequential paragraph IDs only to rows with non-empty passages
    current_id = 1
    for idx, row in df.iterrows():
        # Check if passage is not empty (not NaN and not empty string)
        if pd.notna(row['Passage']) and row['Passage'].strip() != '':
            df.at[idx, 'Paragraph_id'] = current_id
            current_id += 1
    
    print(f"\nFixed paragraph_id column:\n{df['Paragraph_id'].head(20)}")
    print(f"\nTotal rows with passages: {df['Paragraph_id'].notna().sum()}")
    print(f"Total rows: {len(df)}")
    
    # Save the updated dataframe
    df.to_csv('../annotation_dataset_completed.csv', index=False)
    print("\nUpdated file saved successfully!")

if __name__ == "__main__":
    fix_paragraph_ids()
