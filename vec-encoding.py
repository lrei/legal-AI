import sqlite3
import warnings
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer, util
import numpy as np

# BUG: every section is saved 3 times, each time 500 indices apart. Fix this.


# Database connection
conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()
c.execute('SELECT id, chapter, article, summary, text FROM blocks')
rows = c.fetchall()

warnings.filterwarnings('ignore', category=Warning)

es = Elasticsearch(
    hosts=["http://localhost:9200"],
    verify_certs=False  # Disable certificate verification (for development only)
)
index_name = 'documents'
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
es.indices.create(index=index_name)

# Initialize SentenceTransformer model
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# Index documents in Elasticsearch
actions = []
for row in rows:
    doc = {
        '_index': index_name,
        '_id': row[0],
        '_source': {
            'chapter': row[1],
            'article': row[2],
            'summary': row[3],
            'text': row[4]
        }
    }
    actions.append(doc)
helpers.bulk(es, actions)

print("Fetch and normalize corpus embeddings")
corpus = [row[4] for row in rows]
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)



corpus_embeddings = util.normalize_embeddings(corpus_embeddings)
print("Corpus embeddings normalized")

def search_and_rerank(query, top_k=64, rerank_k=32):
    print("search_and_rerank()")
    query_embedding = model.encode(query, convert_to_tensor=True)

     # Ensure the query_embedding is a 2D tensor
    if query_embedding.dim() == 1:
        query_embedding = query_embedding.unsqueeze(0)

    query_embedding = util.normalize_embeddings(query_embedding)

    print("Initial search with Elasticsearch")
    search_results = es.search(
        index=index_name,
        body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['chapter', 'article', 'summary', 'text']
                }
            },
            'size': top_k
        }
    )

    print("Extract document IDs and fetch embeddings for the top_k results")
    top_k_docs = [hit['_id'] for hit in search_results['hits']['hits']]
    top_k_embeddings = np.array([corpus_embeddings[int(doc_id)] for doc_id in top_k_docs])

    print("Re-rank using semantic search")
    hits = util.semantic_search(query_embedding, top_k_embeddings, top_k=rerank_k, score_function=util.dot_score)
    
    print("Retrieve and return re-ranked documents")
    reranked_docs = [rows[int(top_k_docs[hit['corpus_id']])] for hit in hits[0]]
    return reranked_docs

# Example usage
query = "Personal use of AI"
results = search_and_rerank(query)
print("Number of results: ", len(results))
for result in results:
    print(result)
    print("\n")
