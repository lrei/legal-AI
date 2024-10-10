import sqlite3
import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch
import lancedb
import os
from sentence_transformers import CrossEncoder
from numpy import dot
from numpy.linalg import norm

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def normalize_embedding(embedding):
    return embedding / np.linalg.norm(embedding)

def generate_bge_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).numpy().flatten()
    return normalize_embedding(embedding)

def cosine_similarity(a, b):
    return dot(a, b)/(norm(a)*norm(b))

def get_metadata_from_db(cursor, id_value):
    cursor.execute("SELECT regulation, chapter, article, passage, content FROM embeddings WHERE id = ?", (id_value,))
    return cursor.fetchone()

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

def search_legislation_lance(query_text, query_embedding, table, cursor, reranker, k=10, initial_limit=30, cosine_similarity_threshold=0.3):
    query_embedding = normalize_embedding(query_embedding.tolist())
    candidate_passages = []
    passage_metadata = []
    limit = initial_limit

    # Retrieve search results from LanceDB and ensure embeddings are included
    results = table.search(query_embedding).limit(limit).to_pandas()
    
    if 'vector' not in results.columns:
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
            
            # Omit articles titled "Definitions" because they do not provide any insight
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
    scored_passages = list(zip(candidate_passages, relevance_scores, passage_metadata))
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
            # Remove overlap between passages
            overlap_start = min(overlap_length, len(previous_chunk))
            while overlap_start > 0 and previous_chunk[-overlap_start:] != content[:overlap_start]:
                overlap_start -= 1
            content = content[overlap_start:].strip()

        combined_article += content + " "

        previous_chunk = content
        previous_passage_number = passage_number

    return combined_article.strip()

def retrieve_articles(query_text, k=10, threshold=0.6, sentence_transformer_model="BAAI/bge-small-en", reranker_model='cross-encoder/ms-marco-MiniLM-L-6-v2'):
    # Connect to LanceDB and open the embeddings table
    ldb = lancedb.connect('lancedb_files/Merged')
    table = ldb.open_table('embeddings')

    # Connect to the SQLite database
    conn = sqlite3.connect('data/Merged/merged.db')
    cursor = conn.cursor()

    # Load the BGE embedding model
    tokenizer = AutoTokenizer.from_pretrained(sentence_transformer_model, trust_remote_code=True)
    model = AutoModel.from_pretrained(sentence_transformer_model, trust_remote_code=True)

    # Load the Cross-Encoder re-ranking model
    reranker = CrossEncoder(reranker_model)

    # Generate the query embedding
    query_embedding = generate_bge_embedding(query_text, tokenizer, model)

    # Search for relevant articles with re-ranking and cosine similarity threshold
    results = search_legislation_lance(
        query_text, query_embedding, table, cursor, reranker, k=k, cosine_similarity_threshold=threshold
    )

    conn.close()

    articles = []

    if results:
        for (regulation, article), article_info in results.items():
            chapter = article_info['chapter']
            full_article_content = article_info['full_article']
            combined_content = combine_passages_with_overlap_removal(full_article_content)
            output = (
                f"Regulation: {regulation}\n"
                f"{chapter}\n"
                f"{article}\n"
                f"{combined_content}\n"
            )
            articles.append(output)
    else:
        articles.append("No relevant articles found.")

    return articles
