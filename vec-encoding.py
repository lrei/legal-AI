from sentence_transformers import SentenceTransformer
import sqlite3
import faiss
import numpy as np

conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()

model = SentenceTransformer('all-MiniLM-L6-v2') # lahko kasneje damo tudi kakšnega drugega

c.execute('SELECT id, text FROM blocks')
rows = c.fetchall()

text_ids = []
texts = []
for row in rows:
    text_ids.append(row[0])
    texts.append(row[1])


vectors = model.encode(texts)

conn.close()

# faiss
index = faiss.IndexFlatL2(vectors.shape[1])  # Assuming L2 distance
index.add(np.array(vectors))

faiss.write_index(index, 'data/vector_index.faiss')
