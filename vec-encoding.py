from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import sqlite3
import faiss
import numpy as np



conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()



model_name = 'nlpaueb/legal-bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name) # lahko kasneje damo tudi kakšnega drugega

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

faiss.write_index(index, 'ijs/data/vector_index.faiss')
print('Index saved to ijs/data/vector_index.faiss')
