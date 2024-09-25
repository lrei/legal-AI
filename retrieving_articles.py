import sqlite3
import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch
import lancedb
import os
import sys
from sentence_transformers import CrossEncoder

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def normalize_embedding(embedding):
    return embedding / np.linalg.norm(embedding)

def generate_bge_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).numpy().flatten()
    return normalize_embedding(embedding)


# Cross indexing from .db files and LanceDB files
def get_metadata_from_db(cursor, id_value):
    cursor.execute("SELECT regulation, chapter, article, passage, content FROM embeddings WHERE id = ?", (id_value,))
    return cursor.fetchone()

# Getting rid of the overlapping passages to form a coherent article
def get_full_article(cursor, regulation, article):
    cursor.execute("""
        SELECT passage, content 
        FROM embeddings 
        WHERE regulation = ? AND article = ?
        ORDER BY 
            CAST(SUBSTR(passage, INSTR(passage, '.') + 1, INSTR(SUBSTR(passage, INSTR(passage, '.') + 1), '.') - 1) AS INTEGER),
            CAST(SUBSTR(passage, INSTR(SUBSTR(passage, INSTR(passage, '.') + 1), '.') + 1, LENGTH(passage)) AS INTEGER)
    """, (regulation, article))
    rows = cursor.fetchall()
    return rows  

def search_legislation_lance(query_text, query_embedding, table, cursor, reranker, k=10, initial_limit=30, increment=30):
    query_embedding = normalize_embedding(query_embedding.tolist())
    candidate_passages = []
    passage_metadata = []
    limit = initial_limit
    results = table.search(query_embedding).limit(limit).to_pandas()

    for index, row in results.iterrows():
        metadata = get_metadata_from_db(cursor, row['id'])
        if metadata:
            regulation, chapter, article, passage, content = metadata
            
            # Omit the articles titled "Definitions" because they provide no insight into the legal matter 
            if "definitions" in article.lower():
                continue
            
            candidate_passages.append(content)
            passage_metadata.append({
                'regulation': regulation,
                'chapter': chapter,
                'article': article,
                'passage': passage,
                'content': content
            })

    # Prepare inputs for the re-ranker
    reranker_inputs = [[query_text, passage] for passage in candidate_passages]

    # Compute relevance scores using the CrossEncoder re-ranker
    relevance_scores = reranker.predict(reranker_inputs)

    scored_passages = list(zip(candidate_passages, relevance_scores, passage_metadata))

    scored_passages.sort(key=lambda x: x[1], reverse=True)

    # Select the top K passages
    top_k_passages = scored_passages[:k]

    article_results = {}
    for content, score, metadata in top_k_passages:
        regulation = metadata['regulation']
        chapter = metadata['chapter']
        article = metadata['article']

        article_key = (regulation, article)
        if article_key not in article_results:
            full_article = get_full_article(cursor, regulation, article)
            article_results[article_key] = (chapter, full_article)

    return article_results

def combine_passages_with_overlap_removal(full_article_content, overlap_length=30):
    combined_article = ""
    previous_passage_number = None
    previous_chunk = ""

    for passage, content in full_article_content:
        passage_number = passage.split(".")[:3]
        passage_str = ".".join(passage_number)

        if previous_passage_number and previous_passage_number != passage_number:
            combined_article += "\n"

        if previous_chunk:
            overlap_start = min(overlap_length, len(previous_chunk))
            while overlap_start > 0 and previous_chunk[-overlap_start:] != content[:overlap_start]:
                overlap_start -= 1
            content = content[overlap_start:].strip()

        combined_article += content + " "

        previous_chunk = content
        previous_passage_number = passage_number

    return combined_article.strip()

def main():
    if len(sys.argv) < 2:
        print("No query text provided.")
        sys.exit(1)
    else:
        query_text = sys.argv[1]
        try:
            k = int(sys.argv[2]) if len(sys.argv) > 2 else 3  
        except ValueError:
            k = 3

    ldb = lancedb.connect('lancedb_files/Merged')
    table = ldb.open_table('embeddings')  # LanceDB table

    conn = sqlite3.connect('data/Merged/merged.db') # SQL database
    cursor = conn.cursor()

    # Load the BGE embedding model
    model_name = "BAAI/bge-small-en"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Load the Cross-Encoder re-ranking model
    reranker_model_name = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    reranker = CrossEncoder(reranker_model_name)

    # Generate query embedding
    query_embedding = generate_bge_embedding(query_text, tokenizer, model)

    # Search for relevant articles with re-ranking
    results = search_legislation_lance(query_text, query_embedding, table, cursor, reranker, k=k)

    if results:
        for (regulation, article), (chapter, full_article_content) in results.items():
            combined_content = combine_passages_with_overlap_removal(full_article_content)
            output = f"Regulation: {regulation}\n{chapter}\n{article}\n{combined_content}\n"
            print(output)
    else:
        print(f"No relevant articles found.")

    conn.close()

if __name__ == "__main__":
    main()
