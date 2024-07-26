# The document is not relevant anymore, since we switched to a different approach for retrieval (elastic search)
# See vec-encoding.py

import sqlite3
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()

model = SentenceTransformer('all-MiniLM-L6-v2')

index = faiss.read_index('data/vector_index.faiss')

def search_similar_text(query_text, top_k=5):
    query_vector = model.encode([query_text])[0]

    D, I = index.search(np.array([query_vector]), top_k)
    similar_texts = []
    for i in range(top_k):
        text_id = int(I[0][i])
        c.execute('SELECT text FROM blocks WHERE id = ?', (text_id,))
        row = c.fetchone()

        if row:
            similar_texts.append(row[0])
        else:
            print(f"No text found for id: {text_id}")

    return similar_texts
# Write any query -----------------------------------
query = "Bussiness"
#-----------------------------------

results = search_similar_text(query, top_k=3)
print(f"Query: {query}")
print("Top 3 Similar Texts:")
for i, result in enumerate(results, 1):
    print(f"{i}. {result}")

conn.close()
