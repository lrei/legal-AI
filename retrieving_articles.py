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

# Function to retrieve metadata from the SQLite database
def get_metadata_from_db(cursor, id_value):
    cursor.execute("SELECT regulation, chapter, article, passage, content FROM embeddings WHERE id = ?", (id_value,))
    return cursor.fetchone()

# Function to retrieve the full article, assembling all its passages
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

from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b)/(norm(a)*norm(b))

def search_legislation_lance(query_text, query_embedding, table, cursor, reranker, k=10, initial_limit=30, cosine_similarity_threshold=0.3):
    query_embedding = normalize_embedding(query_embedding.tolist())
    candidate_passages = []
    passage_metadata = []
    limit = initial_limit

    # Retrieve search results from LanceDB and ensure embeddings are included
    results = table.search(query_embedding).limit(limit).to_pandas()
    
    # Ensure that the 'vector' column is present
    if 'vector' not in results.columns:
        # Fetch the embeddings separately if not included
        ids = results['id'].tolist()
        vectors = table.filter(table['id'].isin(ids)).to_pandas()
        results = results.merge(vectors[['id', 'vector']], on='id')

    # Compute cosine similarity between query embedding and passage embeddings
    results['cosine_similarity'] = results['vector'].apply(lambda x: cosine_similarity(query_embedding, x))

    # Filter out passages below the cosine similarity threshold
    filtered_results = results[results['cosine_similarity'] >= cosine_similarity_threshold]
    if filtered_results.empty:
        return {}

    # Collect candidate passages and their metadata
    for index, row in filtered_results.iterrows():
        id_value = row['id']
        cosine_sim = row['cosine_similarity']
        metadata = get_metadata_from_db(cursor, id_value)
        if metadata:
            regulation, chapter, article, passage, content = metadata
            
            # Omit articles titled "Definitions"
            if "definitions" in article.lower():
                continue
            
            candidate_passages.append(content)
            passage_metadata.append({
                'regulation': regulation,
                'chapter': chapter,
                'article': article,
                'passage': passage,
                'content': content,
                'cosine_similarity': cosine_sim
            })

    if not candidate_passages:
        return {}

    # Prepare inputs for the CrossEncoder re-ranker
    reranker_inputs = [[query_text, passage] for passage in candidate_passages]

    # Compute relevance scores using the CrossEncoder re-ranker
    relevance_scores = reranker.predict(reranker_inputs)

    # Pair passages with their scores and metadata
    scored_passages = list(zip(candidate_passages, relevance_scores, passage_metadata))

    # Sort passages based on relevance scores in descending order
    scored_passages.sort(key=lambda x: x[1], reverse=True)

    # Select the top K passages
    top_k_passages = scored_passages[:k]

    # Compile the results, grouping passages by their articles
    article_results = {}
    for content, score, metadata in top_k_passages:
        regulation = metadata['regulation']
        chapter = metadata['chapter']
        article = metadata['article']
        cosine_sim = metadata['cosine_similarity']

        article_key = (regulation, article)
        if article_key not in article_results:
            full_article = get_full_article(cursor, regulation, article)
            article_results[article_key] = {
                'chapter': chapter,
                'full_article': full_article,
                'cosine_similarity': cosine_sim
            }
        else:
            # Update the cosine similarity if this passage has a higher value
            if cosine_sim > article_results[article_key]['cosine_similarity']:
                article_results[article_key]['cosine_similarity'] = cosine_sim

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
            k = int(sys.argv[2]) if len(sys.argv) > 2 else 10  # Default number of articles
        except ValueError:
            k = 10

        try:
            cosine_similarity_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6  # Threshold
        except ValueError:
            cosine_similarity_threshold = 0.6

    # Connect to LanceDB and open the embeddings table
    ldb = lancedb.connect('lancedb_files/Merged')
    table = ldb.open_table('embeddings')

    # Connect to the SQLite database
    conn = sqlite3.connect('data/Merged/merged.db')
    cursor = conn.cursor()

    # Load the BGE embedding model
    model_name = "BAAI/bge-small-en"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Load the Cross-Encoder re-ranking model
    reranker_model_name = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    reranker = CrossEncoder(reranker_model_name)

    # Generate the query embedding
    query_embedding = generate_bge_embedding(query_text, tokenizer, model)

    # Search for relevant articles with re-ranking and cosine similarity threshold
    results = search_legislation_lance(
        query_text, query_embedding, table, cursor, reranker, k=k, cosine_similarity_threshold=cosine_similarity_threshold
    )

    if results:
        for (regulation, article), article_info in results.items():
            chapter = article_info['chapter']
            full_article_content = article_info['full_article']
            cosine_similarity = article_info['cosine_similarity']
            combined_content = combine_passages_with_overlap_removal(full_article_content)
            output = (
                f"Regulation: {regulation}\n"
                f"{chapter}\n"
                f"{article}\n"
                #f"Cosine Similarity: {cosine_similarity:.4f}\n"
                f"{combined_content}\n"
            )
            print(output)
    else:
        print("No relevant articles found.")

    conn.close()

if __name__ == "__main__":
    main()
