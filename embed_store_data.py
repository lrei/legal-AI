import json
from transformers import AutoTokenizer, AutoModel
import torch
import sqlite3
import numpy as np
import lancedb
import pandas as pd
import os
import shutil  

def embed_paragraph(paragraph, tokenizer, model):
    inputs = tokenizer(paragraph, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].squeeze()
    return embeddings.numpy()

# Relative paths
def get_file_paths(choice):
    if choice == 'dga':
        json_file = 'data/Data_Governance_Act/governance_act.json'
        db_file = 'data/Data_Governance_Act/governance_act.db'
        lancedb_dir = 'lancedb_files/Data_Governance_Act'
    elif choice == 'eaa':
        json_file = 'data/AI_Act/ai_act.json'
        db_file = 'data/AI_Act/ai_act.db'
        lancedb_dir = 'lancedb_files/AI_Act'
    elif choice == 'gdpr':
        json_file = 'data/GDPR/gdpr.json'
        db_file = 'data/GDPR/gdpr.db'
        lancedb_dir = 'lancedb_files/GDPR'
    elif choice == 'da':
        json_file = 'data/Data_Act/data_act.json'
        db_file = 'data/Data_Act/data_act.db'
        lancedb_dir = 'lancedb_files/Data_Act'
    elif choice == 'merged':
        json_file = 'data/Merged/merged.json'
        db_file = 'data/Merged/merged.db'
        lancedb_dir = 'lancedb_files/Merged'
    else:
        return None, None, None
    return json_file, db_file, lancedb_dir


# Merging the 4 JSON files into a bigger one
def merge_json_files():
    json_files = [
        'data/GDPR/gdpr.json',
        'data/AI_Act/ai_act.json',
        'data/Data_Act/data_act.json',
        'data/Data_Governance_Act/governance_act.json'
    ]

    combined_data = []
    total_sections = 0 

    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            combined_data.extend(data)
            total_sections += len(data)  

    os.makedirs('data/Merged', exist_ok=True) 

    with open('data/Merged/merged.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4, ensure_ascii=False)

    print(f"Combined {len(json_files)} JSON files into 'data/Merged/merged.json'")


def process_regulation(choice, tokenizer, model):
    json_file, db_file, lancedb_dir = get_file_paths(choice)
    if json_file is None:
        return

    if os.path.exists(lancedb_dir):
        shutil.rmtree(lancedb_dir)
        print(f"Deleted existing LanceDB directory: {lancedb_dir}")

    with open(json_file, 'r', encoding='utf-8') as f:
        paragraphs_data = json.load(f)


# Creating the SQL database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS embeddings')
    c.execute('''CREATE TABLE IF NOT EXISTS embeddings
                 (id INTEGER PRIMARY KEY, regulation TEXT, chapter TEXT, article TEXT, passage TEXT, content TEXT)''')

    lance_data = []
    total_embeddings = 0

    for i, entry in enumerate(paragraphs_data):
        regulation = entry['Regulation']
        chapter = entry['Chapter']
        article = entry['Article']
        passage = entry['Passage']
        content = entry['Content']

        # Embed the metadata
        embedding = embed_paragraph(content, tokenizer, model)
        embedding = embedding / np.linalg.norm(embedding)

        # Insert into SQLite database (without the embedding)
        c.execute('INSERT INTO embeddings (regulation, chapter, article, passage, content) VALUES (?, ?, ?, ?, ?)',
                  (regulation, chapter, article, passage, content))
        id_value = c.lastrowid

        # Prepare relevant data for LanceDB files (only id and vector!)
        lance_data.append({
            "id": id_value,
            "vector": embedding.tolist()
        })

        total_embeddings += 1

        if i % 100 == 0:
            print(f"[{choice.upper()}] Processed {i} embeddings so far...")

    conn.commit()
    conn.close()

    df = pd.DataFrame(lance_data)

    os.makedirs(lancedb_dir, exist_ok=True) 
    ldb = lancedb.connect(lancedb_dir)
    table_name = "embeddings"

    ldb.create_table(table_name, df, mode='overwrite')

    print(f"[{choice.upper()}] Total embeddings processed: {total_embeddings}")
    print(f"[{choice.upper()}] LanceDB table '{table_name}' created with {total_embeddings} embeddings and saved to {lancedb_dir}.")

def main():
    merge_choice = input("Would you like to merge all JSONs into 'merged.json'? (yes/no): ").lower()
    if merge_choice == 'yes':
        merge_json_files()
    elif merge_choice == 'no':
        pass  
    else:
        exit()

    choice = input("Which regulation would you like to process? (dga/eaa/gdpr/da/merged/all): ").lower()

    tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en")
    model = AutoModel.from_pretrained("BAAI/bge-small-en")

    if choice == 'all':
        regulations = ['dga', 'eaa', 'gdpr', 'da', 'merged']
        for reg in regulations:
            process_regulation(reg, tokenizer, model)
    else:
        process_regulation(choice, tokenizer, model)

if __name__ == "__main__":
    main()
