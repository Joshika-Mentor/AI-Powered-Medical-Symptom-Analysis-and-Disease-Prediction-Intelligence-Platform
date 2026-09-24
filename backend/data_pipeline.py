import pandas as pd
import json
import os
import re

def clean_data():
    raw_file_path = '../data/raw/train_disease.csv' 
    clean_file_path = '../data/processed/cleaned_symptoms.csv'
    schema_file_path = '../data/processed/symptoms_schema.json'

    os.makedirs('../data/processed', exist_ok=True)

    print("Loading raw dataset...")
    try:
        df = pd.read_csv(raw_file_path)
    except FileNotFoundError:
        print(f"ERROR: Cannot find {raw_file_path}. Ensure it is one folder up in data/raw/")
        return

    def sanitize(text):
        text = text.strip().lower()
        return re.sub(r'[\s_]+', '_', text).strip('_')

    df.columns = [sanitize(col) for col in df.columns]

    if 'prognosis' not in df.columns:
        print("ERROR: 'prognosis' column not found.")
        return
        
    df['prognosis'] = df['prognosis'].str.strip()

    original_shape = df.shape
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Dropped duplicates. Shape went from {original_shape} to {df.shape}")

    symptoms = [col for col in df.columns if col != 'prognosis']
    
    with open(schema_file_path, 'w') as f:
        json.dump(sorted(symptoms), f)
    print(f"Exported {len(symptoms)} symptoms to {schema_file_path}")

    df.to_csv(clean_file_path, index=False)
    print(f"Clean dataset saved to {clean_file_path}")

if __name__ == "__main__":
    clean_data()