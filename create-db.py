import sqlite3
import json

# Step 1: Read the JSON file
with open('data/ai_article_data.json', 'r', encoding='utf-8') as f:
    blocks = json.load(f)

# Step 2: Connect to SQLite database (create new if not exists)
conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()

# Step 3: Create a table to store text blocks (if not exists)
c.execute('''
CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY,
    chapter TEXT,
    article TEXT,
    date TEXT,
    summary TEXT,
    paragraph TEXT,
    text TEXT
)
''')

# Step 4: Insert data into the table
for block in blocks:
    chapter = block['Chapter']
    article = block['Article']
    date = block['Expected date']
    summary = block['Summary']
    paragraph = block['Paragraph']
    text = block['Text']
    c.execute('INSERT INTO blocks (chapter, article, date, summary, paragraph, text) VALUES (?, ?, ?, ?, ?, ?)', (chapter, article, date, summary, paragraph, text))

# Commit changes and close connection
conn.commit()
conn.close()

print("Data inserted into SQLite database successfully.")

# ----------------- Example of retrieval ---------------------------
conn = sqlite3.connect('data/blocks.db')
c = conn.cursor()

paragraph = 2  # Example paragraph to retrieve
c.execute('SELECT * FROM blocks WHERE paragraph = ?', (paragraph,))
rows = c.fetchall()

print(f"Text blocks with position {paragraph}:")

row = rows[0]
text = row[2]
print(f"ID: {row[0]},  {row[1]}, {row[2]}, paragraph, {row[5]}, Text: {row[6]}")

conn.close()
