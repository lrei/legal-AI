import sqlite3
import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
import torch

# Load the model and tokenizer
model_name = 'nlpaueb/legal-bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Connect to the database
conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()

c.execute('SELECT id, chapter, article, date, summary, paragraph, text FROM blocks')
records = c.fetchall()

conn.close()

vectors = []
for record in records:
    concatenated_text = ' | '.join(record[1:])  # brez id
    inputs = tokenizer(concatenated_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        vectors.append(embeddings.squeeze().numpy())

# Convert list of numpy arrays to a single numpy array
vectors_np = np.vstack(vectors)

# Create a FAISS index and add the vectors
index = faiss.IndexFlatL2(vectors_np.shape[1])
index.add(vectors_np)

# Save the index
faiss.write_index(index, 'data/vector_index.faiss')
print('Index saved to data/vector_index.faiss')

# Load the FAISS index
index = faiss.read_index('data/vector_index.faiss')

# Prepare the query
query_text = "Businesses must comply with the GDPR"
inputs = tokenizer(query_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
with torch.no_grad():
    outputs = model(**inputs)
    query_vector = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

# Search the index
k = 5  # Number of nearest neighbors to find
D, I = index.search(np.array([query_vector]), k)  # D: distances, I: indices

# Process the results
print("Indices of the most similar vectors:", I)
print("Distances:", D)
number_of_vectors = len(records)
print("number_of_vectors:", number_of_vectors)