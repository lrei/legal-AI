import sqlite3
import json

# Step 1: Read the JSON file
with open('data/output.json', 'r', encoding='utf-8') as f:
    blocks = json.load(f)

# Step 2: Connect to SQLite database (create new if not exists)
conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()

# Step 3: Create a table to store text blocks (if not exists)
c.execute('''
CREATE TABLE IF NOT EXISTS text_blocks (
    id INTEGER PRIMARY KEY,
    position INTEGER,
    text TEXT
)
''')

# Step 4: Insert data into the table
for block in blocks:
    position = block['position']
    text = block['text']
    c.execute('INSERT INTO text_blocks (position, text) VALUES (?, ?)', (position, text))

# Commit changes and close connection
conn.commit()
conn.close()

print("Data inserted into SQLite database successfully.")

# ----------------- Example of retrieval ---------------------------
conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()

position = 2  # Example position to retrieve
c.execute('SELECT * FROM text_blocks WHERE position = ?', (position,))
rows = c.fetchall()

print(f"Text blocks with position {position}:")

row = rows[0]
text = row[2]
print(f"ID: {row[0]}, Position: {row[1]}, Text: {text}")

conn.close()
